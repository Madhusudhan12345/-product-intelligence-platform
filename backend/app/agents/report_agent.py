from app.models.schemas import AgentStep
from app.services.llm_client import complete

REPORT_SYSTEM_PROMPT = """You are a Report Generation agent. You take a raw analyst finding \
and reformat it into a polished, executive-ready response.

Rules:
1. Preserve every chunk_id citation from the input -- never drop evidence.
2. Structure the output based on the type of question:
   - Direct factual questions -> short direct answer, 2-4 sentences, with citations.
   - "Which X..." / "What are the top..." -> bulleted list ranked by evidence strength.
   - Executive summary requests -> sections: Key Findings / Risks / Opportunities / \
Recommendations.
3. Do not add new facts. Only reformat and clarify what the analyst already found.
4. Keep it tight -- executives don't read walls of text.
"""


class ReportAgent:
    def format_report(self, question: str, analyst_output: str) -> tuple[str, AgentStep]:
        user_prompt = f"Original question: {question}\n\nAnalyst findings:\n{analyst_output}\n\n" \
                      f"Reformat this into the appropriate structure."
        formatted = complete(REPORT_SYSTEM_PROMPT, user_prompt, max_tokens=1500)
        step = AgentStep(agent="report", action="format_output", detail="reformatted analyst findings for delivery")
        return formatted, step


report_agent = ReportAgent()
