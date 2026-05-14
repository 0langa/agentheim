from __future__ import annotations

from typing import Any

from presets.base import PRESET_REGISTRY, Preset, Question


class CommandAssistantPreset(Preset):
    def __init__(self) -> None:
        super().__init__(
            preset_id="command-assistant",
            workflow_id="command_assistant",
            name="Command Assistant",
            description="Parse intent and generate safe shell commands.",
            guided_questions=[
                Question(key="command_description", type="text", text="What do you want to do?"),
                Question(key="explain_only", type="confirm", text="Show explanation only (do not run)?", default=False),
            ],
            default_config={},
            support_state="stable_candidate",
            required_capabilities=["plan", "code_edit"],
        )

    def run(self, inputs: dict[str, Any]) -> Any:
        from workflows.command_assistant.runtime import run_task
        return run_task(user_input=inputs["command_description"])


PRESET_REGISTRY.register(CommandAssistantPreset())
