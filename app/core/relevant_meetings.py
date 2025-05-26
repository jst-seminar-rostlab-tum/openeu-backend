import logging
from collections import defaultdict
from typing import List

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from app.core.config import Settings
from app.core.supabase_client import supabase
from app.core.vector_search import get_top_k_neighbors_by_embedding
from app.models.meeting import Meeting


class RelevantMeetingsResponse(BaseModel):
    meetings: list[Meeting]


settings = Settings()
openai = OpenAI(api_key=settings.get_openai_api_key())
EMBED_MODEL = "text-embedding-ada-002"


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def fetch_relevant_meetings(user_id: str, k: int) -> RelevantMeetingsResponse:
    meetings: List[Meeting] = []
    # 1) load the stored profile embedding for `user_id`
    try:
        resp = supabase.table("profiles").select("embedding").eq("id", user_id).single().execute()
        profile_embedding = resp.data["embedding"]
    except supabase.errors.SupabaseError as db_err:
        logger.error("Failed to fetch embedding for user %s: %s", user_id, db_err)
        # no embedding ⇒ no neighbors ⇒ empty response
        return RelevantMeetingsResponse(meetings=[])
    except Exception:
        logger.exception("Unexpected error loading profile embedding")
        return RelevantMeetingsResponse(meetings=[])

    # 2) call `get_top_k_neighbors_by_embedding`
    try:
        neighbors = get_top_k_neighbors_by_embedding(
            vector_embedding=profile_embedding,
            allowed_sources={
                "ep_meetings": "title",
                "mep_meetings": "title",
                "ipex_events": "title",
                "austrian_parliament_meetings": "title",
            },
            k=k,
        )
    except Exception as e:
        logger.error("Similarity search failed: %s", e)
        return RelevantMeetingsResponse(meetings=[])
    if not neighbors:
        return RelevantMeetingsResponse(meetings=[])

    # 3) fetch metadata for each neighbor
    ids_by_source = defaultdict(list)
    for n in neighbors:
        ids_by_source[n["source_table"]].append(n["source_id"])

    fetched = {}
    base_query = supabase.table("v_meetings").select("*")
    for source_table, id_list in ids_by_source.items():
        try:
            rows = base_query.eq("source_table", source_table).in_("source_id", id_list).execute().data
        except supabase.errors.SupabaseError as partial_db_err:
            logger.warning("Failed to fetch rows for %s: %s", source_table, partial_db_err)
            continue
        except Exception:
            logger.exception("Unexpected error fetching %s", source_table)
            continue

        for row in rows:
            fetched[(source_table, row["source_id"])] = row

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
