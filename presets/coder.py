from __future__ import annotations

from typing import Any

from presets.base import PRESET_REGISTRY, Preset, Question


class CoderPreset(Preset):
    def __init__(self) -> None:
        super().__init__(
            preset_id="coder",
            workflow_id="coder",
            name="Coder",
            description="Persistent local coding session for any workspace folder.",
            guided_questions=[
                Question(key="task", type="text", text="What should the coder do?"),
                Question(key="repo", type="text", text="Target workspace path?", default="."),
                Question(key="trust_mode", type="choice", text="Trust mode?", options=["read_only", "ask", "workspace"], default="ask"),
            ],
            default_config={"trust_mode": "ask"},
            support_state="stable_candidate",
            required_capabilities=["text", "json"],
            product_tier="recommended",
            recommended_for=["new project scaffolding", "local coding sessions", "editing existing code"],
            estimated_time="ongoing session",
            output_kind="chat + local edits",
            example_inputs={
                "task": "Build a small FastAPI app in this folder",
                "repo": ".",
                "trust_mode": "ask",
            },
        )

    def run(self, inputs: dict[str, Any]) -> Any:
        from workflows.coder.runtime import create_session, post_message

        session = create_session(inputs.get("repo", "."), trust_mode=inputs.get("trust_mode", "ask"))
        if inputs.get("task"):
            return post_message(inputs.get("repo", "."), session.session_id, inputs["task"])
        return session


PRESET_REGISTRY.register(CoderPreset())
