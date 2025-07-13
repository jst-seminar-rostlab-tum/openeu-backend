import os
import tempfile
import requests
from fastapi import HTTPException
from postgrest.exceptions import APIError
from app.core.pdf_extractor import extract_text_from_pdf
from app.core.supabase_client import supabase
import logging
import json
import threading
from scripts.embedding_generator import EmbeddingGenerator


def _download_pdf(url: str) -> str:
    """Download the PDF from the given URL to a temp file. Returns the file path."""
    temp_pdf_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            temp_pdf_path = tmp.name
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail=f"Failed to download PDF: HTTP {response.status_code}")
            tmp.write(response.content)
        return temp_pdf_path
    except HTTPException as e:
        logging.error(f"HTTPException: {e}")
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        raise HTTPException(503, "Failed to download PDF, try again later") from None
    except Exception as e:
        logging.error(f"Exception: {e}")
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        raise HTTPException(503, "Failed to download PDF, try again later") from None


def _extract_and_store_legislation_text(legislation_id: str, pdf_url: str) -> str:
    """
    Download the PDF, extract text, and store it in the DB. Returns the extracted text.
    """
    temp_pdf_path = _download_pdf(pdf_url)
    try:
        extracted_text = extract_text_from_pdf(temp_pdf_path)
    except Exception:
        raise HTTPException(500, "Failed to extract text from PDF, try again later") from None
    finally:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
    try:
        supabase.table("legislative_procedure_files").upsert(
            {
                "id": legislation_id,
                "link": pdf_url,
                "extracted_text": str(extracted_text),
            }
        ).execute()
    except APIError as e:
        logging.error(f"APIError: {e}")
        raise HTTPException(503, "Failed to store extracted text in DB, try again later") from None
    except Exception as e:
        logging.error(f"Exception: {e}")
        raise HTTPException(500, "Unexpected error during DB upsert, try again later") from None
    return extracted_text


def get_or_extract_legislation_text(legislation_id: str) -> str:
    """
    Get extracted text for a legislation_id, or extract and store if not present.
    """
    # 1. Check if already present in legislative_procedure_files
    try:
        existing = (
            supabase.table("legislative_procedure_files").select("extracted_text").eq("id", legislation_id).execute()
        )
        if existing.data and len(existing.data) > 0:
            return existing.data[0]["extracted_text"]
    except APIError as e:
        logging.error(f"APIError: {e}")
        raise HTTPException(503, "DB lookup failed, try again later") from None
    except Exception as e:
        logging.error(f"Exception: {e}")
        raise HTTPException(500, "Unexpected error during DB lookup, try again later") from None
    # 2. Get the link from legislative_files from documentation_gateway
    try:
        result = supabase.table("legislative_files").select("documentation_gateway").eq("id", legislation_id).execute()
        if not result.data or len(result.data) == 0:
            raise HTTPException(404, f"No documentation_gateway found for legislation_id '{legislation_id}'")
        documentation_gateway = result.data[0].get("documentation_gateway")
        link = None
        if documentation_gateway:
            try:
                docs = (
                    documentation_gateway
                    if isinstance(documentation_gateway, list)
                    else json.loads(documentation_gateway)
                )
                for doc in docs:
                    if (
                        doc.get("document_type") == "Legislative proposal"
                        and doc.get("reference")
                        and doc["reference"].get("link")
                    ):
                        link = doc["reference"]["link"]
                        break
            except Exception as e:
                logging.error(f"Failed to parse documentation_gateway: {e}")
                link = None
        if not link:
            return ""
    except APIError as e:
        logging.error(f"APIError: {e}")
        raise HTTPException(503, "Failed to fetch documents_gateway, try again later") from None
    except Exception as e:
        logging.error(f"Exception: {e}")
        raise HTTPException(500, "Unexpected error during documents_gateway fetch, try again later") from None
    # 3. Download, extract, and store
    return _extract_and_store_legislation_text(legislation_id, link)


def trigger_legislation_embedding_async(legislation_id: str, extracted_text: str):
    """
    Triggers async embedding for a legislative file after extraction.
    Meant to be called from the API layer using FastAPI BackgroundTasks.
    """
    def embed():
        try:
            eg = EmbeddingGenerator(max_tokens=2000, overlap=200)
            eg.embed_row(
                source_table="legislative_procedure_files",
                row_id=legislation_id,
                content_column="extracted_text",
                content_text=str(extracted_text),
                destination_table="documents_embeddings",
            )
            logging.info(f"Embedding completed for legislation_id={legislation_id}")
        except Exception as e:
            logging.error(f"Embedding failed for legislation_id={legislation_id}: {e}")

    # Run in a background thread (non-blocking)
    thread = threading.Thread(target=embed)
    thread.start()


##########################
# TESTING - DELETE LATER #
##########################
if __name__ == "__main__":
    legislation_id = "2025/0039(COD)"
    print(f"Extracting and embedding for legislation_id: {legislation_id}")
    text = get_or_extract_legislation_text(legislation_id)
    if text is None:
        print("No 'Legislative proposal' document found for this procedure.")
    print("Text extracted. Running embedding synchronously...")
    
    eg = EmbeddingGenerator(max_tokens=2000, overlap=200)
    eg.embed_row(
        source_table="legislative_procedure_files",
        row_id=legislation_id,
        content_column="extracted_text",
        content_text=str(text),
        destination_table="documents_embeddings",
    )
    print("Embedding complete.")
