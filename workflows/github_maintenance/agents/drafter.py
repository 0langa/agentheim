from __future__ import annotations

from pydantic import BaseModel, Field

from core.schemas_runtime import AgentResult
from workflows.github_maintenance.agents.base import BaseAgent


class DraftResult(BaseModel):
    pr_title: str
    pr_body: str
    branch_name: str = Field(default="")


class DrafterAgent(BaseAgent[DraftResult]):
    def run_draft(self, summary_json: str) -> AgentResult:
        prompt = (
            "Draft a pull request title and body based on the following issue summaries.\n\n"
            f"{summary_json}\n\n"
            "Return only valid JSON matching the DraftResult schema."
        )
        return self.run_structured(prompt, max_output_tokens=1500)
