import logging
from typing import Optional
from datetime import datetime, time, timedelta

from openai import OpenAI
from postgrest import SyncSelectRequestBuilder
from pydantic import BaseModel, ValidationError


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

    except Exception as e:
        logger.exception(f"Unexpected error loading profile embedding or profile doesnt exist: {e}")
        return RelevantMeetingsResponse(meetings=[])

    # 2) call `get_top_k_neighbors`
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
            query=profile_embedding_input,
            sources=["meeting_embeddings"],
            allowed_topic_ids=allowed_topic_ids,
            allowed_countries=[],
            start_date = start_date_time,
            end_date = end_date_time,
            k=1000,
        )

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