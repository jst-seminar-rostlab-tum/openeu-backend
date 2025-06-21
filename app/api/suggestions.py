import logging
from fastapi import APIRouter, HTTPException, Query, Request

from app.core.supabase_client import supabase

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/suggestions")
def get_suggestions(
    request: Request,
    query: str = Query(..., min_length=2, description="Fuzzy text to search meeting titles"),
    limit: int = Query(5, ge=1, le=20, description="Number of suggestions to return"),
):
    caller_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
    logger.info("GET /suggestions | caller=%s | query='%s' | limit=%s", caller_ip, query, limit)

    try:
        result = supabase.rpc("search_meetings_suggestions", {"search_text": query}).execute()

        return {"data": result.data[:limit]}

    except Exception as e:
        logger.error("INTERNAL ERROR: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
