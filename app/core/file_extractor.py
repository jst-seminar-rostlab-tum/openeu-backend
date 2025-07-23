from langchain_community.document_loaders import PyPDFLoader
from docx import Document
import os


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text from a PDF file using PyMuPDF.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: The extracted text from the PDF.
    Raises:
        Exception: If extraction fails.
    """
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        return "\n".join([doc.page_content for doc in docs])
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF '{pdf_path}': {e}") from e


def extract_text_from_docx(docx_path: str) -> str:
    """
    Extracts all text from a DOCX file.

    Args:
        docx_path (str): Path to the DOCX file.

    Returns:
        str: The extracted text from the DOCX.
    Raises:
        Exception: If extraction fails.
    """
    try:
        doc = Document(docx_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX '{docx_path}': {e}") from e


def extract_text_from_file(file_path: str) -> str:
    """
    Extracts text from a file (PDF or DOCX) based on its extension.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: The extracted text.
    Raises:
        Exception: If extraction fails or file type is unsupported.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise Exception(f"Unsupported file type: {ext}")
