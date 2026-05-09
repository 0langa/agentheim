import pytest

from ai_team.config import load_team_config
from ai_team.core.model_registry import ModelRegistry


def _seed_env(monkeypatch) -> None:
    monkeypatch.setenv("AI_TEAM_PROVIDER_IDS", "default")
    monkeypatch.setenv("AI_TEAM_PROVIDER_DEFAULT_TYPE", "openai_compatible")
    monkeypatch.setenv("AI_TEAM_PROVIDER_DEFAULT_ENDPOINT", "https://api.example.com/v1")
    monkeypatch.setenv("AI_TEAM_PROVIDER_DEFAULT_API_KEY_ENV", "AI_TEAM_API_KEY")
    monkeypatch.setenv("AI_TEAM_API_KEY", "secret")


def test_registry_resolves_workflow_roles(monkeypatch) -> None:
    _seed_env(monkeypatch)
    config = load_team_config()
    registry = ModelRegistry.from_team_config(config)

    planner = registry.resolve_model("planner", "plan")
    executor = registry.resolve_model("executor", "code_edit")
    verifier = registry.resolve_model("verifier", "verify")

    assert planner.role == "planner"
    assert executor.role == "executor"
    assert verifier.role == "verifier"


def test_registry_rejects_unknown_capability(monkeypatch) -> None:
    _seed_env(monkeypatch)
    config = load_team_config()
    registry = ModelRegistry.from_team_config(config)

    with pytest.raises(ValueError):
        registry.resolve_model("executor", "verify")
