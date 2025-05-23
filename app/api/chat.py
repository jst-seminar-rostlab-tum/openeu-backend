import logging
import random
import string

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


class ChatResponseItem(BaseModel):
    session_id: int
    message: str


def build_system_prompt(messages: list[dict[str, str | int]], prompt: str) -> str:
    messages_text = ""
    for message in messages:
        messages_text += f"{message['author']}: {message['content']}\n"

    context = get_top_k_neighbors(
        f"Previous conversation: {messages_text}\n\nQuestion: {prompt}", {"bt_plenarprotokolle": "text"}
    )
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


def get_response(prompt: str, session_id: int):
    try:
        database_messages = supabase.table("chat_messages").select("*").eq("chat_session", session_id).execute()
        messages = database_messages.data
        messages.sort(key=lambda message: message["id"])
        if len(messages) > 10:
            messages = messages[-10:]

        thread_id = "".join(random.choices(string.ascii_letters + string.digits, k=20))
        supabase.table("chat_messages").upsert(
            {
                "chat_session": session_id,
                "content": prompt,
                "author": "user",
            }
        ).execute()
        supabase.table("chat_messages").upsert(
            {
                "chat_session": session_id,
                "content": "",
                "author": "assistant",
                "thread_id": thread_id,
            }
        ).execute()

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
        logging.error("Error in getting response from OpenAI:", str(e))
        raise HTTPException(503, "OpenAI server is busy, try again later") from None
    try:
        full_response = ""
        for chunk in response:
            current_content = chunk.choices[0].delta.content
            if current_content is not None and len(current_content) > 0:
                full_response += current_content
                supabase.table("chat_messages").update(
                    {
                        "content": full_response,
                    }
                ).eq("thread_id", thread_id).eq("chat_session", session_id).execute()

                yield f"id: {session_id}\ndata: {current_content}\n\n"
    except Exception as e:
        logging.error("OpenAI response Error: " + str(e))
        raise HTTPException(503, "OpenAI server is busy, try again later") from None


@router.post("/")
async def get_chat_response(chat_response_item: ChatResponseItem):
    return StreamingResponse(
        get_response(chat_response_item.message, chat_response_item.session_id), media_type="text/event-stream"
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
def get_all_messages(session_id: int) -> list[dict[str, str | int]]:
    try:
        response = supabase.table("chat_messages").select("*").eq("chat_session", session_id).execute()
    except APIError as e:
        logging.error(f"Supabase APIError: {e}")
        raise HTTPException(503, "Failed to get chat sessions, try again later") from None
    except Exception as e:
        logging.error(f"Unexpected error during select: {e}")
        raise HTTPException(503, "Failed to get chat sessions, try again later") from None

    return response.data


@router.get("/sessions")
def get_user_sessions(user_id: str) -> list[dict[str, str | int]]:
    try:
        response = supabase.table("chat_sessions").select("*").eq("user_id", user_id).execute()
    except APIError as e:
        logging.error(f"Supabase APIError: {e}")
        raise HTTPException(503, "Failed to get chat sessions, try again later") from None
    except Exception as e:
        logging.error(f"Unexpected error during select: {e}")
        raise HTTPException(503, "Failed to get chat sessions, try again later") from None

    return response.data
