from __future__ import annotations

from pydantic import BaseModel, Field

from core.schemas_runtime import AgentResult
from workflows.github_maintenance.agents.base import BaseAgent


class IssueSummaryItem(BaseModel):
    number: int
    title: str
    summary: str


class SummaryResult(BaseModel):
    issues: list[IssueSummaryItem] = Field(default_factory=list)


class SummarizerAgent(BaseAgent[SummaryResult]):
    def run_summary(self, issues_text: str) -> AgentResult:
        prompt = (
            "Summarize the following GitHub issues. For each issue provide number, title, and a brief summary.\n\n"
            f"{issues_text}\n\n"
            "Return only valid JSON matching the SummaryResult schema."
        )
        return self.run_structured(prompt, max_output_tokens=1500)
