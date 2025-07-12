from typing import Optional, Any
import logging
from datetime import datetime

from app.core.openai_client import EMBED_MODEL, openai
from app.core.supabase_client import supabase

logger = logging.getLogger(__name__)


def get_top_k_neighbors(
    query: Optional[str] = None,
    embedding: Optional[list[float]] = None,
    allowed_sources: Optional[dict[str, str]] = None,
    allowed_topics: Optional[list[str]] = None,
    allowed_topic_ids: Optional[list[str]] = None,
    allowed_countries: Optional[list[str]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    k: int = 5,
    sources: Optional[list[str]] = None,
) -> list[dict]:
    """
    Fetch the top-k nearest neighbors for a text query or a given embedding.

    Parameters:
    - embedding: pre-computed embedding vector (mutually exclusive with query).
    - query: natural language string to be embedded and matched (mutually exclusive with embedding).
    - allowed_sources: mapping of table names to column names to filter the search.
    - k: number of neighbors to retrieve.
    - sources: a list indicating which embedding RPC to use:
        * ["document_embeddings"]
        * ["meeting_embeddings"]
        * None or other: combined embeddings
    -allowed_topics/allowed countries only viable for meetings

    Returns:
        A list of dicts representing matching records.
    """

    if (query is None and embedding is None) or (query and embedding):
        raise ValueError("Provide exactly one of `query` or `embedding`.")

    # Generate embedding if only query is provided
    if embedding is None:
        assert query is not None
        embedding = openai.embeddings.create(input=query, model=EMBED_MODEL).data[0].embedding

    tables = list(allowed_sources or {})
    cols = list((allowed_sources or {}).values())

    rpc_args: dict[str, Any] = {
        "query_embedding": embedding,
        "match_count": k,
    }

    # Determine which RPC to call based on sources
    if sources == ["document_embeddings"]:
        rpc_name = "match_filtered"

    elif sources == ["meeting_embeddings"] or allowed_topic_ids or allowed_topics or allowed_countries:
        rpc_name = "match_filtered_meetings"
    else:
        rpc_name = "match_combined_filtered_embeddings"

    if tables:
        rpc_args.update({"src_tables": tables, "content_columns": cols})

    logger.info(f"Calling {rpc_name} with: query_embedding={embedding[:5]}, match_count={k}, (len={len(embedding)})")
    if rpc_name == "match_filtered_meetings":
        rpc_args = {
            "query_embedding": embedding,
            "match_count": k,
            **({"src_tables": tables} if tables else {}),
            **({"content_columns": cols} if cols else {}),
            **({"allowed_topics": allowed_topics} if allowed_topics else {}),
            **({"allowed_topic_ids": allowed_topic_ids} if allowed_topic_ids else {}),
            **({"allowed_countries": allowed_countries} if allowed_countries else {}),
            "start_date": str(start_date) if start_date else None,
            "end_date": str(end_date) if end_date else None,
        }
        # Optionally: Only include keys that are not None to avoid passing nulls unnecessarily
        rpc_args = {k: v for k, v in rpc_args.items() if v is not None}

    resp = supabase.rpc(rpc_name, rpc_args).execute()
    logger.info(f"Result: {resp.data}, Error: {getattr(resp, 'error', None)}")

    return resp.data



get_top_k_neighbors(query="digital", allowed_countries=["European Union"])


