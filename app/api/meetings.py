import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from app.core.supabase_client import supabase
from app.core.vector_search import get_top_k_neighbors
from app.models.meeting import Meeting

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

router = APIRouter()


_START = Query(None, description="Start datetime (ISO8601)")
_END = Query(None, description="End datetime (ISO8601)")
_TOPICS = Query(None, description="List of topic names (repeat or comma-separated)")
_SOURCE_TABLES = Query(
    None, alias="source_table", description="Filter by source table(s) (repeat or comma-separated)"
)  # URL param stays singular: ?source_table=…
DEFAULT_COUNTRY = Query(None, description="Filter by country (e.g., 'Austria', 'European Union')")



def to_utc_aware(dt: Optional[datetime]) -> Optional[datetime]:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@router.get("/meetings", response_model=list[Meeting])
def get_meetings(
    request: Request,  # new param: provides caller info
    limit: int = Query(500, gt=1),
    start: Optional[datetime] = _START,
    end: Optional[datetime] = _END,
    query: Optional[str] = Query(None, description="Search query using semantic similarity"),
    topics: Optional[list[str]] = _TOPICS,
    country: Optional[list[str]] = DEFAULT_COUNTRY,
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
    try:
        start = to_utc_aware(start)
        end = to_utc_aware(end)

        # --- SEMANTIC QUERY CASE ---
        # --- source table - normalise multi-value params ----------------------------------
        logging.info(f"tables: {source_tables}")

        if source_tables and len(source_tables) == 1 and "," in source_tables[0]:
            source_tables = [t.strip() for t in source_tables[0].split(",") if t.strip()]

        if query:
            # tell the vector search which tables are allowed -- value can be any string
            allowed_sources: dict[str, str] = {t: "embedding_input" for t in source_tables} if source_tables else {}
            logging.info(f"tables: {source_tables}")

            neighbors = get_top_k_neighbors(
                query=query,
                allowed_topic_ids=topics,
                allowed_countries=country,
                allowed_sources=allowed_sources,
                k=limit,
                sources=["meeting_embeddings"],
            )
            if not neighbors:
                # ---------- 2a)  LOG EMPTY RESPONSE (semantic path, no neighbours) ----------
                logger.info("Response formed – empty list (no neighbours found)")
                return JSONResponse(status_code=200, content={"data": []})
            
            # Create a lookup from neighbors for fast similarity access
            similarity_lookup = {
                (n["source_table"], n["source_id"]): n["similarity"] for n in neighbors
            }


            db_query = supabase.table("v_meetings").select("*")

            conditions = [f"and(source_table.eq.{n['source_table']},source_id.eq.{n['source_id']})" for n in neighbors]

            db_query = supabase.table("v_meetings").select("*").or_(",".join(conditions))

            logger.info(f"{conditions}")

            if start:
                db_query = db_query.gte("meeting_start_datetime", start.isoformat())
            if end:
                db_query = db_query.lte("meeting_start_datetime", end.isoformat())

            result = db_query.order("meeting_start_datetime", desc=True).limit(limit).execute()
            data = result.data
            
            for item in data:
                key = (item["source_table"], item["source_id"])
                item["similarity"] = similarity_lookup.get(key)

            if not isinstance(data, list):
                raise ValueError("Expected list of records from Supabase")
            # ---------- 2b)  LOG NON-EMPTY / EMPTY RESPONSE (default path) ----------
            logger.info("Response formed – %d result(s) from default query", len(data))
            return JSONResponse(status_code=200, content={"data": data})

        # --- DEFAULT QUERY CASE ---
        db_query = supabase.table("v_meetings").select("*")

        if source_tables:
            db_query = db_query.in_("source_table", source_tables)

        if start:
            db_query = db_query.gte("meeting_start_datetime", start.isoformat())
        if end:
            db_query = db_query.lte("meeting_start_datetime", end.isoformat())
        if country:
            db_query = db_query.in_("location", country)

        # --- TOPIC FILTERING ---
        if topics:
            if len(topics) == 1 and "," in topics[0]:
                topics = [t.strip() for t in topics[0].split(",") if t.strip()]
            db_query = db_query.in_("topic_id", topics)

        result = db_query.order("meeting_start_datetime", desc=True).limit(limit).execute()
        data = result.data

        if not isinstance(data, list):
            raise ValueError("Expected list of records from Supabase")
        # ---------- 2c)  LOG NON-EMPTY / EMPTY RESPONSE (default path) ----------
        logger.info("Response formed – %d result(s) from default query", len(data))
        return JSONResponse(status_code=200, content={"data": data})

    except Exception as e:
        logger.error("INTERNAL ERROR: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
