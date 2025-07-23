import logging
import time

from app.core.supabase_client import supabase
from scripts.embedding_generator import EmbeddingGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

generator = EmbeddingGenerator()


def embedd_missing_entries():
    """
    Fetch meetings without embeddings and attempt to generate embeddings
    with up to 3 retries per meeting before giving up.
    """
    try:
        response = supabase.rpc("get_meetings_without_embeddings").execute()
        meetings = response.data or []
        logger.info(f"Fetched {len(meetings)} meetings without embeddings.")
    except Exception:
        logger.exception("Failed to fetch meetings without embeddings.")
        return

    for meeting in meetings:
        meeting_id = meeting.get("source_id")
        source_table = meeting.get("source_table")

        for attempt in range(1, 4):  # Try up to 3 times
            try:
                # Fetch source content
                src_resp = supabase.table(source_table).select("*").eq("id", meeting_id).single().execute()
                content_text = src_resp.data.get("embedding_input") or meeting.get("title")

                # Generate and store embedding
                generator.embed_row(
                    source_table=source_table,
                    row_id=meeting_id,
                    content_column="embedding_input",
                    content_text=content_text,
                    destination_table="meeting_embeddings",
                )

                logger.info(
                    f"Successfully embedded meeting id={meeting_id} "
                    f"from table='{source_table}' on attempt {attempt}."
                )
                break  # Exit retry loop on success

            except Exception:
                logger.exception(f"Attempt {attempt} failed for meeting id={meeting_id} from table='{source_table}'.")
                if attempt < 3:
                    wait_time = attempt * 2
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Giving up on meeting id={meeting_id} from table='{source_table}' after 3 attempts.")


if __name__ == "__main__":
    embedd_missing_entries()
