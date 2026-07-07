import re
import time
from typing import List, Optional

from app.agents.analyst_agent import analyst_agent
from app.agents.report_agent import report_agent
from app.agents.retriever_agent import retriever_agent
from app.models.schemas import AgentStep, QueryResponse, RetrievedChunk
from app.services.llm_client import complete
from app.services.memory import memory_store

FOLLOWUP_SYSTEM_PROMPT = """You are a research planning agent. Given an original question and \
the analysis produced so far, decide if there is an important gap in the evidence that a \
follow-up search could fill.

Respond with EXACTLY one line:
- If a follow-up search would help, respond: FOLLOWUP: <short reformulated search query>
- If the evidence is already sufficient, respond: DONE
"""


def _extract_keywords(question: str) -> List[str]:
    stop = {"what", "which", "are", "the", "is", "how", "why", "do", "does", "a", "an", "of", "for", "to", "in"}
    words = re.findall(r"[a-zA-Z]{3,}", question.lower())
    return [w for w in words if w not in stop][:8]


class Orchestrator:
    """
    Sequential + conditional agent chain:
    Retriever -> Analyst -> (deep_research mode: follow-up Retriever -> Analyst, up to 2 hops) -> Report

    Memory is consulted before analysis and updated after, so repeated/related
    questions benefit from previously derived insights.
    """

    def run(self, question: str, mode: str = "standard",
            source_type_filter: Optional[List[str]] = None,
            date_from: Optional[str] = None, date_to: Optional[str] = None) -> QueryResponse:
        start = time.time()
        trace: List[AgentStep] = []

        # 1. Memory lookup
        keywords = _extract_keywords(question)
        prior_insights = memory_store.get_relevant_insights(keywords)
        if prior_insights:
            trace.append(AgentStep(agent="memory", action="recall",
                                    detail=f"found {len(prior_insights)} relevant prior insights"))

        # 2. Initial retrieval
        evidence, step = retriever_agent.retrieve(
            question, source_type_filter=source_type_filter, date_from=date_from, date_to=date_to
        )
        trace.append(step)

        # 3. Initial analysis
        analysis, step = analyst_agent.analyze(question, evidence, prior_insights)
        trace.append(step)

        # 4. Deep research: up to 2 follow-up hops
        all_evidence: List[RetrievedChunk] = list(evidence)
        if mode == "deep_research":
            for hop in range(2):
                decision = complete(
                    FOLLOWUP_SYSTEM_PROMPT,
                    f"Original question: {question}\n\nAnalysis so far:\n{analysis}",
                    max_tokens=100,
                )
                if not decision.strip().startswith("FOLLOWUP:"):
                    trace.append(AgentStep(agent="planner", action="stop_research",
                                            detail=f"hop {hop+1}: evidence deemed sufficient"))
                    break

                followup_query = decision.split("FOLLOWUP:", 1)[1].strip()
                trace.append(AgentStep(agent="planner", action="plan_followup",
                                        detail=f"hop {hop+1}: searching '{followup_query}'"))

                new_evidence, step = retriever_agent.retrieve(
                    followup_query, source_type_filter=source_type_filter,
                    date_from=date_from, date_to=date_to,
                )
                trace.append(step)

                seen_ids = {c.chunk_id for c in all_evidence}
                merged_new = [c for c in new_evidence if c.chunk_id not in seen_ids]
                all_evidence.extend(merged_new)

                analysis, step = analyst_agent.analyze(question, all_evidence, prior_insights)
                trace.append(step)

        # 5. Report formatting
        final_answer, step = report_agent.format_report(question, analysis)
        trace.append(step)

        # 6. Persist to memory
        source_ids = list({c.source_id for c in all_evidence})
        memory_store.log_query(question, final_answer, [s.model_dump() for s in trace], source_ids)
        # store a distilled insight (first ~200 chars of analysis) for future recall
        memory_store.add_insight(analysis[:300], question)

        latency_ms = (time.time() - start) * 1000

        return QueryResponse(
            question=question,
            answer=final_answer,
            evidence=all_evidence,
            agent_trace=trace,
            used_memory=prior_insights,
            latency_ms=round(latency_ms, 1),
        )


orchestrator = Orchestrator()
