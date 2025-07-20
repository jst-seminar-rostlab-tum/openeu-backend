from pydantic import BaseModel


class ChatMessageItem(BaseModel):
    session_id: str
    message: str
    legislation_id: str | None = None
