from __future__ import annotations

from pydantic import BaseModel, Field

from core.schemas_runtime import AgentResult
from workflows.docs_maintenance.agents.base import BaseAgent


class DocUpdate(BaseModel):
    path: str
    new_content: str


class UpdateResult(BaseModel):
    updates: list[DocUpdate] = Field(default_factory=list)


class UpdaterAgent(BaseAgent[UpdateResult]):
    def run_update(self, stale_docs_json: str) -> AgentResult:
        prompt = (
            "Given the following stale documentation findings, produce updated content for each file.\n\n"
            f"{stale_docs_json}\n\n"
            "Return only valid JSON matching the UpdateResult schema."
        )
        return self.run_structured(prompt, max_output_tokens=2500)
