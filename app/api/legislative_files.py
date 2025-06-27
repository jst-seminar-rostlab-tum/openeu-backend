import logging
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from typing import Optional

from app.core.supabase_client import supabase
from app.core.vector_search import get_top_k_neighbors
from app.models.legislative_file import LegislativeFilesResponse, LegislativeFileSuggestionResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/legislative-files", response_model=LegislativeFilesResponse)
def get_legislative_files(
    limit: int = Query(100, gt=1),
    query: Optional[str] = Query(None, description="Semantic search query"),
    year: Optional[int] = Query(None, description="Filter by reference year (e.g. 2025)"),
    committee: Optional[str] = Query(None, description="Filter by committee name"),
    rapporteur: Optional[str] = Query(None, description="Filter by rapporteur name"),
):
    try:
        if query:
            neighbors = get_top_k_neighbors(
                query=query,
                allowed_sources={"legislative_files": "embedding_input"},
                k=limit,
                sources=["document_embeddings"],  # triggers match_filtered
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
            response = supabase.table("legislative_files").select("*").limit(limit).execute()
            records = response.data or []

        # Apply year filtering
        if year:
            records = [r for r in records if r.get("id", "").startswith(str(year))]

        # Apply committee filtering
        if committee:
            records = [r for r in records if r.get("committee") == committee]

        if rapporteur:
            records = [r for r in records if r.get("rapporteur") == rapporteur]

        return JSONResponse(status_code=200, content={"data": records[:limit]})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/legislative-files/suggestions", response_model=LegislativeFileSuggestionResponse)
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
