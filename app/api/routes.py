from datetime import date
from typing import Optional

from fastapi import APIRouter, Query

from app.models.meeting import Meeting

router = APIRouter()


@router.get("/meetings", response_model=list[Meeting])
def get_meetings(
    frequency: Optional[str] = Query(None, enum=["daily", "weekly", "monthly"]),
    country: Optional[str] = None,
):
    return [Meeting(date=date.today(), name="EU Tech Summit", tags=["tech", "eu"])]
