from typing import Optional, Union
import logging

from app.core.openai_client import EMBED_MODEL, openai
from app.core.supabase_client import supabase

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", force=True)
logger = logging.getLogger(__name__)


def get_top_k_neighbors(
    query: Optional[str] = None,
    embedding: Optional[list[float]] = None,
    allowed_sources: Optional[dict[str, str]] = None,
    allowed_topic_ids: Optional[list[str]] = None,
    allowed_countries: Optional[list[str]] = None,
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

    rpc_args: dict[str, Union[list, int]] = {
        "query_embedding": embedding,
        "match_count": k,
    }

    # Determine which RPC to call based on sources
    if sources == ["document_embeddings"]:
        rpc_name = "match_filtered" if tables else "match_default"
        if tables:
            rpc_args.update({"src_tables": tables, "content_columns": cols})

    elif sources == ["meeting_embeddings"]:
        rpc_name = "match_filtered_meetings"
        if tables:
            rpc_args.update({"src_tables": tables, "content_columns": cols})

    else:
        rpc_name = "match_combined_filtered_embeddings"

    logging.info(f"tables: {tables}")
    logging.info(f"tables: {allowed_sources}")
    if tables:
        rpc_args.update({"src_tables": tables, "content_columns": cols})

    if rpc_name == "match_filtered_meetings":
        if allowed_topic_ids is not None:
            rpc_args["allowed_topic_ids"] = allowed_topic_ids
        if allowed_countries is not None:
            rpc_args["allowed_countries"] = allowed_countries

    resp = supabase.rpc(rpc_name, rpc_args).execute()
    logger.info(f"response: {resp}")

    return resp.data


def get_top_k_neighbors_by_embedding(
    vector_embedding: list[float], allowed_sources: dict[str, str], k: int = 5, sources=Optional[list]
) -> list[dict]:
    """
    Fetch the top-k nearest neighbors for a text query or a given embedding.

    Parameters:
    - embedding: pre-computed embedding vector
    - allowed_sources: mapping of table names to column names to filter the search.
    - k: number of neighbors to retrieve.
    - sources: a list indicating which embedding RPC to use:
        * ["document_embeddings"]
        * ["meeting_embeddings"]
        * None or other: combined embeddings

    Returns:
        A list of dicts representing matching records.
    """
    if allowed_sources:
        tables = list(allowed_sources.keys())
        cols = list(allowed_sources.values())

    if sources == ["document_embeddings"]:
        if allowed_sources:
            resp = supabase.rpc(
                "match_filtered",
                {"src_tables": tables, "content_columns": cols, "query_embedding": vector_embedding, "match_count": k},
            ).execute()
        else:
            resp = supabase.rpc("match_default", {"query_embedding": vector_embedding, "match_count": k}).execute()

    if sources == ["meeting_embeddings"]:
        if allowed_sources:
            resp = supabase.rpc(
                "match_filtered_meetings",
                {"src_tables": tables, "content_columns": cols, "query_embedding": vector_embedding, "match_count": k},
            ).execute()
        else:
            resp = supabase.rpc(
                "match_default_meetings", {"query_embedding": vector_embedding, "match_count": k}
            ).execute()

    else:
        if allowed_sources:
            resp = supabase.rpc(
                "match_combined_filtered_embeddings",
                {"src_tables": tables, "content_columns": cols, "query_embedding": vector_embedding, "match_count": k},
            ).execute()
        else:
            resp = supabase.rpc(
                "match_combined_embeddings", {"query_embedding": vector_embedding, "match_count": k}
            ).execute()

    return resp.data
