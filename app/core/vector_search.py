from app.core.openai_client import EMBED_MODEL, openai
from app.core.supabase_client import supabase
from typing import Optional


def get_top_k_neighbors(query: str, allowed_sources: dict[str, str], k: int = 5) -> list[dict]:
    """
    allowed_sources = {
        "table":"colom"
        "bt_plenarprotokolle":"text"
    }
    """
    embedding = openai.embeddings.create(input=[query], model=EMBED_MODEL).data[0].embedding

    tables = list(allowed_sources.keys())
    cols = list(allowed_sources.values())

    if allowed_sources:
        resp = supabase.rpc(
            "match_filtered",
            {"src_tables": tables, "content_columns": cols, "query_embedding": embedding, "match_count": k},
        ).execute()
    else:
        resp = supabase.rpc("match_default", {"query_embedding": embedding, "match_count": k}).execute()

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
