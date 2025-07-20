from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Notification(BaseModel):
    id: int
    user_id: UUID
    sent_at: datetime
    message_subject: Optional[str]
    type: str
    message: Optional[str]
    relevance_score: Optional[float]