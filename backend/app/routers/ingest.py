import json
from typing import List

from fastapi import APIRouter

from app.models.schemas import IngestResponse, SourceDocument
from app.services.ingestion import chunk_document
from app.services.memory import memory_store
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


@router.get("/admin/reset-and-reseed")
def reset_and_reseed():
    """
    Wipes the vector store + memory, then re-ingests the bundled sample_sources.json.
    Meant for fixing accidental duplicate ingestion on hosts without shell access.
    """
    vector_store.reset()
    memory_store.reset()

    with open("data/sample_sources.json") as f:
        raw = json.load(f)
    docs = [SourceDocument(**d) for d in raw]
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc))
    vector_store.add_chunks(all_chunks)

    return {"status": "reset complete", "reseeded_stats": vector_store.stats()}