from langchain_community.document_loaders import PyPDFLoader


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


if __name__ == "__main__":
    with open("app/core/DEV.txt", "w") as f:
        f.write(extract_text_from_pdf("app/core/TEST_PDF.pdf"))
