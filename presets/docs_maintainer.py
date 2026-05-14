from __future__ import annotations

from typing import Any

from presets.base import PRESET_REGISTRY, Preset, Question


class DocsMaintainerPreset(Preset):
    def __init__(self) -> None:
        super().__init__(
            preset_id="docs-maintainer",
            workflow_id="docs_maintenance",
            name="Docs Maintainer",
            description="Detect stale documentation and update or align it.",
            guided_questions=[
                Question(key="repo", type="text", text="Target repository path?", default="."),
                Question(key="apply", type="confirm", text="Apply documentation changes?", default=True),
            ],
            default_config={"mode": "apply"},
            support_state="beta",
            required_capabilities=["file_read", "plan", "code_edit"],
        )

    def run(self, inputs: dict[str, Any]) -> Any:
        from workflows.docs_maintenance.runtime import run_task
        mode = "apply" if inputs.get("apply", True) else "plan"
        return run_task(repo_path=inputs.get("repo", "."), mode=mode)


PRESET_REGISTRY.register(DocsMaintainerPreset())
