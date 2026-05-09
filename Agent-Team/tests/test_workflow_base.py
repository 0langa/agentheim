from pathlib import Path

from ai_team.config import AgentModelConfig, ModelRole
from ai_team.providers.base import ModelProvider, ModelRequest, ModelResponse
from ai_team.schemas import ImplementationPlan
from ai_team.workflows.base import AgentSpec, build_agent


class DummyProvider(ModelProvider):
    def invoke(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(role=request.role, model=self.config.model, provider=self.config.provider, content="{}")


class DummyModel:
    def __init__(self, config: AgentModelConfig) -> None:
        self.config = config


class DummyRegistry:
    def __init__(self, config: AgentModelConfig) -> None:
        self._model = DummyModel(config)

    def resolve_model(self, role: str, required_capability: str):
        return self._model

    def create_provider(self, config: AgentModelConfig):
        return DummyProvider(config)


def test_build_agent_uses_registry_provider_signature(tmp_path: Path) -> None:
    prompt = tmp_path / "system.md"
    prompt.write_text("system prompt", encoding="utf-8")
    config = AgentModelConfig(
        role=ModelRole.PLANNER,
        provider="default",
        provider_type="openai_compatible",
        endpoint="https://api.example.com/v1",
        api_key="secret",
        model="planner-model",
    )
    registry = DummyRegistry(config)
    spec = AgentSpec(role="planner", capability="plan", prompt_path=prompt)

    agent = build_agent(registry=registry, spec=spec, output_schema=ImplementationPlan)
    assert agent.role_config.model == "planner-model"
