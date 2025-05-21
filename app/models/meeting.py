from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class Meeting(BaseModel):
    meeting_id: str
    title: str
    meeting_start_datetime: datetime
    meeting_end_datetime: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = []

    