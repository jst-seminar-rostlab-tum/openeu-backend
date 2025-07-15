import os
import tempfile
import requests
from fastapi import HTTPException
from postgrest.exceptions import APIError
from app.core.pdf_extractor import extract_text_from_pdf
from app.core.supabase_client import supabase
import logging
import json
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


def get_or_extract_legislation_text(legislation_id: str) -> tuple[str | None, str | None]:
    """
    Get extracted text and proposal file link for a legislation_id, or extract and store if not present.
    Returns (extracted_text, proposal_link). If not found, both may be None.
    """
    # 1. Check if already present in legislative_procedure_files
    try:
        existing = (
            supabase.table("legislative_procedure_files")
            .select("extracted_text, link")
            .eq("id", legislation_id)
            .execute()
        )
        if existing.data and len(existing.data) > 0:
            return existing.data[0]["extracted_text"], existing.data[0].get("link")
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
            return None, None
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
            return None, None
    except APIError as e:
        logging.error(f"APIError: {e}")
        raise HTTPException(503, "Failed to fetch documents_gateway, try again later") from None
    except Exception as e:
        logging.error(f"Exception: {e}")
        raise HTTPException(500, "Unexpected error during documents_gateway fetch, try again later") from None
    # 3. Download, extract, and store
    extracted_text = _extract_and_store_legislation_text(legislation_id, link)
    return extracted_text, link


def embed_legislation_text_sync(legislation_id: str, extracted_text: str) -> bool:
    """
    Synchronously embeds the extracted text for a legislative file and stores it in the DB.
    Returns True on success, False on failure.
    """
    try:
        eg = EmbeddingGenerator(max_tokens=2000, overlap=200)
        eg.embed_row(
            source_table="legislative_procedure_files",
            row_id=legislation_id,
            content_column="extracted_text",
            content_text=str(extracted_text),
            destination_table="documents_embeddings",
        )
        logging.info(f"[SYNC] Embedding completed for legislation_id={legislation_id}")
        return True
    except Exception as e:
        logging.error(f"[SYNC] Embedding failed for legislation_id={legislation_id}: {e}")
        return False
