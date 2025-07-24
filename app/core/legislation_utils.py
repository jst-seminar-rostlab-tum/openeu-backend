import os
import tempfile
import requests
import mimetypes
from fastapi import HTTPException
from postgrest.exceptions import APIError
from app.core.file_extractor import extract_text_from_file
from app.core.supabase_client import supabase
import logging
import json
from scripts.embedding_generator import EmbeddingGenerator
from app.core.chat_utils import get_response
from app.core.table_metadata import get_table_description
from app.core.vector_search import get_top_k_neighbors
from app.core.cohere_client import co
from app.models.chat import ChatMessageItem


def _download_file(url: str) -> str:
    """
    Download a file from the given URL to a temp file. Returns the file path.
    The file extension is inferred from the URL if possible.
    """
    temp_file_path = None
    try:
        # Try to get the extension from the URL
        ext = os.path.splitext(url)[1]
        if not ext:
            # Fallback: try to get extension from content-type header
            response = requests.head(url, timeout=10)
            content_type = response.headers.get('content-type')
            ext = mimetypes.guess_extension(content_type) or '' if content_type else ''
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            temp_file_path = tmp.name
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail=f"Failed to download file: HTTP {response.status_code}")
            tmp.write(response.content)
        return temp_file_path
    except HTTPException as e:
        logging.error(f"HTTPException: {e}")
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(503, "Failed to download file, try again later") from None
    except Exception as e:
        logging.error(f"Exception: {e}")
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(503, "Failed to download file, try again later") from None


def _extract_and_store_legislation_text(legislation_id: str, pdf_url: str) -> str:
    """
    Download the PDF, extract text, and store it in the DB. Returns the extracted text.
    """
    temp_pdf_path = _download_file(pdf_url)
    try:
        extracted_text = extract_text_from_file(temp_pdf_path)
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


def _get_or_extract_legislation_text(legislation_id: str) -> tuple[str | None, str | None]:
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


def _embed_legislation_text_sync(legislation_id: str, extracted_text: str) -> bool:
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


def _build_legislation_context_message(main_message: str, proposal_link: str | None = None) -> str:
    """
    Helper to build a user-facing context message for legislation responses.
    If a proposal_link is provided, appends a markdown link to the message.
    """
    if proposal_link:
        return f"{main_message} You can read the proposal document directly: [Proposal Document]({proposal_link})"
    return main_message


def process_legislation(legislation_request: ChatMessageItem, user_id: str):
    """
    Process a legislative procedure: use RAG if embeddings exist, otherwise extract PDF text and store in DB.
    Returns a streaming LLM response with appropriate context (including errors or missing files).
    Always informs the user.
    """
    try:
        extracted_text, proposal_link = _get_or_extract_legislation_text(legislation_request.legislation_id)
        # 1. Check for existing embeddings for this legislative_id
        emb_response = (
            supabase.table("documents_embeddings")
            .select("*")
            .eq("source_id", legislation_request.legislation_id)
            .limit(1)
            .execute()
        )
        if not (emb_response.data and len(emb_response.data) > 0):
            # Embedding does not exist, extract and embed synchronously
            if not proposal_link or not extracted_text:
                # Fetch the legislative_files DB row
                legislative_row_resp = (
                    supabase.table("legislative_files")
                    .select("*")
                    .eq("id", legislation_request.legislation_id)
                    .execute()
                )
                if legislative_row_resp.data and len(legislative_row_resp.data) > 0:
                    legislative_row = legislative_row_resp.data[0]
                    # Format the row as readable context
                    context_lines = [f"{k}: {v}" for k, v in legislative_row.items() if v is not None]
                    context_text = f"No legislative proposal document was found for this procedure. \
                        However, here is all available information from the database for this legislative procedure: \
                        {'\n'.join(context_lines)} \
                        Further details will be available as soon as the official legislative proposal is published."
                else:
                    context_text = "No legislative proposal document was found for this procedure."
                yield from get_response(
                    legislation_request.message,
                    legislation_request.session_id,
                    user_id,
                    context_text=context_text
                )
                return
            success = _embed_legislation_text_sync(legislation_request.legislation_id, extracted_text)
            if not success:
                context_text = _build_legislation_context_message(
                    "I'm having trouble processing this legislative procedure right now.\
                    Please try again in a few moments.",
                    proposal_link,
                )
                yield from get_response(
                    legislation_request.message,
                    legislation_request.session_id,
                    user_id,
                    context_text=context_text
                )
                return
            # After embedding, check again for embedding (should exist now)
            emb_response = (
                supabase.table("documents_embeddings")
                .select("*")
                .eq("source_id", legislation_request.legislation_id)
                .limit(1)
                .execute()
            )
            if not (emb_response.data and len(emb_response.data) > 0):
                context_text = _build_legislation_context_message(
                    "I'm having trouble processing this legislative procedure right now.\
                    Please try again in a few moments.",
                    proposal_link,
                )
                yield from get_response(
                    legislation_request.message,
                    legislation_request.session_id,
                    user_id,
                    context_text=context_text
                )
                return
        # RAG flow (embedding exists)
        try:
            neighbors = get_top_k_neighbors(
                query=legislation_request.message,
                sources=["document_embeddings"],
                source_id=legislation_request.legislation_id,
                k=35,
            )
            if neighbors and len(neighbors) > 0:
                # Rerank neighbors
                docs = [n["content_text"] for n in neighbors]
                rerank_resp = co.rerank(
                    model="rerank-v3.5",
                    query=legislation_request.message,
                    documents=docs,
                    top_n=min(5, len(docs)),
                )
                neighbors_re = []
                for result in rerank_resp.results:
                    idx = result.index
                    new_score = result.relevance_score
                    neighbors[idx]["similarity"] = new_score
                    if new_score > 0.1:
                        neighbors_re.append(neighbors[idx])
                neighbors = neighbors_re
            if not neighbors or len(neighbors) == 0:
                # fallback logic
                context_text = str(extracted_text)
                yield from get_response(
                    legislation_request.message,
                    legislation_request.session_id,
                    user_id,
                    context_text=context_text
                )
                return
            context_text = ""
            for element in neighbors:
                source_table = element.get("source_table")
                table_desc = get_table_description(source_table) if source_table else "Unspecified data"
                context_text += f"[Source: {table_desc}]\n{element.get('content_text')}\n\n"
            yield from get_response(
                legislation_request.message, legislation_request.session_id, user_id, context_text=context_text
            )
            return
        except Exception as e:
            logging.error(f"RAG/LLM error for legislation_id={legislation_request.legislation_id}: {e}")
            context_text = _build_legislation_context_message(
                "I'm experiencing technical difficulties and can't provide an answer right now.\
                Please try again in a few moments.",
                proposal_link,
            )
            yield from get_response(
                legislation_request.message, legislation_request.session_id, user_id, context_text=context_text
            )
            return
    except APIError as e:
        logging.error(f"Supabase APIError: {e}")
        raise HTTPException(503, "Failed to get legislative file, try again later") from None
    except Exception as e:
        logging.error(f"Unexpected error during legislation processing: {e}")
        raise HTTPException(503, "Failed to get legislative file, try again later") from None
    
    