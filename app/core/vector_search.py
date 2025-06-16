from app.core.openai_client import EMBED_MODEL, openai
from app.core.supabase_client import supabase
from typing import Optional,Union




def get_top_k_neighbors(
    query: Optional[str] = None,
    embedding: Optional[list[float]] = None,
    allowed_sources: dict[str, str] = None,
    k: int = 5,
    sources: Optional[list[str]] = None,
) -> list[dict]:
    """
    Fetch the top-k nearest neighbors for a text query or a given embedding.

    Parameters:
    - query: natural language string to be embedded and matched (mutually exclusive with embedding).
    - embedding: pre-computed embedding vector (mutually exclusive with query).
    - allowed_sources: mapping of table names to column names to filter the search.
    - k: number of neighbors to retrieve.
    - sources: a list indicating which embedding RPC to use:
        * ["document_embeddings"]
        * ["meeting_embeddings"]
        * None or other: combined embeddings

    Returns:
        A list of dicts representing matching records.
    """
    if (query is None and embedding is None) or (query and embedding):
        raise ValueError("Provide exactly one of `query` or `embedding`.")

    # Generate embedding if only query is provided
    if embedding is None:
        embedding = openai.embeddings.create(input=[query], model=EMBED_MODEL).data[0].embedding

    tables = list(allowed_sources or {})
    cols = list((allowed_sources or {}).values())

    # Determine which RPC to call based on sources
    if sources == ["document_embeddings"]:
        rpc_name = "match_filtered" if tables else "match_default"
        
    elif sources == ["meeting_embeddings"]:
        rpc_name = "match_filtered_meetings" if tables else "match_default_meetings"
        
    else:
        rpc_name = (
            "match_combined_filtered_embeddings" if tables else "match_combined_embeddings"
        )

    rpc_args: dict[str, Union[list, int]] = {
        "query_embedding": embedding,
        "match_count": k,
    }

    if tables:
        rpc_args.update({"src_tables": tables, "content_columns": cols})

    resp = supabase.rpc(rpc_name, rpc_args).execute()
    return resp.data


def get_top_k_neighbors_by_embedding(
    vector_embedding: list[float], allowed_sources: dict[str, str], k: int = 5, sources = Optional[list]
) -> list[dict]:
    """
    allowed_sources = {
        "table": "column",
        "bt_plenarprotokolle": "text"
    }
    sources = [
        "document_embeddings", "meeting_embeddings"
    ]
    vector_embedding: list of floats representing the embedding
    """
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
            resp = supabase.rpc("match_default_meetings", {"query_embedding": vector_embedding, "match_count": k}).execute()
    
    else:
        if allowed_sources:
            resp = supabase.rpc(
                "match_combined_filtered_embeddings",
                {"src_tables": tables, "content_columns": cols, "query_embedding": vector_embedding, "match_count": k},
            ).execute()
        else:
            resp = supabase.rpc("match_combined_embeddings", {"query_embedding": vector_embedding, "match_count": k}).execute()
    
    return resp.data
