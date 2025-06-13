import logging
from typing import Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from postgrest.exceptions import APIError

from app.core.config import Settings
from app.core.supabase_client import supabase

settings = Settings()
logging.basicConfig(level=logging.INFO)

embedder = OpenAIEmbeddings(model=settings.EMBED_MODEL)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.MAX_TOKENS,
    chunk_overlap=100,
)

META_DELIM = '::META::'

conflict_map = {
    "documents_embeddings": ["source_table", "source_id", "content_text"],
    "meeting_embeddings": ["source_table", "source_id"],
}

class embeddingGenerator:
    
    try:
        response = supabase.table("v_meetings").select("source_table").execute().data
    except Exception as e:
        logging.error(f"Failed to init embeddingGenerator with exception: {e}")
        raise e
    
    
    def embed_row(
        source_table: str, row_id: str, content_column: str, 
        content_text: str, destination_table: Optional[str]
        ) -> None:

        """
        Splits content_text into chunks using LangChain's text splitter, embeds each chunk with metadata
        included in the embedding input (separated by a delimiter), and upserts to Supabase.

        Args:
            source_table: Name of the source table for provenance.
            row_id: Primary key or unique identifier of the source row.
            content_column: Column name where text came from.
            content_text: The full text for embedding.
            metadata: Optional dict of extra metadata to attach to every chunk.
        """
        
        conflicts = conflict_map[destination_table] or []
        destination_table = destination_table or "documents_embeddings"
        
        if source_table in embeddingGenerator.response:
            destination_table = "meeting_embeddings"
        
        base_meta = ""

        if META_DELIM in content_text:
            base_meta, content_text = content_text.split(META_DELIM, 1)


        chunks = text_splitter.split_text(content_text)

        upsert_rows: list[dict] = []
        for chunk in chunks:
            merged_meta = base_meta + chunk
            upsert_rows.append({
                "source_table": source_table,
                "source_id": row_id,
                "content_column": content_column,
                "content_text": merged_meta,
                "embedding": None,
            })

        batch_size = settings.BATCH_SZ
        for i in range(0, len(upsert_rows), batch_size):
            batch = upsert_rows[i : i + batch_size]
            texts_to_embed = [row["content_text"] for row in batch]

            try:
                embeddings = embedder.embed_documents(texts_to_embed)
                for row, emb in zip(batch, embeddings):
                    row["embedding"] = emb
            except Exception as e:
                logging.error(f"Embedding failed on batch {i // batch_size + 1}: {e}")
                continue
            
            try:

                supabase.table("documents_embeddings").upsert(
                    batch,
                    on_conflict=conflicts
                ).execute()

            except APIError as e:
                logging.error(f"Supabase APIError: {e}")
            except Exception as e:
                logging.error(f"Unexpected error during upsert for batch {i // batch_size + 1}: {e}")