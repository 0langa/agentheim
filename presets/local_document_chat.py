from __future__ import annotations

from typing import Any

from presets.base import PRESET_REGISTRY, Preset, Question


class LocalDocumentChatPreset(Preset):
    def __init__(self) -> None:
        super().__init__(
            preset_id="local-document-chat",
            workflow_id="documents",
            name="Local Document Chat",
            description="Index, retrieve, and answer questions about local documents.",
            guided_questions=[
                Question(key="query", type="text", text="What is your question?"),
                Question(key="repo", type="text", text="Repository path containing documents?", default="."),
            ],
            default_config={},
            support_state="stable_candidate",
            required_capabilities=["file_read", "search", "synthesize", "cite"],
            product_tier="recommended",
            recommended_for=["document Q&A", "knowledge base search", "research over local files"],
            estimated_time="1-5 minutes",
            output_kind="answer with citations",
            example_inputs={
                "query": "What does the authentication module do?",
                "repo": ".",
            },
        )

    def run(self, inputs: dict[str, Any]) -> Any:
        from workflows.documents.runtime import run_task
        return run_task(
            query=inputs["query"],
            repo_path=inputs.get("repo", "."),
        )


PRESET_REGISTRY.register(LocalDocumentChatPreset())
