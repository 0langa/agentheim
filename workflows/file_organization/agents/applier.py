from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from workflows.file_organization.agents.base import BaseAgent
from workflows.file_organization.agents.proposer import ProposerResult


class AppliedMove(BaseModel):
    source: str
    target: str
    success: bool
    error: str = ""


class ApplierResult(BaseModel):
    moves: list[AppliedMove] = Field(default_factory=list)
    summary: str = ""


class ApplierAgent(BaseAgent[ApplierResult]):
    def build_apply_prompt(self, proposal: ProposerResult, repo_root: str | Path) -> str:
        actions = "\n".join(f"- {a.source} -> {a.target}" for a in proposal.actions) or "- none"
        return (
            f"Repository: {repo_root}\n\n"
            f"Apply the following approved file moves:\n{actions}\n\n"
            "Confirm each move and report results. "
            "Return only valid JSON matching the required schema. Do not wrap in markdown."
        )
