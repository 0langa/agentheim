from __future__ import annotations

from pydantic import BaseModel, Field

from core.schemas_runtime import AgentResult
from workflows.docs_maintenance.agents.base import BaseAgent


class AlignmentIssue(BaseModel):
    path: str
    issue: str
    suggestion: str


class AlignmentResult(BaseModel):
    aligned: bool = True
    issues: list[AlignmentIssue] = Field(default_factory=list)


class AlignerAgent(BaseAgent[AlignmentResult]):
    def run_alignment(self, updated_docs_json: str) -> AgentResult:
        prompt = (
            "Check the following updated documentation for consistency with the codebase.\n\n"
            f"{updated_docs_json}\n\n"
            "Return only valid JSON matching the AlignmentResult schema."
        )
        return self.run_structured(prompt, max_output_tokens=1500)
