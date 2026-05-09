from pathlib import Path

from ai_team.repo.redaction import is_secret_file, redact_text


def test_redact_text_masks_secret_patterns() -> None:
    text = "API_KEY=supersecret123\npassword: hunter2\nconnection string=Server=tcp;User=me"
    redacted = redact_text(text)
    assert "supersecret123" not in redacted
    assert "hunter2" not in redacted
    assert "Server=tcp" not in redacted


def test_is_secret_file_detects_secret_names() -> None:
    assert is_secret_file(Path(".env"))
    assert is_secret_file(Path("config/secrets.yml"))
    assert not is_secret_file(Path("src/main.py"))