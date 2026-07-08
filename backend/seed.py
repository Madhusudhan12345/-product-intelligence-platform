"""
Run once to populate the FAISS index with sample source documents.
Safe to re-run: skips ingestion if the index already has data, so repeated
builds/redeploys (e.g. on Render) don't duplicate chunks.
Usage: python seed.py
"""
import json

from app.models.schemas import SourceDocument
from app.services.ingestion import chunk_document
from app.services.vectorstore import vector_store

stats = vector_store.stats()
if stats["total_chunks"] > 0:
    print(f"Vector store already has {stats['total_chunks']} chunks -- skipping seed.")
    print(stats)
else:
    with open("data/sample_sources.json") as f:
        raw = json.load(f)

    docs = [SourceDocument(**d) for d in raw]
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc))

    vector_store.add_chunks(all_chunks)
    print(f"Ingested {len(all_chunks)} chunks from {len(docs)} source documents.")
    print(vector_store.stats())