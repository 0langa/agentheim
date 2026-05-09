import json

from ai_team.repo.command_detect import detect_commands


def test_detect_commands_for_node_and_python(tmp_path) -> None:
    (tmp_path / "package.json").write_text(json.dumps({"scripts": {"build": "tsc", "test": "vitest"}}), encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_demo.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")

    commands = detect_commands(tmp_path, {path.relative_to(tmp_path) for path in tmp_path.rglob("*") if path.is_file()})
    names = {command.name for command in commands}

    assert "npm-build:." in names
    assert "npm-test:." in names
    assert "npm-install:." in names
    assert "pytest:." in names