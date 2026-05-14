from __future__ import annotations

from typing import Any

from presets.base import PRESET_REGISTRY, Preset, Question


class FileOrganizerPreset(Preset):
    def __init__(self) -> None:
        super().__init__(
            preset_id="file-organizer",
            workflow_id="file_organization",
            name="File Organizer",
            description="Analyze, propose, preview, and apply file organization changes.",
            guided_questions=[
                Question(key="goal", type="text", text="What organization goal? (e.g., organize downloads by year)"),
                Question(key="target_dir", type="text", text="Target directory?", default="."),
                Question(key="dry_run", type="confirm", text="Run in dry-run mode?", default=True),
            ],
            default_config={"dry_run": True},
            support_state="beta",
            required_capabilities=["file_read", "plan"],
        )

    def run(self, inputs: dict[str, Any]) -> Any:
        from workflows.file_organization.runtime import run_task
        return run_task(
            task_text=inputs["goal"],
            repo_path=inputs.get("target_dir", "."),
            dry_run=inputs.get("dry_run", True),
        )


PRESET_REGISTRY.register(FileOrganizerPreset())
