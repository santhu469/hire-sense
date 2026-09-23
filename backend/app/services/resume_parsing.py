import io

import docx
from pypdf import PdfReader


def extract_text(content: bytes, content_type: str) -> str:
    if content_type == "application/pdf":
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        document = docx.Document(io.BytesIO(content))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    raise ValueError(f"Unsupported content type for text extraction: {content_type}")
