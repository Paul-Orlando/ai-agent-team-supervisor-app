import pdfplumber
from pathlib import Path


def extract_text(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    if not text.strip():
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if len(chunk) >= 50:          # skip tiny trailing fragments
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def load_pdf_chunks(pdf_path: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    text = extract_text(pdf_path)
    return chunk_text(text, chunk_size, overlap)
