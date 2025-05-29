import logging
from typing import List

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


def fetch_all_embeddings() -> List[EmbeddingEntry]:
    """
    Fetch all embedding records from the database.
    Returns a list entries.
    """
    response = supabase.table(EMBEDDING_TABLE_NAME).select("*").execute()
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


def clean_up_embeddings() -> None:
    """
    Fetches all embeddings and deletes any whose source
    record no longer exists.
    """
    embeddings = fetch_all_embeddings()
    logger.info(f"Fetched {len(embeddings)} embedding entries.")

    for entry in embeddings:
        source_table = entry.source_table
        source_id = entry.source_id
        row_id = entry.id

        if not record_exists(source_table, source_id):
            logger.info(f"Deleting embedding for missing record {source_table}/{source_id}")
            delete_embedding(row_id)


if __name__ == "__main__":
    clean_up_embeddings()
