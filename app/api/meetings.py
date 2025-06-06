import logging
from datetime import datetime, timezone
from typing import Optional

from dateutil import parser
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.core.supabase_client import supabase
from app.core.vector_search import get_top_k_neighbors
from app.models.meeting import Meeting

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


_START = Query(None, description="Start datetime (ISO8601)")
_END = Query(None, description="End datetime (ISO8601)")


def to_utc_aware(dt: Optional[datetime]) -> Optional[datetime]:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@router.get("/meetings", response_model=list[Meeting])
def get_meetings(
    limit: int = Query(100, gt=1),
    start: Optional[datetime] = _START,
    end: Optional[datetime] = _END,
    query: Optional[str] = Query(None, description="Search query using semantic similarity"),
):
    try:
        start = to_utc_aware(start)
        end = to_utc_aware(end)

        if query:
            neighbors = get_top_k_neighbors(
                query=query,
                allowed_sources={
                    "ep_meetings": "title",
                    "mep_meetings": "title",
                    "ipex_events": "title",
                    "austrian_parliament_meetings": "title",
                },
                k=100,
            )

            if not neighbors:
                return JSONResponse(status_code=200, content={"data": []})

            results = []
            for neighbor in neighbors:
                match = (
                    supabase.table("v_meetings")
                    .select("*")
                    .eq("source_table", neighbor["source_table"])
                    .eq("source_id", neighbor["source_id"])
                    .limit(1)
                    .execute()
                )

                if match.data:
                    record = match.data[0]
                    meeting_time_str = record.get("meeting_start_datetime")
                    if not meeting_time_str:
                        continue

                    meeting_time = to_utc_aware(parser.isoparse(meeting_time_str))
                    assert meeting_time is not None

                    should_include = True
                    if start is not None and meeting_time < start:
                        should_include = False
                    if end is not None and meeting_time > end:
                        should_include = False

                    if should_include:
                        results.append(record)

            return JSONResponse(status_code=200, content={"data": results})

        db_query = supabase.table("v_meetings").select("*")

        if start:
            db_query = db_query.gte("meeting_start_datetime", start.isoformat())
        if end:
            db_query = db_query.lte("meeting_start_datetime", end.isoformat())

        result = db_query.order("meeting_start_datetime", desc=True).limit(limit).execute()
        data = result.data

        if not isinstance(data, list):
            raise ValueError("Expected list of records from Supabase")

        return JSONResponse(status_code=200, content={"data": data})

    except Exception as e:
        logger.error("INTERNAL ERROR: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
