import logging
from typing import Optional
from datetime import datetime, time, timedelta

from openai import OpenAI
from postgrest import SyncSelectRequestBuilder
from pydantic import BaseModel, ValidationError
from app.core.cohere_client import co

from app.core.config import Settings
from app.core.supabase_client import supabase
from app.core.vector_search import get_top_k_neighbors
from app.models.meeting import Meeting


class RelevantMeetingsResponse(BaseModel):
    meetings: list[Meeting]


settings = Settings()
openai = OpenAI(api_key=settings.get_openai_api_key())
EMBED_MODEL = "text-embedding-ada-002"


logger = logging.getLogger(__name__)


def fetch_relevant_meetings(
    user_id: str,
    k: int,
    query_to_compare: Optional[SyncSelectRequestBuilder] = None,
    consider_frequency: bool = True,
) -> RelevantMeetingsResponse:
    meetings: list[Meeting] = []
    # 1) load the stored profile embedding for `user_id`
    try:
        resp = (
            supabase.table("v_profiles")
            .select("embedding", "countries", "newsletter_frequency", "topic_ids", "embedding_input")
            .eq("id", user_id)
            .single()
            .execute()
        )
        profile_embedding_input = resp.data["embedding_input"]
        newsletter_frequency = resp.data.get("newsletter_frequency", "daily")
        allowed_topic_ids = resp.data["topic_ids"]
        allowed_countries = resp.data["countries"]

    except Exception as e:
        logger.exception(f"Unexpected error loading profile embedding or profile doesnt exist: {e}")
        return RelevantMeetingsResponse(meetings=[])

    # 2) call `get_top_k_neighbors`

    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that reformulates text for semantic search. "
                        "Your task is to generate a meeting title for a legislative/institutional meeting concerning the user. "
                        "For example:\n"
                        "User Input: As the CEO of Transport Logistics, a company pioneering the integration of AI in transportation, "
                        "I am steering a dynamic growth-stage enterprise with a team of 21-50 professionals.\n"
                        "Output: Meeting on Infrastructure and Technology"
                    ),
                },
                {"role": "user", "content": profile_embedding_input},
            ],
            temperature=0,
            max_tokens=128,
        )
        reformulated_query = (completion.choices[0].message.content or profile_embedding_input).strip()

    except Exception as e:
        reformulated_query = profile_embedding_input
        logger.error(f"An error occurred: {e}")

    try:
        start_date_time = None
        end_date_time = None

        if consider_frequency:
            today = datetime.now().date()

            if newsletter_frequency == "weekly":
                # Start from Monday of the current week
                start_date = today - timedelta(days=today.weekday())
                start_date_time = datetime.combine(start_date, time.min)
                end_date = start_date + timedelta(days=6)
                end_date_time = datetime.combine(end_date, time.max)
            else:
                # Start and end are just today
                start_date_time = datetime.combine(today, time.min)
                end_date_time = datetime.combine(today, time.max)

        neighbors = get_top_k_neighbors(
            query=reformulated_query,
            sources=["meeting_embeddings"],
            allowed_topic_ids=allowed_topic_ids,
            allowed_countries=allowed_countries,
            start_date=start_date_time,
            end_date=end_date_time,
            k=1000,
        )

        docs = [n["content_text"] for n in neighbors]

        rerank_resp = co.rerank(
            model="rerank-v3.5",
            query=reformulated_query,
            documents=docs,
            top_n=min(k, len(docs)),
        )

        neighbors_re = []
        for result in rerank_resp.results:
            idx = result.index
            new_score = result.relevance_score
            neighbors[idx]["similarity"] = new_score
            if new_score > 0.05:
                neighbors_re.append(neighbors[idx])

        neighbors = neighbors_re

        sorted_neighbors = sorted(neighbors, key=lambda n: n["similarity"], reverse=True)[:k]

        if query_to_compare:
            match = query_to_compare.order("meeting_start_datetime", desc=True).execute()

            if match.data:
                allowed_keys = {(r["source_table"], r["source_id"]) for r in match.data}

                neighbors = [n for n in sorted_neighbors if (n["source_table"], n["source_id"]) in allowed_keys]

    except Exception as e:
        logger.error("Similarity search failed: %s", e)
        return RelevantMeetingsResponse(meetings=[])
    if not neighbors:
        return RelevantMeetingsResponse(meetings=[])

    # 3) fetch metadata for each neighbor
    # Prepare lists for the filter function
    source_tables = [n["source_table"] for n in neighbors]
    source_ids = [n["source_id"] for n in neighbors]

    rpc_params: dict = {
        "source_tables": source_tables,
        "source_ids": source_ids,
        "max_results": k,
    }

    try:
        rows = (
            supabase.rpc(
                "get_meetings_by_filter",
                rpc_params,
            )
            .execute()
            .data
        )
    except Exception:
        logger.exception("Unexpected error fetching meetings with filter")
        return RelevantMeetingsResponse(meetings=[])

    fetched = {}
    for row in rows:
        fetched[(row["source_table"], row["source_id"])] = row

    # 4) assemble ordered list, injecting similarity
    for n in neighbors:
        key = (n["source_table"], n["source_id"])
        row = fetched.get(key)
        if not row:
            logger.debug("No metadata found for %s %s", *key)
            continue

        # carry over similarity
        row["similarity"] = n.get("similarity")
        try:
            meetings.append(Meeting.model_validate(row))
        except ValidationError as ve:
            logger.warning("Skipping invalid row %s: %s", row.get("source_id"), ve)

    return RelevantMeetingsResponse(meetings=meetings)
