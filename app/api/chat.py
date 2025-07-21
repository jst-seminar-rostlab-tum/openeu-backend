import logging
from datetime import datetime


from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from postgrest.exceptions import APIError
from pydantic import BaseModel

from app.core.auth import check_request_user_id
from app.core.supabase_client import supabase
from app.core.legislation_utils import process_legislation
from app.models.chat import ChatMessageItem
from app.core.chat_utils import get_response

router = APIRouter(prefix="/chat")


class NewSessionItem(BaseModel):
    title: str
    user_id: str


class NewChatResponseModel(BaseModel):
    session_id: str


class MessagesResponseModel(BaseModel):
    id: str
    chat_session: str
    content: str
    author: str
    date: datetime


class SessionsResponseModel(BaseModel):
    id: str
    user_id: str
    title: str


@router.post("/")
async def get_chat_response(chat_message_item: ChatMessageItem):
    if chat_message_item.legislation_id:
        return StreamingResponse(process_legislation(chat_message_item), media_type="text/event-stream")
    return StreamingResponse(
        get_response(chat_message_item.message, chat_message_item.user_id, chat_message_item.session_id),
        media_type="text/event-stream"
    )


@router.post("/start", response_model=NewChatResponseModel)
def create_new_session(request: Request, new_session_item: NewSessionItem) -> dict[str, str]:
    check_request_user_id(request, new_session_item.user_id)
    data = {
        "title": new_session_item.title,
        "user_id": new_session_item.user_id,
    }

    try:
        response = supabase.table("chat_sessions").upsert(data).execute()
    except APIError as e:
        logging.error(f"Supabase APIError: {e}")
        raise HTTPException(503, "Failed to create chat session, try again later") from None
    except Exception as e:
        logging.error(f"Unexpected error during upsert: {e}")
        raise HTTPException(503, "Failed to create chat session, try again later") from None

    return {"session_id": response.data[0].get("id")}


@router.get("/sessions/{session_id}", response_model=list[MessagesResponseModel])
def get_all_messages(session_id: str) -> list:
    try:
        response = supabase.table("chat_messages").select("*").order("date").eq("chat_session", session_id).execute()
    except APIError as e:
        logging.error(f"Supabase APIError: {e}")
        raise HTTPException(503, "Failed to get chat sessions, try again later") from None
    except Exception as e:
        logging.error(f"Unexpected error during select: {e}")
        raise HTTPException(503, "Failed to get chat sessions, try again later") from None

    return response.data


@router.get("/sessions", response_model=list[SessionsResponseModel])
def get_user_sessions(request: Request, user_id: str) -> list[dict[str, str]]:
    check_request_user_id(request, user_id)
    try:
        response = supabase.table("chat_sessions").select("*").eq("user_id", user_id).execute()
    except APIError as e:
        logging.error(f"Supabase APIError: {e}")
        raise HTTPException(503, "Failed to get chat sessions, try again later") from None
    except Exception as e:
        logging.error(f"Unexpected error during select: {e}")
        raise HTTPException(503, "Failed to get chat sessions, try again later") from None

    return response.data
