import logging
from typing import Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from postgrest.exceptions import APIError

from app.core.config import Settings
from app.core.openai_client import BATCH_SZ, EMBED_MODEL, MAX_TOKENS, openai
from app.core.supabase_client import supabase


class EmbeddingGenerator:
    def __init__(self, max_tokens: int = MAX_TOKENS, overlap: int = 100):
        try:
            response = supabase.rpc("get_meeting_tables").execute().data
            self.known_meeting_sources = [row["source_table"] for row in response]

        except Exception as e:
            logging.error(f"Failed to init EmbeddingGenerator with exception: {e}")
            raise e

        self.settings = Settings()

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_tokens,
            chunk_overlap=overlap,
        )

        self.META_DELIM = "::META::"

        self.conflict_map = {
            "documents_embeddings": "source_table, source_id, content_text",
            "meeting_embeddings": "source_table, source_id",
        }

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        resp = openai.embeddings.create(model=EMBED_MODEL, input=texts)
        return [d.embedding for d in resp.data]

    def embed_row(
        self,
        source_table: str,
        row_id: str,
        content_column: str,
        content_text: str,
        destination_table: Optional[str] = None,
    ) -> None:
        """
        Splits content_text using LangChain, embeds each chunk with optional metadata,
        and writes the results to Supabase.

        Args:
            source_table: Origin table name.
            row_id: Unique identifier from source.
            content_column: Column name of the original content.
            content_text: Text to embed.
            destination_table: Optional override for where to store embeddings.
        """

        if self.META_DELIM in content_text:
            base_meta, content_text = content_text.split(self.META_DELIM, 1)
        else:
            base_meta = ""

        if not destination_table:
            destination_table = (
                "meeting_embeddings" if source_table in self.known_meeting_sources else "documents_embeddings"
            )

        conflicts = self.conflict_map.get(destination_table, "")

        chunks = self.text_splitter.split_text(content_text)

        chunks = [chunks[0]] if destination_table == "meeting_embeddings" else chunks
        upsert_rows: list[dict] = []

        for chunk in chunks:
            full_text = base_meta + chunk
            upsert_rows.append(
                {
                    "source_table": source_table,
                    "source_id": row_id,
                    "content_column": content_column,
                    "content_text": full_text,
                    "embedding": None,
                }
            )

        logging.info(f"Embedding {source_table}")

        for i in range(0, len(upsert_rows), BATCH_SZ):
            batch = upsert_rows[i : i + BATCH_SZ]
            texts = [r["content_text"] for r in batch]

            try:
                vectors = self.embed_batch(texts)
                for rec, vec in zip(batch, vectors):
                    rec["embedding"] = vec
            except Exception as e:
                logging.error(f"Embedding failed on batch {i // BATCH_SZ + 1}: {e}")
                continue

            try:
                supabase.table(destination_table).upsert(batch, on_conflict=conflicts).execute()
            except APIError as e:
                logging.error(f"Supabase APIError: {e}")
            except Exception as e:
                logging.error(f"Unexpected error during upsert for batch {i // BATCH_SZ + 1}: {e}")
