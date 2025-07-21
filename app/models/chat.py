from pydantic import BaseModel


class ChatMessageItem(BaseModel):
    session_id: str
    user_id: str | None = None
    message: str
    legislation_id: str | None = None
