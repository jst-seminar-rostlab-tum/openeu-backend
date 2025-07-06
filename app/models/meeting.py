from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.person import Person


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
    member: Optional[Person] = None
    attendees: Optional[str] = None


class MeetingSuggestion(BaseModel):
    title: str
    similarity_score: float


class RelevantMeetingsResponse(BaseModel):
    meetings: list[Meeting]


class MeetingSuggestionResponse(BaseModel):
    data: list[MeetingSuggestion]
