from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class Notification(BaseModel):
    id: int
    user_id: UUID
    sent_at: datetime
    type: str
    message: Optional[str]