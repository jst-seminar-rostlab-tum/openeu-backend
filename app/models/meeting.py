from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Meeting(BaseModel):
    meeting_id: str
    title: str
    status: Optional[str] = None
    meeting_url: Optional[str] = None
    meeting_start_datetime: datetime
    meeting_end_datetime: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    similarity: Optional[float] = None
