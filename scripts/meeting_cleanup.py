import logging
import multiprocessing
from pydantic import BaseModel

from app.core.supabase_client import supabase
from embedding_generator import EmbeddingGenerator 

logger = logging.getLogger(__name__)


class EmbeddingEntry(BaseModel):
    id: str
    source_table: str
    source_id: str
    content_column: str
    content_text: str
    embedding: str
    created_at: str
    

generator = EmbeddingGenerator()


def get_meetings_without_embedding():
    response = supabase.rpc("get_meetings_without_embeddings").execute()
    meetings = response.data
    
    for meeting in meetings:
        try:
            meeting_from_source = supabase.table(meeting["source_table"]).select("*").eq("id", meeting["source_id"]).single().execute()
            content_text = meeting_from_source["embedding_input"]
        except Exception as e:
            content_text = meeting["title"]
        
        EmbeddingGenerator.embed_row(source_table=meeting["source_table"], row_id=meeting["source_id"], content_column="embedding_input", content_text=content_text, destination_table="meeting_embeddings")
        
        

    