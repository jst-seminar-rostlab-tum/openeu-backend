import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from app.core.openai_client import openai

from fastapi_cache.decorator import cache

from app.core.relevant_meetings import fetch_relevant_meetings
from app.core.supabase_client import supabase
from app.core.cohere_client import co
from app.core.vector_search import get_top_k_neighbors
from app.models.meeting import Meeting, MeetingSuggestionResponse, LegislativeMeetingsResponse

logger = logging.getLogger(__name__)

router = APIRouter()


_START = Query(None, description="Start datetime (ISO8601)")
_END = Query(None, description="End datetime (ISO8601)")
_TOPICS = Query(None, description="List of topic names (repeat or comma-separated)")
_SOURCE_TABLES = Query(
    None, alias="source_table", description="Filter by source table(s) (repeat or comma-separated)"
)  # URL param stays singular: ?source_table=…
_COUNTRY = Query(
    None,
    description="Filter by country (e.g., 'Austria', 'European Union')",
)


def to_utc_aware(dt: Optional[datetime]) -> Optional[datetime]:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def parse_query_list(param: Optional[list[str]]) -> Optional[list[str]]:
    if param is None:
        return None
    result = []
    for item in param:
        result.extend([x.strip() for x in item.split(",")])
    return result

@router.get("/meetings", response_model=dict[str, list[Meeting]])
@cache(namespace="meetings", expire=3600)
def get_meetings(
    request: Request,  # new param: provides caller info
    limit: int = Query(800, gt=1),
    start: Optional[datetime] = _START,
    end: Optional[datetime] = _END,
    query: Optional[str] = Query(None, description="Search query using semantic similarity"),
    topics: Optional[list[str]] = _TOPICS,
    country: Optional[list[str]] = _COUNTRY,
    user_id: Optional[str] = Query(None, description="User ID for personalized meeting recommendations"),
    source_tables: Optional[list[str]] = _SOURCE_TABLES,
):
    # ---------- 1)  LOG INCOMING REQUEST ----------
    caller_ip = request.headers.get(
        "X-Forwarded-For",
        request.client.host if request.client else "unknown",
    )

    logger.info(
        "GET /meetings | caller=%s | limit=%s | start=%s | end=%s | "
        "query=%s | topics=%s | country=%s | source_tables=%s",
        caller_ip,
        limit,
        start,
        end,
        query,
        topics,
        country,
        source_tables,
    )
    source_tables = parse_query_list(source_tables)
    topics = parse_query_list(topics)
    country = parse_query_list(country)

    try:
        start = to_utc_aware(start)
        end = to_utc_aware(end)

        # --- SEMANTIC QUERY CASE ---
        # --- source table - normalise multi-value params ----------------------------------
        if source_tables and len(source_tables) == 1 and "," in source_tables[0]:
            source_tables = [t.strip() for t in source_tables[0].split(",") if t.strip()]

        if query:
            # tell the vector search which tables are allowed -- value can be any string
            if user_id:
                resp = supabase.table("v_profiles").select("embedding_input").eq("id", user_id).single().execute()
                if resp.data:
                    query = query + "Profile information: " + str(resp.data)
            allowed_sources: dict[str, str] = {t: "embedding_input" for t in source_tables} if source_tables else {}

            try:
                completion = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that reformulates text for semantic search."
                            "Your task is to generate a meeting summary document based on the user's question. "
                            + "Use a formal tone, and try to vary the phrasing and details based on the query context. "
                            + "Keep the summary within three sentences, with a clear title and a brief description.",
                        },
                        {"role": "user", "content": query},
                    ],
                    temperature=0,
                    max_tokens=128,
                )
                reformulated_query = (completion.choices[0].message.content or query).strip()

            except Exception as e:
                reformulated_query = query
                logger.error(f"An error occurred: {e}")

            neighbors = get_top_k_neighbors(
                query=reformulated_query,
                k=1000,
                sources=["meeting_embeddings"],
                allowed_sources=allowed_sources,
                allowed_topics=topics,
                allowed_countries=country,
                start_date=start if start is not None else None,
                end_date=end if end is not None else None,
            )

            if not neighbors:
                # ---------- 2a)  LOG EMPTY RESPONSE (semantic path, no neighbours) ----------
                logger.info("Response formed – empty list (no neighbours found)")
                return JSONResponse(status_code=200, content={"data": []})

            docs = [n["content_text"] for n in neighbors]

            rerank_resp = co.rerank(
                model="rerank-v3.5",
                query=reformulated_query,
                documents=docs,
                top_n=min(limit, len(docs)),
            )

            neighbors_re = []
            for result in rerank_resp.results:
                idx = result.index
                new_score = result.relevance_score
                neighbors[idx]["similarity"] = new_score
                if new_score > 0.1:
                    neighbors_re.append(neighbors[idx])

            neighbors = neighbors_re

            map_table_and_id_to_similarity = {
                f"{n['source_table']}_{n['source_id']}": n["similarity"] for n in neighbors
            }
            source_ids = [n["source_id"] for n in neighbors]
            neighbor_tables = [n["source_table"] for n in neighbors]

            if topics and len(topics) == 1 and "," in topics[0]:
                topics = [t.strip() for t in topics[0].split(",") if t.strip()]

            params = {
                "source_tables": neighbor_tables,
                "source_ids": source_ids,
                "max_results": limit,
            }
            match = supabase.rpc("get_meetings_by_filter", params=params).execute()

            results = []
            if match.data:
                for record in match.data:
                    record["similarity"] = map_table_and_id_to_similarity[
                        f"{record['source_table']}_{record['source_id']}"
                    ]

                    results.append(record)

            # ---------- 2b)  LOG NON-EMPTY / EMPTY RESPONSE (semantic path) ----------
            logger.info(
                "Response formed – %d result(s) from semantic query",
                len(results[:limit]),
            )
            return JSONResponse(status_code=200, content={"data": results[:limit]})

        # --- DEFAULT QUERY CASE ---
        db_query = supabase.table("v_meetings").select("*")

        if source_tables:
            db_query = db_query.in_("source_table", source_tables)

        if start:
            db_query = db_query.gte("meeting_start_datetime", start.isoformat())
        if end:
            db_query = db_query.lte("meeting_start_datetime", end.isoformat())

        if country:
            # normalize to lowercase (for readability; ILIKE is case‑insensitive anyway)
            lower_countries = [c.lower() for c in country]

            # build something like:
            #   or=(location.ilike.*germany*,location.ilike.*france*,location.ilike.*spain*)
            or_clauses = ",".join(f"location.ilike.\"*{c}*\"" for c in lower_countries)

            db_query = db_query.or_(or_clauses)

        # --- TOPIC FILTERING ---
        if topics:
            if len(topics) == 1 and "," in topics[0]:
                topics = [t.strip() for t in topics[0].split(",") if t.strip()]
            db_query = db_query.in_("topic", topics)

            # --- USER RELEVANT MEETINGS CASE ---
        if user_id:
            relevant = fetch_relevant_meetings(
                user_id=user_id, k=100, query_to_compare=db_query, consider_frequency=False
            )
            data = []
            for m in relevant.meetings:
                data.append(m.model_dump(mode="json"))
            return JSONResponse(status_code=200, content={"data": data})

        res = db_query.order("meeting_start_datetime", desc=True).limit(limit).execute()
        data = res.data

        if not isinstance(data, list):
            raise ValueError("Expected list of records from Supabase")
        # ---------- 2c)  LOG NON-EMPTY / EMPTY RESPONSE (default path) ----------
        logger.info("Response formed – %d result(s) from default query", len(data))
        return JSONResponse(status_code=200, content={"data": data})

    except Exception as e:
        logger.error("INTERNAL ERROR: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/meetings/suggestions", response_model=MeetingSuggestionResponse)
