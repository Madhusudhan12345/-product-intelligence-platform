from typing import List

from fastapi import APIRouter

from app.models.schemas import IngestResponse, SourceDocument
from app.services.ingestion import chunk_document
from app.services.vectorstore import vector_store

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("", response_model=IngestResponse)
def ingest_documents(documents: List[SourceDocument]):
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))
    vector_store.add_chunks(all_chunks)
    return IngestResponse(
        ingested_chunks=len(all_chunks),
        source_ids=[d.source_id for d in documents],
    )


@router.get("/stats")
def ingest_stats():
    return vector_store.stats()
