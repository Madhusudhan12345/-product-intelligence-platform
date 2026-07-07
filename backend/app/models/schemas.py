from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SourceDocument(BaseModel):
    source_id: str
    source_type: str  # support_ticket | prd | meeting_note | github_issue | interview | release_note
    title: str
    content: str
    date: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = []


class Chunk(BaseModel):
    chunk_id: str
    source_id: str
    source_type: str
    title: str
    text: str
    date: Optional[str] = None


class RetrievedChunk(Chunk):
    score: float


class QueryRequest(BaseModel):
    question: str
    mode: str = "standard"  # "standard" | "deep_research"
    source_type_filter: Optional[List[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class AgentStep(BaseModel):
    agent: str
    action: str
    detail: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    evidence: List[RetrievedChunk]
    agent_trace: List[AgentStep]
    used_memory: List[str] = []
    latency_ms: float


class IngestResponse(BaseModel):
    ingested_chunks: int
    source_ids: List[str]
