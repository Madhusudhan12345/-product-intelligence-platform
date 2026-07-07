from fastapi import APIRouter

from app.agents.orchestrator import orchestrator
from app.models.schemas import QueryRequest, QueryResponse
from app.services.memory import memory_store

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def run_query(req: QueryRequest):
    return orchestrator.run(
        question=req.question,
        mode=req.mode,
        source_type_filter=req.source_type_filter,
        date_from=req.date_from,
        date_to=req.date_to,
    )


@router.get("/history")
def query_history(limit: int = 20):
    return memory_store.recent_queries(limit=limit)
