from pathlib import Path
import json

import pytest

from ai_team.agents.base import BaseAgent
from ai_team.config import AgentModelConfig, ModelRole
from ai_team.providers.base import ModelProvider, ModelRequest, ModelResponse
from ai_team.schemas import ImplementationPlan


VALID_PLAN = {
    "summary": "Add README usage section.",
    "assumptions": ["README exists."],
    "non_goals": ["No code changes."],
    "detected_repo_type": "python",
    "risks": [{"risk": "Docs drift", "impact": "Low", "mitigation": "Use current context pack."}],
    "task_graph": {
        "ordered_tasks": [
            {
                "id": "task-1",
                "type": "docs",
                "title": "Update README usage section",
                "dependencies": [],
                "acceptance_criteria": [{"description": "README has usage section", "measurable": True}],
                "max_edit_scope": "README section only",
                "expected_verifier_commands": [],
                "work_order": {
                    "id": "wo-1",
                    "title": "README usage",
                    "objective": "Document usage",
                    "relevant_files": ["README.md"],
                    "required_context_excerpts": ["Current README excerpt"],
                    "constraints": ["Keep existing behavior"],
                    "forbidden_changes": ["No code edits"],
                    "acceptance_criteria": [{"description": "Usage documented", "measurable": True}],
                    "expected_commands": [],
                    "max_edit_scope": "README section only"
                }
            }
        ],
        "dependencies": []
    },
    "verification_strategy": ["Manual README review"],
    "estimated_commands": [],
    "files_likely_to_change": ["README.md"],
    "stop_conditions": ["Stop if README missing"]
}


class FakeProvider(ModelProvider):
    def __init__(self, config: AgentModelConfig, outputs: list[str]) -> None:
        super().__init__(config)
        self.outputs = outputs

    def invoke(self, request: ModelRequest) -> ModelResponse:
        content = self.outputs.pop(0)
        return ModelResponse(role=request.role, model=self.config.model, provider=self.config.provider, content=content)


def _config() -> AgentModelConfig:
    return AgentModelConfig(
        role=ModelRole.PLANNER,
        provider="default",
        provider_type="openai_compatible",
        endpoint="https://example",
        api_key="secret",
        model="grok",
    )


def test_base_agent_repairs_invalid_json_once() -> None:
    provider = FakeProvider(_config(), ["not json", json.dumps(VALID_PLAN)])
    agent = BaseAgent(provider=provider, role_config=_config(), system_prompt="system", output_schema=ImplementationPlan)
    result = agent.run_structured("plan")
    assert result.success is True
    assert result.parsed_output is not None


def test_base_agent_fails_after_invalid_repair() -> None:
    provider = FakeProvider(_config(), ["bad", "still bad"])
    agent = BaseAgent(provider=provider, role_config=_config(), system_prompt="system", output_schema=ImplementationPlan)
    result = agent.run_structured("plan")
    assert result.success is False
    assert result.error is not None
