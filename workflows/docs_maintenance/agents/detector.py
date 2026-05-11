from __future__ import annotations

from pydantic import BaseModel, Field

from core.schemas_runtime import AgentResult
from workflows.docs_maintenance.agents.base import BaseAgent


class StaleDocItem(BaseModel):
    path: str
    reason: str


class DetectionResult(BaseModel):
    stale_docs: list[StaleDocItem] = Field(default_factory=list)


class DetectorAgent(BaseAgent[DetectionResult]):
    def run_detection(self, docs_context: str) -> AgentResult:
        prompt = (
            "Review the following documentation files and identify stale or outdated docs.\n\n"
            f"{docs_context}\n\n"
            "Return only valid JSON matching the DetectionResult schema."
        )
        return self.run_structured(prompt, max_output_tokens=1500)
