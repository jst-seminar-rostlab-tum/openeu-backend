from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.core.supabase_client import supabase

router = APIRouter()


_LIMIT = Query(20, gt=1)
_START = Query(None, description="Start datetime (ISO8601)")
_END   = Query(None, description="End datetime (ISO8601)")


@router.get("/meetings")
def get_meetings(
    limit: _LIMIT, # type: ignore
    start: Optional[datetime] = _START,
    end:   Optional[datetime] = _END
):
    try:
        # build base query
        query = supabase.table("v_meetings").select("*")

        # apply date filters if provided
        if start:
            query = query.gte("meeting_start_datetime", start.isoformat())
        if end:
            query = query.lte("meeting_start_datetime", end.isoformat())

        # finalize
        result = (
            query
            .order("meeting_start_datetime", desc=True)
            .limit(limit)
            .execute()
        )

        data = result.data

        if not isinstance(data, list):
            raise ValueError("Expected list of records from Supabase")

        return JSONResponse(status_code=200, content={"data": data})

    except Exception as e:
        print("INTERNAL ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
