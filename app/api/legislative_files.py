import logging
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from typing import Optional

from fastapi_cache.decorator import cache

from app.core.auth import check_request_user_id
from app.core.relevant_legislatives import fetch_relevant_legislative_files
from app.core.supabase_client import supabase
from app.core.vector_search import get_top_k_neighbors
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
    request: Request,
    limit: int = Query(500, gt=1),
    query: Optional[str] = Query(None, description="Semantic search query"),
    year: Optional[int] = Query(None, description="Filter by reference year (e.g. 2025)"),
    committee: Optional[str] = Query(None, description="Filter by committee name"),
    rapporteur: Optional[str] = Query(None, description="Filter by rapporteur name"),
    user_id: Optional[str] = Query(None, description="User ID for personalized meeting recommendations"),
):
    check_request_user_id(request, user_id)
    try:
        if query:
            if user_id:
                resp = supabase.table("profiles").select("embedding_input").eq("id", user_id).single().execute()
                if resp.data:
                    query = query + "Profile information: " + str(resp.data)
            neighbors = get_top_k_neighbors(
                query=query,
                allowed_sources={"legislative_files": "embedding_input"},
                k=limit,
                sources=["document_embeddings"],
            )

            if not neighbors:
                return JSONResponse(status_code=200, content={"data": []})

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

            result = db_query.limit(limit).execute()
            records = result.data or []

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

        return {"data": result.data[:limit]}

    except Exception as e:
        logger.error("INTERNAL ERROR: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
