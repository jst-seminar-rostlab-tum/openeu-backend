import logging
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, ValidationError
from datetime import datetime

from app.core.config import Settings
from postgrest import SyncSelectRequestBuilder
from app.core.supabase_client import supabase
from app.core.vector_search import get_top_k_neighbors
from app.models.legislative_file import LegislativeFile


class RelevantLegislativeFilesResponse(BaseModel):
    legislative_files: list[LegislativeFile]


settings = Settings()
openai = OpenAI(api_key=settings.get_openai_api_key())
EMBED_MODEL = "text-embedding-ada-002"


logger = logging.getLogger(__name__)


def fetch_relevant_legislative_files(
    user_id: str,
    k: int,
    query_to_compare: Optional[SyncSelectRequestBuilder] = None,
) -> RelevantLegislativeFilesResponse:
    legislative_files: list[LegislativeFile] = []
    # 1) load the stored profile embedding for `user_id`
    try:
        resp = (
            supabase.table("profiles")
            .select("embedding", "countries", "newsletter_frequency")
            .eq("id", user_id)
            .single()
            .execute()
        )
        profile_embedding = resp.data["embedding"]

    except Exception as e:
        logger.exception(f"Unexpected error loading profile embedding or profile doesnt exist: {e}")
        return RelevantLegislativeFilesResponse(legislative_files=[])

    # 2) call `get_top_k_neighbors`
    try:
        neighbors = get_top_k_neighbors(
            embedding=profile_embedding,
            allowed_sources={"legislative_files": "embedding_input"},
            sources=["document_embeddings"],
            k=k,
        )

        if query_to_compare:
            match = query_to_compare.execute()

            if match.data:
                allowed_keys = {r["id"] for r in match.data}

                neighbors = [n for n in neighbors if n["source_id"] in allowed_keys]

    except Exception as e:
        logger.error("Similarity search failed: %s", e)
        return RelevantLegislativeFilesResponse(legislative_files=[])
    if not neighbors:
        return RelevantLegislativeFilesResponse(legislative_files=[])

    # 3) Fetch the actual legislative files based on the neighbors
    # Extract source_ids (these are the legislative file ids)
    source_ids = [n["source_id"] for n in neighbors]

    # Direct query to the legislative_files table
    try:
        response = supabase.table("legislative_files").select("*").in_("id", source_ids).execute()
        rows = response.data
    except Exception as e:
        logger.exception(f"Unexpected error fetching legislative files: {e}")
        return RelevantLegislativeFilesResponse(legislative_files=[])

    # Create a map from id to row for easier access
    fetched = {row["id"]: row for row in rows}

    # 4) assemble ordered list, injecting similarity
    for n in neighbors:
        source_id = n["source_id"]
        row = fetched.get(source_id)
        if not row:
            logger.debug(f"No legislative file found for id {source_id}")
            continue

        # carry over similarity
        row["similarity"] = n.get("similarity")

        # Fix missing required fields
        if "source_table" not in row:
            row["source_table"] = "legislative_files"
        if "source_id" not in row:
            row["source_id"] = row["id"]

        # Fix date format
        if "lastpubdate" in row and isinstance(row["lastpubdate"], str):
            try:
                # Parse the string date format
                parsed_date = datetime.strptime(row["lastpubdate"], "%a %b %d %Y")
                row["lastpubdate"] = parsed_date.date()
            except (ValueError, TypeError):
                # If parsing fails, set to None
                logger.warning(f"Could not parse date: {row['lastpubdate']}")
                row["lastpubdate"] = None

        try:
            legislative_files.append(LegislativeFile.model_validate(row))
        except ValidationError as ve:
            logger.warning(f"Skipping invalid legislative file {source_id}: {ve}")

    return RelevantLegislativeFilesResponse(legislative_files=legislative_files)
