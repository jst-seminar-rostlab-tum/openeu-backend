import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.core.supabase_client import supabase
from app.models.meeting import Meeting

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


_START = Query(None, description="Start datetime (ISO8601)")
_END = Query(None, description="End datetime (ISO8601)")


@router.get("/meetings", response_model=list[Meeting])
def get_meetings(limit: int = Query(100, gt=1), start: Optional[datetime] = _START, end: Optional[datetime] = _END):
    try:
        query = supabase.table("v_meetings").select("*")

        if start:
            query = query.gte("meeting_start_datetime", start.isoformat())
        if end:
            query = query.lte("meeting_start_datetime", end.isoformat())

        result = query.order("meeting_start_datetime", desc=True).limit(limit).execute()

        data = result.data

        if not isinstance(data, list):
            raise ValueError("Expected list of records from Supabase")

        return JSONResponse(status_code=200, content={"data": data})

    except Exception as e:
        logger.error("INTERNAL ERROR: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e