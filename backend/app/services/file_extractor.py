"""
Extract plain text from uploaded requirement documents.
Supports: PDF, DOCX, TXT, MD
"""
import logging

logger = logging.getLogger(__name__)


def extract_text(filename: str, content: bytes) -> str:
    """
    Extract text from a file based on its extension.
    Returns the raw text content.
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"

    if ext == "pdf":
        return _extract_pdf(content)
    elif ext in ("docx", "doc"):
        return _extract_docx(content)
    elif ext in ("txt", "md", "text"):
        return content.decode("utf-8", errors="replace")
    else:
        raise ValueError(f"Unsupported file type: .{ext}. Use PDF, DOCX, or TXT.")


def _extract_pdf(content: bytes) -> str:
    import io
    import pdfplumber

    text_parts = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text.strip())

    result = "\n\n".join(text_parts)
    if not result.strip():
        raise ValueError("Could not extract text from PDF. The file may be image-based or protected.")
    return result


def _extract_docx(content: bytes) -> str:
    import io
    from docx import Document

    doc = Document(io.BytesIO(content))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    result = "\n".join(paragraphs)
    if not result.strip():
        raise ValueError("Could not extract text from DOCX. The file appears to be empty.")
    return result
