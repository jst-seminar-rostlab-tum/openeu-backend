from typing import Optional, Union
import logging

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
        rpc_name = "match_filtered"

    elif sources == ["meeting_embeddings"] or allowed_topic_ids or allowed_topics or allowed_countries:
        rpc_name = "match_filtered_meetings"

    else:
        rpc_name = "match_combined_filtered_embeddings"

    if tables:
        rpc_args.update({"src_tables": tables, "content_columns": cols})

    if rpc_name == "match_filtered_meetings":
        if allowed_topics is not None and allowed_topics != []:
            rpc_args["allowed_topics"] = allowed_topics
        if allowed_countries is not None and allowed_countries != []:
            rpc_args["allowed_countries"] = allowed_countries
        if allowed_topic_ids is not None and allowed_topic_ids != []:
            rpc_args["allowed_topic_ids"] = allowed_topic_ids

    resp = supabase.rpc(rpc_name, rpc_args).execute()
    logger.info(f"Result: {resp.data}, Error: {getattr(resp, 'error', None)}")

    return resp.data

def get_top_k_neighbors_by_embedding(
    vector_embedding: list[float], allowed_sources: Optional[dict[str, str]] = None, k: int = 5, sources: Optional[list] = None
) -> list[dict]:
    """
    Fetch the top-k nearest neighbors for a pre-computed embedding.

    Parameters:
    - vector_embedding: pre-computed embedding vector
    - allowed_sources: mapping of table names to column names to filter the search.
    - k: number of neighbors to retrieve.
    - sources: a list indicating which embedding RPC to use:
        * ["document_embeddings"]
        * ["meeting_embeddings"]
        * None or other: combined embeddings

    Returns:
        A list of dicts representing matching records.
    """
    tables = []
    cols = []
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

    elif sources == ["meeting_embeddings"]:
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
                {"src_tables": tables, "query_embedding": vector_embedding, "match_count": k},
            ).execute()
        else:
            resp = supabase.rpc(
                "match_combined_embeddings", {"query_embedding": vector_embedding, "match_count": k}
            ).execute()

    return resp.data

