import hashlib
from typing import List

from app.config import settings
from app.models.schemas import Chunk, SourceDocument


def _chunk_text(text: str, size: int, overlap: int) -> List[str]:
    text = text.strip()
    if len(text) <= size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def chunk_document(doc: SourceDocument) -> List[Chunk]:
    raw_chunks = _chunk_text(doc.content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    chunks = []
    for i, text in enumerate(raw_chunks):
        chunk_id = hashlib.sha1(f"{doc.source_id}-{i}".encode()).hexdigest()[:12]
        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                source_id=doc.source_id,
                source_type=doc.source_type,
                title=doc.title,
                text=text,
                date=doc.date,
            )
        )
    return chunks
