from __future__ import annotations

from pydantic import BaseModel, Field

from workflows.file_organization.agents.analyzer import AnalyzerResult
from workflows.file_organization.agents.base import BaseAgent


class MoveAction(BaseModel):
    source: str
    target: str
    reason: str


class ProposerResult(BaseModel):
    actions: list[MoveAction] = Field(default_factory=list)
    new_structure_summary: str = ""
    preview: str = ""
    warnings: list[str] = Field(default_factory=list)


class ProposerAgent(BaseAgent[ProposerResult]):
    def build_propose_prompt(self, analysis: AnalyzerResult) -> str:
        files = "\n".join(
            f"- {f.path} (category: {f.category}, confidence: {f.confidence})"
            for f in analysis.files
        )
        return (
            f"Based on the following file analysis:\n{files}\n\n"
            "Propose a new directory structure to organize these files logically. "
            "Each action must map a source file path to a target file path. "
            "Return only valid JSON matching the required schema. Do not wrap in markdown."
        )

    def build_preview_prompt(self, proposal: ProposerResult) -> str:
        actions = "\n".join(f"- {a.source} -> {a.target} ({a.reason})" for a in proposal.actions) or "- none"
        return (
            f"Review the following proposed file moves:\n{actions}\n\n"
            "Generate a human-readable preview of the changes and list any warnings. "
            "Return only valid JSON matching the required schema. Do not wrap in markdown."
        )
