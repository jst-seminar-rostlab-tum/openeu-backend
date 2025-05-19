from openai import OpenAI

from app.core.config import Settings
from app.core.supabase_client import supabase

setting = Settings()
openai = OpenAI(api_key=setting.get_openai_api_key())

EMBED_MODEL = "text-embedding-ada-002"
EMBED_DIM = 1536


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

    resp = supabase.rpc(
        "match_filtered", 
        {
            "src_tables": tables, "content_columns": cols,
            "query_embedding": embedding, "match_count": k
        }
    ).execute()

    return resp.data
