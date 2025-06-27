from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Meeting(BaseModel):
    meeting_id: str
    source_table: str
    source_id: str
    title: str
    topic: Optional[str] = None
    status: Optional[str] = None
    meeting_url: Optional[str] = None
    meeting_start_datetime: datetime
    meeting_end_datetime: Optional[datetime] = None
    location: Optional[str] = None
    exact_location: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    similarity: Optional[float] = None


class RelevantMeetingsResponse(BaseModel):
    meetings: list[Meeting]