@cache(namespace="meetings", expire=3600)
def get_meeting_suggestions(
    request: Request,
    query: str = Query(..., min_length=2, description="Fuzzy text to search meeting titles"),
    limit: int = Query(5, ge=1, le=20, description="Number of suggestions to return"),
):
    caller_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
    logger.info("GET /meetings/suggestions | caller=%s | query='%s' | limit=%s", caller_ip, query, limit)

    try:
        result = supabase.rpc("search_meetings_suggestions", {"search_text": query}).execute()

        return {"data": result.data[:limit]}

    except Exception as e:
        logger.error("INTERNAL ERROR: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/legislative-files/meetings", response_model=LegislativeMeetingsResponse)
@cache(namespace="meetings", expire=3600)  # type: ignore[arg-type]
def get_meetings_by_legislative_id(
    legislative_id: str = Query(..., description="Legislative procedure reference ID to filter meetings"),
    limit: int = Query(500, gt=0, le=1000, description="Maximum number of meetings to return"),
) -> JSONResponse:
    """
    Returns all meetings from the mep_meetings table that reference the given legislative (procedure_reference) ID
    """
    try:
        if not legislative_id or not legislative_id.strip():
            raise HTTPException(status_code=400, detail="legislative_id must be provided and non-empty.")

        result = (
            supabase.table("mep_meetings")
            .select("*")
            .eq("procedure_reference", legislative_id)
            .limit(limit)
            .order("meeting_date")
            .execute()
        )

        data = result.data
        if not isinstance(data, list):
            raise ValueError("Expected list of records from Supabase")

        logger.info(
            f"GET /legislative-files/meetings | legislative_id={legislative_id} | returned {len(data)} result(s)"
        )
        return JSONResponse(status_code=200, content={"data": data})
    except HTTPException as he:
        logger.warning(f"Bad request: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"INTERNAL ERROR in /legislative-files/meetings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.") from e
