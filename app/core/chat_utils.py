import logging
from datetime import datetime, timezone


from fastapi import HTTPException
from openai.types.chat import ChatCompletionAssistantMessageParam, ChatCompletionUserMessageParam
from openai import OpenAI
from app.core.supabase_client import supabase
from app.core.table_metadata import get_table_description
from app.core.vector_search import get_top_k_neighbors

client = OpenAI()


def build_system_prompt(messages: list[dict[str, str | int]], prompt: str, user_profile: str = "",
                        context_text: str = "") -> str:
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
    Ensure all responses are tailored to the user's profile
    If tailoring is not possible, provide a general response without forced personalization.
    The user profile is provided between ***START USER PROFILE*** and ***END USER PROFILE***.
    More information on how OpenEU works is between ***START CONTEXT BLOCK*** and ***END CONTEXT BLOCK***
    ***START USER PROFILE***
    {user_profile}
    ***END USER PROFILE***
    ***START CONTEXT BLOCK***
    {context_text}
    ***END CONTEXT BLOCK***`,
    """

    return assistant_system_prompt


def get_profile_embedding_input(user_id: str) -> str:
    result = supabase.table("profiles").select("embedding_input").eq("id", user_id).execute().data
    if result and len(result) == 1:
        return result[0]["embedding_input"]
    else:
        return ""


def get_response(prompt: str, session_id: str, user_id: str = "", context_text: str = ""):
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

        user_profile = get_profile_embedding_input(user_id) if user_id == "" else ""
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                ChatCompletionAssistantMessageParam(
                    content=build_system_prompt(messages, prompt, user_profile, context_text), role="assistant"
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
