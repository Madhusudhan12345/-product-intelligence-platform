"""
Run once to populate the FAISS index with sample source documents.
Usage: python seed.py
"""
import json

from app.models.schemas import SourceDocument
from app.services.ingestion import chunk_document
from app.services.vectorstore import vector_store

with open("data/sample_sources.json") as f:
    raw = json.load(f)

docs = [SourceDocument(**d) for d in raw]
all_chunks = []
for doc in docs:
    all_chunks.extend(chunk_document(doc))

vector_store.add_chunks(all_chunks)
print(f"Ingested {len(all_chunks)} chunks from {len(docs)} source documents.")
print(vector_store.stats())
