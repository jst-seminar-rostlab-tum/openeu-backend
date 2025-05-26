import logging
from collections import defaultdict
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.supabase_client import supabase
from app.core.vector_search import get_top_k_neighbors_by_embedding
from app.models.meeting import Meeting

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/meetings", tags=["meetings"])

_START = Query(None, description="Start datetime (ISO8601)")
_END = Query(None, description="End datetime (ISO8601)")


@router.get("/", response_model=list[Meeting])
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


class RelevantMeetingsResponse(BaseModel):
    meetings: list[Meeting]


@router.get("/relevant", response_model=RelevantMeetingsResponse, summary="Fetch your top-K most relevant meetings")
async def fetch_relevant_meetings(
    user_id: str = Query(..., description="Supabase user ID"),
    k: int = Query(5, ge=1, le=100, description="Number of meetings to return"),
):
    """
    1) load the stored profile embedding for `user_id`
    2) call `get_top_k_relevant_meetings(embedding, start_date, end_date, k)`
    3) return meetings + normalized relevance scores
    """
    # 1) fetch profile embedding
    resp = supabase.table("profiles").select("embedding").eq("id", user_id).single().execute()

    profile_embedding = resp.data["embedding"]
    meetings = get_top_k_neighbors_by_embedding(
        vector_embedding=profile_embedding,
        allowed_sources={
            "ep_meetings": "title",
            "mep_meetings": "title",
            "ipex_events": "title",
            "austrian_parliament_meetings": "title",
        },
        k=k,
    )
    if not meetings:
        return JSONResponse(status_code=200, content={"data": []})

    ids_by_source = defaultdict(list)
    for n in meetings:
        ids_by_source[n["source_table"]].append(n["source_id"])

    fetched = {}
    base_query = supabase.table("v_meetings").select("*")

    for source_table, id_list in ids_by_source.items():
        print(source_table)
        print(id_list)
        rows = base_query.eq("source_table", source_table).in_("source_id", id_list).execute().data
        for row in rows:
            fetched[(source_table, row["source_id"])] = row

    ordered_rows = [
        fetched[(n["source_table"], n["source_id"])] for n in meetings if (n["source_table"], n["source_id"]) in fetched
    ]
    print(ordered_rows)

    try:
        return JSONResponse(status_code=200, content={"data": ordered_rows})
    except Exception as ve:
        logger.error("Pydantic validation failed: %s", ve)
        raise HTTPException(status_code=500, detail="Data format error") from ve
