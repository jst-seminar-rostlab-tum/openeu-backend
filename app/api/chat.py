import logging
from datetime import datetime, timezone


from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from openai import OpenAI
from openai.types.chat import ChatCompletionAssistantMessageParam, ChatCompletionUserMessageParam
from postgrest.exceptions import APIError
from pydantic import BaseModel

from app.core.auth import check_request_user_id
from app.core.supabase_client import supabase
from app.core.table_metadata import get_table_description
from app.core.vector_search import get_top_k_neighbors
from app.core.legislation_utils import get_or_extract_legislation_text, trigger_legislation_embedding_async

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


class LegislationRequest(BaseModel):
    legislation_id: str
    session_id: str
    message: str


def build_system_prompt(messages: list[dict[str, str | int]], prompt: str, context_text: str = "") -> str:
    messages_text = ""
    for message in messages:
        messages_text += f"{message['author']}: {message['content']}\n"

    if not context_text:
        context = get_top_k_neighbors(
            query=f"Previous conversation: {messages_text}\n\nQuestion: {prompt}", allowed_sources={}, k=20
        )
        context_text = ""
        for element in context:
            source_table = element.get("source_table")
            table_desc = get_table_description(source_table) if source_table else "Unspecified data"
            context_text += f"[Source: {table_desc}]\n{element.get('content_text')}\n\n"

    timestamp = datetime.now(timezone.utc).isoformat(timespec="minutes")

    assistant_system_prompt = f"""
    You are a helpful assistant working for Project Europe. Current time: {timestamp}.
    Your task is to answer questions on OpenEU, a platform for screening EU legal processes.
    You will get a question and a prior conversation if there is any and your task 
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


def get_response(prompt: str, session_id: str, context_text: str = ""):
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
                ChatCompletionAssistantMessageParam(
                    content=build_system_prompt(messages, prompt, context_text), role="assistant"
                ),
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


@router.post("/legislation/")
def process_legislation(legislation_request: LegislationRequest):
    """
    Process a legislative procedure: use RAG if embeddings exist, otherwise extract PDF text and store in DB.
    Returns a streaming LLM response or extracted text/info if no document is found, or raises an HTTPException on error
    Triggers embedding after extraction.
    """
    try:
        # 1. Check for existing embeddings for this legislative_id
        emb_response = (
            supabase.table("documents_embeddings")
            .select("*")
            .eq("source_id", legislation_request.legislation_id)
            .limit(1)
            .execute()
        )
        if emb_response.data and len(emb_response.data) > 0:
            # RAG flow
            try:
                neighbors = get_top_k_neighbors(
                    query=legislation_request.message,
                    sources=["document_embeddings"],
                    source_id=legislation_request.legislation_id,
                    k=10,
                )
                if not neighbors or len(neighbors) == 0:
                    return {"info": "No relevant context found for this legislative procedure. Please try again later."}
                context_text = ""
                for element in neighbors:
                    source_table = element.get("source_table")
                    table_desc = get_table_description(source_table) if source_table else "Unspecified data"
                    context_text += f"[Source: {table_desc}]\n{element.get('content_text')}\n\n"
                # Use the main chat streaming response with injected context
                return StreamingResponse(
                    get_response(
                        legislation_request.message, legislation_request.session_id, context_text=context_text
                    ),
                    media_type="text/event-stream",
                )
            except Exception as e:
                logging.error(f"RAG/LLM error for legislation_id={legislation_request.legislation_id}: {e}")
                raise HTTPException(
                    503, "Failed to generate answer for this legislative procedure, try again later"
                ) from None
        # 2. Fallback: extract and embed as before
        extracted_text = get_or_extract_legislation_text(legislation_request.legislation_id)
        if extracted_text is None:
            return {"extracted_text": None, "info": "No 'Legislative proposal' document found for this procedure."}
        # Always trigger embedding synchronously
        trigger_legislation_embedding_async(legislation_request.legislation_id, extracted_text)
        return {"extracted_text": extracted_text}
    except APIError as e:
        logging.error(f"Supabase APIError: {e}")
        raise HTTPException(503, "Failed to get legislative file, try again later") from None
    except Exception as e:
        logging.error(f"Unexpected error during legislation processing: {e}")
        raise HTTPException(503, "Failed to get legislative file, try again later") from None


if __name__ == "__main__":
    legislation_request = LegislationRequest(
        legislation_id="2025/0039(COD)",
        session_id="585f0e4e-b68d-423e-b278-78fd5085dd33",
        message="What is the proposal for?",
    )
    result = process_legislation(legislation_request)
    print(result)
