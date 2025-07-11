import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache

from app.core.extract_topics import TOPICS_TABLE
from app.core.supabase_client import supabase
from app.models.topic import Topic

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/topics", response_model=dict[str, list[Topic]])
@cache(namespace="topics", expire=86400)
def get_topics():
    try:
        response = supabase.table(TOPICS_TABLE).select("*").execute()
        return JSONResponse(status_code=200, content={"data": response.data})
    except Exception as e:
        logger.error("INTERNAL ERROR: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
