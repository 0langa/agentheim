from __future__ import annotations

from typing import Any

from presets.base import PRESET_REGISTRY, Preset, Question


class ResearchReportPreset(Preset):
    def __init__(self) -> None:
        super().__init__(
            preset_id="research-report",
            workflow_id="research",
            name="Research Report",
            description="Gather, summarize, and report on a research topic.",
            guided_questions=[
                Question(key="topic", type="text", text="Research topic?"),
                Question(key="repo", type="text", text="Target repository path?", default="."),
            ],
            default_config={},
            support_state="beta",
            required_capabilities=["web_search", "fetch", "summarize", "report"],
        )

    def run(self, inputs: dict[str, Any]) -> Any:
        from workflows.research.runtime import run_task
        return run_task(topic=inputs["topic"], repo_path=inputs.get("repo", "."))


PRESET_REGISTRY.register(ResearchReportPreset())
