import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from openai import OpenAI
from openai.types.chat import ChatCompletionAssistantMessageParam, ChatCompletionUserMessageParam
from postgrest.exceptions import APIError
from pydantic import BaseModel

from app.core.supabase_client import supabase
from app.core.vector_search import get_top_k_neighbors

client = OpenAI()
router = APIRouter(prefix="/chat")


class NewSessionItem(BaseModel):
    title: str
    user_id: str


class ChatMessageItem(BaseModel):
    session_id: str
    message: str


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


def build_system_prompt(messages: list[dict[str, str | int]], prompt: str) -> str:
    messages_text = ""
    for message in messages:
        messages_text += f"{message['author']}: {message['content']}\n"

    context = get_top_k_neighbors(f"Previous conversation: {messages_text}\n\nQuestion: {prompt}", {}, 20)
    context_text = ""
    for element in context:
        context_text += f"{element.get('content_text')}\n"

    assistant_system_prompt = f"""
    You are a helpful assistant working for Project Europe. Your task is to answer questions on OpenEU, a platform 
    for screening EU legal processes. You will get a question and a prior conversation if there is any and your task 
    is to use your knowledge and the knowledge of OpenEU to answer the question. Do not answer any questions outside 
    the scope of OpenEU.\n\n
    *** BEGIN PREVIOUS CONVERSATION ***
    {messages_text}
    *** END PREVIOUS CONVERSATION ***\n\n
    You will not apologize for previous responses, but instead will indicated new information was gained.
    You will take into account any CONTEXT BLOCK that is provided in a conversation.
    You will say that you can't help on this topic if the CONTEXT BLOCK is empty.
    You will not invent anything that is not drawn directly from the context.
    You will not answer questions that are not related to the context.
    More information on how OpenEU works is between ***START CONTEXT BLOCK*** and ***END CONTEXT BLOCK***
    ***START CONTEXT BLOCK***
    {context_text}
    ***END CONTEXT BLOCK***`,
    """

    return assistant_system_prompt


def get_response(prompt: str, session_id: str):
    try:
        database_messages = (
            supabase.table("chat_messages").select("*").limit(10).eq("chat_session", session_id).execute()
        )
        messages = database_messages.data
        messages.sort(key=lambda message: message["id"])

        supabase.table("chat_messages").upsert(
            {
                "chat_session": session_id,
                "content": prompt,
                "author": "user",
                "date": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()
        message_response = (
            supabase.table("chat_messages")
            .upsert(
                {
                    "chat_session": session_id,
                    "content": "",
                    "author": "assistant",
                }
            )
            .execute()
        )

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                ChatCompletionAssistantMessageParam(content=build_system_prompt(messages, prompt), role="assistant"),
                ChatCompletionUserMessageParam(
                    content=f"Please answer the following question regarding OpenEU: {prompt}", role="user"
                ),
            ],
            temperature=0.3,
            stream=True,
        )
    except Exception as e:
        logging.error("Error in getting response from OpenAI: %s", e)
        fallback_text = (
            "Sorry, I'm currently experiencing technical difficulties and cannot provide an answer. "
            "Please try again in a few moments."
        )

        yield f"id: {session_id}\ndata: {fallback_text}\n\n"
        return  # Stop the generator
    try:
        full_response = ""
        for chunk in response:
            current_content = chunk.choices[0].delta.content
            if current_content is not None and len(current_content) > 0:
                full_response += current_content
                supabase.table("chat_messages").update(
                    {
                        "content": full_response,
                        "date": datetime.now(timezone.utc).isoformat(),
                    }
                ).eq("id", message_response.data[0].get("id")).eq("chat_session", session_id).execute()

                yield f"id: {session_id}\ndata: {current_content}\n\n"
    except Exception as e:
        logging.error("OpenAI response Error: " + str(e))
        raise HTTPException(503, "OpenAI server is busy, try again later") from None


@router.post("/")
async def get_chat_response(chat_message_item: ChatMessageItem):
    return StreamingResponse(
        get_response(chat_message_item.message, chat_message_item.session_id), media_type="text/event-stream"
    )


@router.post("/start", response_model=NewChatResponseModel)
def create_new_session(new_session_item: NewSessionItem) -> dict[str, str]:
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
def get_user_sessions(user_id: str) -> list[dict[str, str]]:
    try:
        response = supabase.table("chat_sessions").select("*").eq("user_id", user_id).execute()
    except APIError as e:
        logging.error(f"Supabase APIError: {e}")
        raise HTTPException(503, "Failed to get chat sessions, try again later") from None
    except Exception as e:
        logging.error(f"Unexpected error during select: {e}")
        raise HTTPException(503, "Failed to get chat sessions, try again later") from None

    return response.data
