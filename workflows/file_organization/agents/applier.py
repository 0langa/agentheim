from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from core.json_repair import repair_json_text
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
    def _parse(self, raw_output: str) -> ApplierResult:
        parsed = json.loads(repair_json_text(raw_output))
        if isinstance(parsed, dict):
            moves = parsed.get("moves")
            if isinstance(moves, list):
                normalized_moves: list[dict[str, object]] = []
                for item in moves:
                    if isinstance(item, dict):
                        normalized = dict(item)
                        if "destination" in normalized and "target" not in normalized:
                            normalized["target"] = normalized.pop("destination")
                        status = normalized.pop("status", None)
                        if "success" not in normalized:
                            if isinstance(status, str):
                                normalized["success"] = status.lower() in {"ok", "success", "done", "applied"}
                            elif status is not None:
                                normalized["success"] = bool(status)
                            else:
                                normalized["success"] = False
                        normalized.setdefault("error", "")
                        normalized_moves.append(normalized)
                parsed["moves"] = normalized_moves
        return self.output_schema.model_validate(parsed)

    def build_apply_prompt(self, proposal: ProposerResult, repo_root: str | Path, task_text: str = "") -> str:
        actions = "\n".join(f"- {a.source} -> {a.target}" for a in proposal.actions) or "- none"
        task_section = f"Organization goal:\n{task_text}\n\n" if task_text else ""
        return (
            f"Repository: {repo_root}\n\n"
            f"{task_section}Apply the following approved file moves:\n{actions}\n\n"
            "Confirm each move and report results. "
            "Return only valid JSON matching the required schema. Do not wrap in markdown."
        )
