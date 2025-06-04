from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Notification(BaseModel):
    id: int
    user_id: UUID
    sent_at: datetime
    type: str
    message: Optional[str]
