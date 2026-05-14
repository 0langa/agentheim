from __future__ import annotations

import json

from pydantic import BaseModel, Field

from core.json_repair import repair_json_text
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
    def _parse(self, raw_output: str) -> ProposerResult:
        parsed = json.loads(repair_json_text(raw_output))
        if isinstance(parsed, dict):
            if "moves" in parsed and "actions" not in parsed:
                parsed["actions"] = parsed.pop("moves")
            actions = parsed.get("actions")
            if isinstance(actions, list):
                normalized_actions: list[dict[str, object]] = []
                for item in actions:
                    if isinstance(item, dict):
                        normalized = dict(item)
                        if "destination" in normalized and "target" not in normalized:
                            normalized["target"] = normalized.pop("destination")
                        normalized.setdefault("reason", "")
                        normalized_actions.append(normalized)
                parsed["actions"] = normalized_actions
            if "summary" in parsed and "new_structure_summary" not in parsed:
                parsed["new_structure_summary"] = parsed.pop("summary")
        return self.output_schema.model_validate(parsed)

    def build_propose_prompt(self, analysis: AnalyzerResult, task_text: str = "") -> str:
        files = "\n".join(
            f"- {f.path} (category: {f.category}, confidence: {f.confidence})"
            for f in analysis.files
        )
        task_section = f"Organization goal:\n{task_text}\n\n" if task_text else ""
        return (
            f"{task_section}Based on the following file analysis:\n{files}\n\n"
            "Propose a new directory structure to organize these files logically. "
            "Each action must map a source file path to a target file path. "
            "Return only valid JSON matching the required schema. Do not wrap in markdown."
        )

    def build_preview_prompt(self, proposal: ProposerResult, task_text: str = "") -> str:
        actions = "\n".join(f"- {a.source} -> {a.target} ({a.reason})" for a in proposal.actions) or "- none"
        task_section = f"Organization goal:\n{task_text}\n\n" if task_text else ""
        return (
            f"{task_section}Review the following proposed file moves:\n{actions}\n\n"
            "Generate a human-readable preview of the changes and list any warnings. "
            "Return only valid JSON matching the required schema. Do not wrap in markdown."
        )
