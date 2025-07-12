import logging
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from typing import Optional

from fastapi_cache.decorator import cache

from app.core.relevant_legislatives import fetch_relevant_legislative_files
from app.core.supabase_client import supabase
from app.core.cohere_client import co
from app.core.vector_search import get_top_k_neighbors
from app.core.openai_client import openai
from app.models.legislative_file import (
    LegislativeFilesResponse,
    LegislativeFileResponse,
    LegislativeFileSuggestionResponse,
)


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/legislative-files", response_model=LegislativeFilesResponse)
@cache(namespace="legislative", expire=3600)
def get_legislative_files(
    limit: int = Query(500, gt=1),
    query: Optional[str] = Query(None, description="Semantic search query"),
    year: Optional[int] = Query(None, description="Filter by reference year (e.g. 2025)"),
    committee: Optional[str] = Query(None, description="Filter by committee name"),
    rapporteur: Optional[str] = Query(None, description="Filter by rapporteur name"),
    user_id: Optional[str] = Query(None, description="User ID for personalized meeting recommendations"),
):
    try:
        if query:
            if user_id:
                resp = supabase.table("profiles").select("embedding_input").eq("id", user_id).single().execute()
                if resp.data:
                    query = query + "Profile information: " + str(resp.data)
            try:
                # 1. Use the correct Chat Completions endpoint
                completion = openai.chat.completions.create(
                    # 2. Use a valid, current model name (e.g., gpt-4o-mini)
                    model="gpt-4o-mini",
                    # 3. Structure the input as a 'messages' list
                    #    This is the most important change.
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

                # 4. Access the response correctly via .message.content
                reformulated_query = (completion.choices[0].message.content or query).strip()

            except Exception as e:
                logger.error(f"An error occurred: {e}")

            neighbors = get_top_k_neighbors(
                query=reformulated_query,
                allowed_sources={"legislative_files": "embedding_input"},
                k=1000,
                sources=["document_embeddings"],  # triggers match_filtered
            )

            if not neighbors:
                return JSONResponse(status_code=200, content={"data": []})

            docs = [n["content_text"] for n in neighbors]

            rerank_resp = co.rerank(
                model="rerank-v3.5",
                query=reformulated_query,
                documents=docs,
                top_n=min(limit, len(docs)),
            )

            neighbors_re = []
            # 2) unpack the (index, similarity) tuples
            for result in rerank_resp.results:
                idx = result.index
                new_score = result.relevance_score
                # overwrite the old vector-search score with the reranker’s score
                neighbors[idx]["similarity"] = new_score
                if new_score > 0.15:
                    neighbors_re.append(neighbors[idx])

            neighbors = neighbors_re

            # Fetch matched rows
            ids = [n["source_id"] for n in neighbors]
            similarity_map = {n["source_id"]: n["similarity"] for n in neighbors}

            response = supabase.table("legislative_files").select("*").in_("id", ids).execute()
            records = response.data or []

            # Add similarity info
            for r in records:
                r["similarity"] = similarity_map.get(r["id"])

        else:
            db_query = supabase.table("legislative_files").select("*")

            if year:
                year_prefix = f"{year}%"
                db_query = db_query.like("id", year_prefix)

            if committee:
                db_query = db_query.eq("committee", committee)

            if rapporteur:
                db_query = db_query.eq("rapporteur", rapporteur)

            if user_id:
                relevant = fetch_relevant_legislative_files(user_id=user_id, query_to_compare=db_query, k=limit)
                data = []
                for m in relevant.legislative_files:
                    data.append(m.model_dump(mode="json"))
                return JSONResponse(status_code=200, content={"data": data})

            res = db_query.limit(limit).execute()
            records = res.data or []

        return JSONResponse(status_code=200, content={"data": records[:limit]})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/legislative-file", response_model=LegislativeFileResponse)
@cache(namespace="legislative", expire=86400)
def get_legislative_file(id: str = Query(..., description="Legislative file ID")):
    """Get a single legislative file by ID"""
    try:
        response = supabase.table("legislative_files").select("*").eq("id", id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail=f"Legislative file with ID '{id}' not found")

        return JSONResponse(status_code=200, content={"legislative_file": response.data[0]})

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching legislative file %s: %s", id, e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/legislative-files/suggestions", response_model=LegislativeFileSuggestionResponse)
@cache(namespace="legislative", expire=3600)
def get_legislation_suggestions(
    request: Request,
    query: str = Query(..., min_length=2, description="Fuzzy text to search legislation titles"),
    limit: int = Query(5, ge=1, le=20, description="Number of suggestions to return"),
):
    caller_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
    logger.info("GET /legislative-files/suggestions | caller=%s | query='%s' | limit=%s", caller_ip, query, limit)

    try:
        result = supabase.rpc("search_legislation_suggestions", {"search_text": query}).execute()
        result = supabase.rpc("search_legislation_suggestions", {"search_text": query}).execute()

        return {"data": result.data[:limit]}

    except Exception as e:
        logger.error("INTERNAL ERROR: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/legislative-files/unique-values")
def get_legislative_unique_values():
    """Returns unique values for year, committee, and status from legislative files."""
    try:
        response = supabase.table("legislative_files").select("id, committee, status").execute()
        data = response.data or []

        years = set()
        committees = set()
        statuses = set()

        for row in data:
            if row.get("id"):
                year_part = row["id"][:4]
                if year_part.isdigit():
                    years.add(year_part)
            if row.get("committee"):
                committees.add(row["committee"])
            if row.get("status"):
                statuses.add(row["status"])

        return {
            "years": sorted(list(years)),
            "committees": sorted(list(committees)),
            "statuses": sorted(list(statuses)),
        }
    except Exception as e:
        logger.error("Something went wrong: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
