from app.core.openai_client import EMBED_MODEL, openai
from app.core.supabase_client import supabase


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
    vector_embedding: list[float], allowed_sources: dict[str, str], k: int = 5
) -> list[dict]:
    """
    allowed_sources = {
        "table": "column",
        "bt_plenarprotokolle": "text"
    }
    vector_embedding: list of floats representing the embedding
    """
    tables = list(allowed_sources.keys())
    cols = list(allowed_sources.values())

    if allowed_sources:
        resp = supabase.rpc(
            "match_filtered",
            {"src_tables": tables, "content_columns": cols, "query_embedding": vector_embedding, "match_count": k},
        ).execute()
    else:
        resp = supabase.rpc("match_default", {"query_embedding": vector_embedding, "match_count": k}).execute()

    return resp.data
