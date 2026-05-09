import pytest

from ai_team.config import ModelRole, load_team_config, redact_secret
from ai_team.errors import ConfigError


def test_redact_secret() -> None:
    assert redact_secret("abcd") == "****"
    assert redact_secret("abcdefgh") == "ab***gh"


def test_load_team_config_openai_compatible_registry(monkeypatch) -> None:
    monkeypatch.setenv("AI_TEAM_PROVIDER_IDS", "default")
    monkeypatch.setenv("AI_TEAM_PROVIDER_DEFAULT_TYPE", "openai_compatible")
    monkeypatch.setenv("AI_TEAM_PROVIDER_DEFAULT_ENDPOINT", "https://api.example.com/v1")
    monkeypatch.setenv("AI_TEAM_PROVIDER_DEFAULT_API_KEY_ENV", "AI_TEAM_API_KEY")
    monkeypatch.setenv("AI_TEAM_API_KEY", "test-api-key")
    monkeypatch.setenv("AI_TEAM_MODEL_PLANNER_NAME", "gpt-4o")
    monkeypatch.setenv("AI_TEAM_MODEL_EXECUTOR_NAME", "gpt-4o-mini")
    monkeypatch.setenv("AI_TEAM_MODEL_VERIFIER_NAME", "gpt-4.1-mini")

    config = load_team_config()
    by_role = config.by_role()

    assert by_role[ModelRole.PLANNER].model == "gpt-4o"
    assert by_role[ModelRole.EXECUTOR].provider_type == "openai_compatible"
    assert by_role[ModelRole.VERIFIER].endpoint == "https://api.example.com/v1"


def test_load_team_config_grok_as_config_only(monkeypatch) -> None:
    monkeypatch.setenv("AI_TEAM_PROVIDER_IDS", "grok")
    monkeypatch.setenv("AI_TEAM_PROVIDER_GROK_TYPE", "openai_compatible")
    monkeypatch.setenv("AI_TEAM_PROVIDER_GROK_ENDPOINT", "https://grok.example/v1")
    monkeypatch.setenv("AI_TEAM_PROVIDER_GROK_API_KEY_ENV", "GROK_API_KEY")
    monkeypatch.setenv("GROK_API_KEY", "grok-secret")
    monkeypatch.setenv("AI_TEAM_MODEL_PLANNER_PROVIDER", "grok")
    monkeypatch.setenv("AI_TEAM_MODEL_EXECUTOR_PROVIDER", "grok")
    monkeypatch.setenv("AI_TEAM_MODEL_VERIFIER_PROVIDER", "grok")

    config = load_team_config()
    by_role = config.by_role()

    assert by_role[ModelRole.PLANNER].provider == "grok"
    assert by_role[ModelRole.PLANNER].provider_type == "openai_compatible"


def test_missing_api_key_env_var_fails(monkeypatch) -> None:
    monkeypatch.setenv("AI_TEAM_PROVIDER_IDS", "default")
    monkeypatch.setenv("AI_TEAM_PROVIDER_DEFAULT_ENDPOINT", "https://api.example.com/v1")
    monkeypatch.setenv("AI_TEAM_PROVIDER_DEFAULT_API_KEY_ENV", "MISSING_KEY")
    monkeypatch.delenv("MISSING_KEY", raising=False)

    with pytest.raises(ConfigError):
        load_team_config().by_role()


def test_config_dump_redaction(monkeypatch) -> None:
    monkeypatch.setenv("AI_TEAM_PROVIDER_IDS", "default")
    monkeypatch.setenv("AI_TEAM_PROVIDER_DEFAULT_ENDPOINT", "https://api.example.com/v1")
    monkeypatch.setenv("AI_TEAM_PROVIDER_DEFAULT_API_KEY_ENV", "AI_TEAM_API_KEY")
    monkeypatch.setenv("AI_TEAM_API_KEY", "super-secret-key")

    config = load_team_config()
    dumped = config.dump(redacted=True)

    assert dumped["providers"]["default"]["api_key"] != "super-secret-key"
    assert "***" in dumped["providers"]["default"]["api_key"]


def test_legacy_grok_config_includes_default_capabilities(monkeypatch) -> None:
    monkeypatch.delenv("AI_TEAM_PROVIDER_IDS", raising=False)
    monkeypatch.setenv("GROK_ORCHESTRATOR_ENDPOINT", "https://legacy-o.example/v1")
    monkeypatch.setenv("GROK_ORCHESTRATOR_KEY", "legacy-orch-key")
    monkeypatch.setenv("GROK_CODER_ENDPOINT", "https://legacy-c.example/v1")
    monkeypatch.setenv("GROK_CODER_KEY", "legacy-coder-key")
    monkeypatch.setenv("GROK_VERIFIER_ENDPOINT", "https://legacy-v.example/v1")
    monkeypatch.setenv("GROK_VERIFIER_KEY", "legacy-verifier-key")

    config = load_team_config()
    assert "plan" in config.models["planner"].capabilities
    assert "code_edit" in config.models["executor"].capabilities
    assert "verify" in config.models["verifier"].capabilities
