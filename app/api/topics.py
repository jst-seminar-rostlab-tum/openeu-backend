import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.core.extract_topics import TABLE_NAME
from app.core.supabase_client import supabase
from app.models.topic import Topic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/topics", response_model=list[Topic])
def get_topics():
    try:
        response = supabase.table(TABLE_NAME).select("*").execute()

        return JSONResponse(status_code=200, content={"data": response.data})
    except Exception as e:
        logger.error("INTERNAL ERROR: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
