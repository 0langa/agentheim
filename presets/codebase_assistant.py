from __future__ import annotations

from typing import Any

from presets.base import PRESET_REGISTRY, Preset, Question


class CodebaseAssistantPreset(Preset):
    def __init__(self) -> None:
        super().__init__(
            preset_id="codebase-assistant",
            workflow_id="coding",
            name="Codebase Assistant",
            description="Inspect, plan, patch, test, and report on a codebase.",
            guided_questions=[
                Question(key="task", type="text", text="What task should the assistant perform?"),
                Question(key="repo", type="text", text="Target repository path?", default="."),
                Question(key="mode", type="choice", text="Execution mode?", options=["apply", "auto", "ci"], default="apply"),
                Question(key="allow_dirty", type="confirm", text="Allow running on a dirty repository?", default=False),
            ],
            default_config={"mode": "apply", "allow_dirty": False},
            required_capabilities=["plan", "code_edit", "verify"],
        )

    def run(self, inputs: dict[str, Any]) -> Any:
        from workflows.coding.runtime import run_task
        return run_task(
            task_text=inputs["task"],
            repo_path=inputs.get("repo", "."),
            mode=inputs.get("mode", "apply"),
            allow_dirty=inputs.get("allow_dirty", False),
        )


PRESET_REGISTRY.register(CodebaseAssistantPreset())
