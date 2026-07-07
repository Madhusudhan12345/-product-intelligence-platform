from typing import List, Optional

from app.models.schemas import AgentStep, RetrievedChunk
from app.services.vectorstore import vector_store


class RetrieverAgent:
    """
    Hybrid retrieval: vector similarity search over FAISS, with optional
    source_type / date filters layered on top. Also supports 'follow-up'
    retrieval for deep-research mode, where it re-queries with a
    reformulated sub-question.
    """

    def retrieve(
        self,
        query: str,
        top_k: int = 6,
        source_type_filter: Optional[List[str]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> tuple[List[RetrievedChunk], AgentStep]:
        results = vector_store.search(
            query,
            top_k=top_k,
            source_type_filter=source_type_filter,
            date_from=date_from,
            date_to=date_to,
        )
        step = AgentStep(
            agent="retriever",
            action="vector_search",
            detail=f"query='{query}' -> {len(results)} chunks "
                   f"(filter={source_type_filter or 'none'})",
        )
        return results, step


retriever_agent = RetrieverAgent()
