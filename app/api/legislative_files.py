from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional

from app.core.supabase_client import supabase
from app.core.vector_search import get_top_k_neighbors
from app.models.legislative_file import LegislativeFilesResponse

router = APIRouter()


@router.get("/legislative_files", response_model=LegislativeFilesResponse)
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
                allowed_sources={"legislative_files": "title"},
                k=limit,
                sources=["document_embeddings"],  # triggers match_filtered
            )

            if not neighbors:
                return JSONResponse(status_code=200, content={"data": []})

            # Fetch matched rows
            ids = [n["source_id"] for n in neighbors]
            similarity_map = {n["source_id"]: n["similarity"] for n in neighbors}

            response = supabase.table("legislative_files").select("*").in_("reference", ids).execute()
            records = response.data or []

            # Add similarity info
            for r in records:
                r["similarity"] = similarity_map.get(r["reference"])

        else:
            response = supabase.table("legislative_files").select("*").limit(limit).execute()
            records = response.data or []

        # Apply year filtering
        if year:
            records = [r for r in records if r.get("reference", "").startswith(str(year))]

        # Apply committee filtering
        if committee:
            records = [r for r in records if r.get("committee") == committee]

        if rapporteur:
            records = [r for r in records if r.get("rapporteur") == rapporteur]

        return JSONResponse(status_code=200, content={"data": records[:limit]})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
