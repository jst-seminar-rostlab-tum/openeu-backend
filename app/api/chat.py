import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam
from postgrest.exceptions import APIError
from pydantic import BaseModel

from app.core.supabase_client import supabase

client = OpenAI()
router = APIRouter(prefix="/chat")


class NewSessionItem(BaseModel):
    title: str
    user_id: str


class ChatResponseItem(BaseModel):
    session_id: str
    message: str


def get_response_openai(prompt: str, session_id: str):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                ChatCompletionUserMessageParam(content=prompt, role="user"),
            ],
            temperature=0.3,
            stream=True,
        )
    except Exception as e:
        logging.error("Error in getting response from OpenAI:", str(e))
        raise HTTPException(503, "OpenAI server is busy, try again later") from None
    try:
        for chunk in response:
            current_content = chunk.choices[0].delta.content
            if current_content is not None and len(current_content) > 0:
                yield f"id: {session_id}\ndata: {current_content}\n\n"
    except Exception as e:
        logging.error("OpenAI response Error: " + str(e))
        raise HTTPException(503, "OpenAI server is busy, try again later") from None


@router.post("/")
async def get_chat_response(chat_response_item: ChatResponseItem):
    return StreamingResponse(
        get_response_openai(chat_response_item.message, chat_response_item.session_id), media_type="text/event-stream"
    )


@router.post("/start")
def create_new_session(new_session_item: NewSessionItem) -> dict[str, int]:
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


@router.get("/sessions/{session_id}")
def get_all_messages(session_id: str) -> dict[str, str]:
    return {"session_id": session_id}


@router.get("/sessions")
def get_user_sessions(user_id: str) -> dict[str, str]:
    return {"user_id": user_id}
