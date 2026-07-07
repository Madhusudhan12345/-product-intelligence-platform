from typing import List

from app.models.schemas import AgentStep, RetrievedChunk
from app.services.llm_client import complete

ANALYST_SYSTEM_PROMPT = """You are a Product & Business Analyst agent inside an autonomous \
product intelligence platform. You are given a question and a set of evidence chunks pulled \
from support tickets, PRDs, meeting notes, GitHub issues, release notes, and customer interviews.

Rules:
1. Base your analysis ONLY on the provided evidence chunks. Do not invent facts.
2. Every claim you make must be traceable to at least one chunk. Reference chunks by their \
[chunk_id] inline, e.g. "Users report login failures after SSO rollout [a1b2c3d4e5f6]."
3. If the evidence is insufficient to answer confidently, say so explicitly rather than guessing.
4. Identify patterns and trends across MULTIPLE sources when possible, not just single mentions.
5. If prior relevant insights are supplied, incorporate them but re-verify against the current \
evidence rather than blindly trusting them.
6. Be concise, structured, and analytical -- write like a sharp product analyst briefing an exec, \
not like a chatbot.
"""


class AnalystAgent:
    def analyze(
        self, question: str, evidence: List[RetrievedChunk], prior_insights: List[str] = None
    ) -> tuple[str, AgentStep]:
        prior_insights = prior_insights or []

        evidence_block = "\n\n".join(
            f"[{c.chunk_id}] (source: {c.source_type}, title: {c.title}, date: {c.date})\n{c.text}"
            for c in evidence
        )
        memory_block = (
            "\n".join(f"- {i}" for i in prior_insights)
            if prior_insights
            else "(no relevant prior insights found)"
        )

        user_prompt = f"""Question: {question}

Relevant prior insights from memory:
{memory_block}

Evidence chunks:
{evidence_block}

Analyze the evidence and answer the question. Cite chunk_ids for every claim."""

        answer = complete(ANALYST_SYSTEM_PROMPT, user_prompt, max_tokens=1500)

        step = AgentStep(
            agent="analyst",
            action="analyze_evidence",
            detail=f"analyzed {len(evidence)} chunks + {len(prior_insights)} prior insights",
        )
        return answer, step


analyst_agent = AnalystAgent()
