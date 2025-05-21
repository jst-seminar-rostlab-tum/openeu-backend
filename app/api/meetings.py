from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Query, HTTPException
from dateutil.relativedelta import relativedelta   # pip install python-dateutil

from app.models.meeting import Meeting
from app.supabase_client import supabase

router = APIRouter()

@router.get("/meetings", response_model=List[Meeting])
def get_meetings(
    frequency: Optional[str] = Query(
        None, description="Next time window", enum=["daily", "weekly", "monthly"]
    ),
    country: Optional[str] = Query(None, description="Filter by meeting_location"),
):
    # ---------- build the Supabase query ----------
    q = supabase.table("v_meetings").select("*")

    # country filter (exact match – switch to ilike if you want case-insensitive)
    if country:
        q = q.eq("location", country)

    # time window filter
    if frequency:
        now = datetime.utcnow()
        if frequency == "daily":
            end = now + timedelta(days=1)
        elif frequency == "weekly":
            end = now + timedelta(weeks=1)
        else:                       # monthly
            end = now + relativedelta(months=1)

        q = (
            q.gte("meeting_start_datetime", now.isoformat())
             .lt ("meeting_start_datetime", end.isoformat())
        )

    # ---------- run the query ----------
    resp = q.execute()
    if resp.error:
        raise HTTPException(status_code=500, detail=resp.error.message)

    return [Meeting(**row) for row in resp.data]


