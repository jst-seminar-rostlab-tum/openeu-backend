import logging
from typing import Dict, List

import tiktoken
from openai import OpenAI
from postgrest.exceptions import APIError

from app.core.config import Settings
from app.core.supabase_client import supabase

settings = Settings()
logging.basicConfig(level=logging.INFO)

openai = OpenAI(api_key=settings.get_openai_api_key())

EMBED_MODEL = "text-embedding-ada-002"
EMBED_DIM = 1536
MAX_TOKENS = 500  
BATCH_SZ = 100 


def chunk_text(text: str, max_tokens: int = MAX_TOKENS) -> List[str]:
    enc = tiktoken.encoding_for_model(EMBED_MODEL)
    tokens = enc.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_toks = tokens[i : i + max_tokens]
        chunks.append(enc.decode(chunk_toks))
    return chunks


def embed_batch(texts: List[str]) -> List[List[float]]:
    resp = openai.embeddings.create(model="text-embedding-ada-002", input=texts)
    data = resp.data
    embs = [d.embedding for d in data]
    return embs


def embed(source_table: str, id_column: str, text_column: str) -> None:
    """
    Generates and stores OpenAI embeddings for text rows from a given table.

    - Skips rows already embedded (based on source_id and column).
    - Loads all rows from `source_table`, extracts text from `text_column`.
    - Chunks text, batches requests to OpenAI, embeds, and upserts results.
    - Writes to `documents_embeddings` with unique (source_table, source_id, content_text).

    Args:
        source_table (str): Name of the source table (e.g. 'bt_documents').
        id_column (str): Primary key column in the source table.
        text_column (str): Column containing text to embed.

    Returns:
        None. Writes results directly to Supabase.

    Logs and skips errors; continues with next batch.
    """
    # 1) load all existing source_ids in embeddings table
    existing_resp = (
        supabase.table("documents_embeddings")
        .select({"source_id,content_column"})
        .eq("source_table", source_table)
        .execute()
    )

    existing = {(item["source_id"], item["content_column"]) for item in existing_resp.data}

    # 2) load all rows from the source table
    raw_resp = supabase.table(source_table).select(f"{id_column}, {text_column}").execute()

    raw_rows = raw_resp.data or []

    to_process = []
    for row in raw_rows:
        source_id = row.get(id_column)
        text = row.get(text_column)
        if ((source_id, text_column) not in existing) and text:
            to_process.append({"source_id": source_id, "text": text})


    upsert_rows: List[Dict] = []
    for item in to_process:
        chunks = chunk_text(item["text"])
        for chunk in chunks:
            upsert_rows.append(
                {
                    "source_table": source_table,
                    "source_id": item["source_id"],
                    "content_column": text_column,
                    "content_text": chunk,
                    "embedding": None,
                }
            )

    for i in range(0, len(upsert_rows), BATCH_SZ):
        batch = upsert_rows[i : i + BATCH_SZ]
        texts = [r["content_text"] for r in batch]
        try:
            vectors = embed_batch(texts)
            for rec, vec in zip(batch, vectors):
                rec["embedding"] = vec

        except Exception as e:
            logging.error(f"Embedding failed on batch {i // BATCH_SZ + 1}: {e}")
            continue

        try:
            (
                supabase.table("documents_embeddings")
                .upsert(batch, on_conflict="source_table, source_id, content_text")
                .execute()
            )
        except APIError as e:
            logging.error(f"Supabase APIError: {e}")
        except Exception as e:
            logging.error(f"Unexpected error during upsert for {i // BATCH_SZ + 1}: {e}: {e}")
