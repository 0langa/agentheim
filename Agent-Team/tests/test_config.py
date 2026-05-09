from ai_team.config import ModelRole, load_team_config, redact_secret


def _clear_model_env(monkeypatch) -> None:
    for name in [
        "GROK_ORCHESTRATOR_ENDPOINT",
        "GROK_ORCHESTRATOR_KEY",
        "GROK_ORCHESTRATOR_MODEL",
        "GROK_CODER_ENDPOINT",
        "GROK_CODER_KEY",
        "GROK_CODER_MODEL",
        "GROK_VERIFIER_ENDPOINT",
        "GROK_VERIFIER_KEY",
        "GROK_VERIFIER_MODEL",
        "AZURE_GROK_ENDPOINT",
        "AZURE_GROK_KEY",
        "AZURE_GROK_MODEL",
        "GROK_REASONER_ENDPOINT",
        "GROK_REASONER_KEY",
        "GROK_REASONER_MODEL",
        "GROK_VERIFY_ENDPOINT",
        "GROK_VERIFY_KEY",
        "GROK_VERIFY_MODEL",
    ]:
        monkeypatch.delenv(name, raising=False)


def test_redact_secret() -> None:
    assert redact_secret("abcd") == "****"
    assert redact_secret("abcdefgh") == "ab***gh"


def test_load_team_config(monkeypatch) -> None:
    _clear_model_env(monkeypatch)
    monkeypatch.setenv("GROK_ORCHESTRATOR_ENDPOINT", "https://o.example")
    monkeypatch.setenv("GROK_ORCHESTRATOR_KEY", "orch-key")
    monkeypatch.setenv("GROK_CODER_ENDPOINT", "https://c.example")
    monkeypatch.setenv("GROK_CODER_KEY", "coder-key")
    monkeypatch.setenv("GROK_VERIFIER_ENDPOINT", "https://v.example")
    monkeypatch.setenv("GROK_VERIFIER_KEY", "verifier-key")

    config = load_team_config()

    assert config.orchestrator.role is ModelRole.ORCHESTRATOR
    assert config.orchestrator.model == "grok-4-20-reasoning"
    assert config.coder.model == "grok-4-1-fast-reasoning"
    assert config.verifier.model == "grok-4-20-non-reasoning"


def test_load_team_config_supports_legacy_aliases(monkeypatch) -> None:
    _clear_model_env(monkeypatch)
    monkeypatch.setenv("AZURE_GROK_ENDPOINT", "https://o.example")
    monkeypatch.setenv("AZURE_GROK_KEY", "orch-key")
    monkeypatch.setenv("AZURE_GROK_MODEL", "grok-4-20-reasoning")
    monkeypatch.setenv("GROK_CODER_ENDPOINT", "https://c.example")
    monkeypatch.setenv("GROK_CODER_KEY", "coder-key")
    monkeypatch.setenv("GROK_REASONER_ENDPOINT", "https://or.example")
    monkeypatch.setenv("GROK_REASONER_KEY", "reasoner-key")
    monkeypatch.setenv("GROK_VERIFY_ENDPOINT", "https://v.example")
    monkeypatch.setenv("GROK_VERIFY_KEY", "verify-key")

    config = load_team_config()

    assert config.orchestrator.endpoint == "https://o.example"
    assert config.coder.endpoint == "https://c.example"
    assert config.verifier.endpoint == "https://v.example"
