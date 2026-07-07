import json
import os
import threading
from typing import List, Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.models.schemas import Chunk, RetrievedChunk


class VectorStore:
    """
    Thin wrapper around a FAISS flat index + a JSON sidecar for chunk metadata.
    Same pattern as the FAISS + all-MiniLM-L6-v2 setup used in prior projects,
    extended with source_type / date filtering for hybrid retrieval.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self.embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.dim = self.embedder.get_sentence_embedding_dimension()
        self.index: faiss.IndexFlatIP = faiss.IndexFlatIP(self.dim)
        self.meta: List[dict] = []
        self._load()

    def _load(self):
        if os.path.exists(settings.FAISS_INDEX_PATH) and os.path.exists(settings.FAISS_META_PATH):
            self.index = faiss.read_index(settings.FAISS_INDEX_PATH)
            with open(settings.FAISS_META_PATH, "r") as f:
                self.meta = json.load(f)

    def _persist(self):
        os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
        faiss.write_index(self.index, settings.FAISS_INDEX_PATH)
        with open(settings.FAISS_META_PATH, "w") as f:
            json.dump(self.meta, f)

    def _embed(self, texts: List[str]) -> np.ndarray:
        vecs = self.embedder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return vecs.astype("float32")

    def add_chunks(self, chunks: List[Chunk]):
        if not chunks:
            return
        with self._lock:
            vecs = self._embed([c.text for c in chunks])
            self.index.add(vecs)
            for c in chunks:
                self.meta.append(c.model_dump())
            self._persist()

    def search(
        self,
        query: str,
        top_k: int = None,
        source_type_filter: Optional[List[str]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[RetrievedChunk]:
        top_k = top_k or settings.TOP_K
        if self.index.ntotal == 0:
            return []

        with self._lock:
            q_vec = self._embed([query])
            # over-fetch then filter, since FAISS flat index has no native metadata filter
            fetch_k = min(self.index.ntotal, max(top_k * 5, 20))
            scores, idxs = self.index.search(q_vec, fetch_k)

        results = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx == -1:
                continue
            m = self.meta[idx]
            if source_type_filter and m["source_type"] not in source_type_filter:
                continue
            if date_from and m.get("date") and m["date"] < date_from:
                continue
            if date_to and m.get("date") and m["date"] > date_to:
                continue
            results.append(RetrievedChunk(score=float(score), **m))
            if len(results) >= top_k:
                break
        return results

    def stats(self) -> dict:
        by_type = {}
        for m in self.meta:
            by_type[m["source_type"]] = by_type.get(m["source_type"], 0) + 1
        return {"total_chunks": len(self.meta), "by_source_type": by_type}


# module-level singleton so FastAPI routers share one in-memory index
vector_store = VectorStore()
