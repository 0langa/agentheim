from __future__ import annotations

from pathlib import Path
from typing import Any

from presets.base import PRESET_REGISTRY, Preset, Question


class GitHubMaintainerPreset(Preset):
    def __init__(self) -> None:
        super().__init__(
            preset_id="github-maintainer",
            workflow_id="github_maintenance",
            name="GitHub Maintainer",
            description="Summarize issues and draft PR descriptions.",
            guided_questions=[
                Question(key="issues_text", type="text", text="Path to issues file or raw issues text?"),
                Question(key="summary_only", type="confirm", text="Summary only (no drafting)?", default=False),
            ],
            default_config={},
            support_state="beta",
            required_capabilities=["summarize", "report"],
        )

    def run(self, inputs: dict[str, Any]) -> Any:
        from workflows.github_maintenance.runtime import run_task
        issues = inputs["issues_text"]
        path = Path(issues)
        if path.exists():
            issues = path.read_text(encoding="utf-8")
        return run_task(issues_text=issues)


PRESET_REGISTRY.register(GitHubMaintainerPreset())
