import pytest

from ai_team.json_repair import extract_json_object, repair_json_text


def test_extract_json_object_from_wrapped_text() -> None:
    raw = "plan follows\n{\"ok\": true}\nthanks"
    assert extract_json_object(raw) == '{"ok": true}'


def test_repair_json_text_fails_without_json() -> None:
    with pytest.raises(ValueError):
        repair_json_text("no json here")