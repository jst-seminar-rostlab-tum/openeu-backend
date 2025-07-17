import logging
import multiprocessing
from pydantic import BaseModel

from app.core.supabase_client import supabase

logger = logging.getLogger(__name__)


class EmbeddingEntry(BaseModel):
    id: str
    source_table: str
    source_id: str
    content_column: str
    content_text: str
    embedding: str
    created_at: str


EMBEDDING_TABLE_NAME = "documents_embeddings"
BATCH_SIZE = 500


def fetch_embeddings_batch(offset: int) -> list[EmbeddingEntry]:
    """
    Fetch a batch of embedding records from the database.
    """
    response = supabase.table(EMBEDDING_TABLE_NAME).select("*").range(offset, offset + BATCH_SIZE - 1).execute()
    data = response.data
    return [EmbeddingEntry(**entry) for entry in data]


def record_exists(table: str, id_: str) -> bool:
    """
    Check if a record with the given id exists in the specified table.
    """
    try:
        response = supabase.table(table).select("id").eq("id", id_).limit(1).execute()
        exists = bool(response.data and len(response.data) > 0)
        return exists
    except Exception as e:
        logger.error(f"Error checking existence of {table}/{id_}: {e}")
        return False


def delete_embedding(row_id: str) -> None:
    """
    Delete the embedding entry with the given id.
    """
    try:
        supabase.table(EMBEDDING_TABLE_NAME).delete().eq("id", row_id).execute()
        logger.info(f"Deleted embedding with id={row_id}")
    except Exception as e:
        logger.error(f"Error deleting embedding with id={row_id}: {e}")


def embedding_cleanup(stop_event: multiprocessing.synchronize.Event) -> None:
    """
    Fetches all embeddings in batches and deletes any whose source
    record no longer exists.
    """
    offset = 0
    total_processed = 0

    while True:
        if stop_event.is_set():
            logger.error("Embedding cleanup stopped by stop event.")
            break

        batch = fetch_embeddings_batch(offset)
        if not batch:
            break

        for entry in batch:
            source_table = entry.source_table
            source_id = entry.source_id
            row_id = entry.id

            if not record_exists(source_table, source_id):
                logger.info(f"Deleting embedding for missing record {source_table}/{source_id}")
                delete_embedding(row_id)

        total_processed += len(batch)
        offset += BATCH_SIZE

    logger.info(f"Completed embedding cleanup. Total processed: {total_processed}")


if __name__ == "__main__":
    embedding_cleanup(stop_event=multiprocessing.Event())
