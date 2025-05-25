import logging
from typing import Dict, List

import tiktoken
from openai import OpenAI
from postgrest.exceptions import APIError

from app.core.config import Settings
from app.core.supabase_client import supabase
from app.core.openai_client import (openai,EMBED_MODEL, MAX_TOKENS,BATCH_SZ)

settings = Settings()
logging.basicConfig(level=logging.INFO)





def chunk_text(text: str, max_tokens: int = MAX_TOKENS) -> List[str]:
    enc = tiktoken.encoding_for_model(EMBED_MODEL)
    tokens = enc.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_toks = tokens[i : i + max_tokens]
        chunks.append(enc.decode(chunk_toks))
    return chunks


def embed_batch(texts: List[str]) -> List[List[float]]:
    resp = openai.embeddings.create(model=EMBED_MODEL, input=texts)
    data = resp.data
    embs = [d.embedding for d in data]
    return embs


def embed_row(source_table: str, row_id: str, content_column: str, content_text: str) -> None:
    """
    Generates and stores OpenAI embeddings for content_text in the doucments_embedding table

    - Chunks text, batches requests to OpenAI, embeds, and upserts results.
    - Writes to `documents_embeddings` with unique (source_table, source_id, content_text).

    Args:
        source_table (str): Name of the source table (e.g. 'bt_documents').
        row_id (str): Primary key column in the source table.
        content_column (str): Column containing text to embed.
        content_text   (str): Content to generate embedding for

    Returns:
        None. Writes results directly to Supabase.

    Logs and skips errors; continues with next batch.
    """

    upsert_rows: List[Dict] = []

    chunks = chunk_text(content_text)
    for chunk in chunks:
        upsert_rows.append(
            {
                "source_table": source_table,
                "source_id": row_id,
                "content_column": content_column,
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
