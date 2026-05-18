from __future__ import annotations

import json
import re
from pathlib import Path

from typer.testing import CliRunner

from interfaces.cli.cli import app


runner = CliRunner()


def test_root_help_includes_coder_group() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "coder" in result.output


def test_commands_json_includes_coder_family() -> None:
    result = runner.invoke(app, ["commands", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    commands = {item["command"] for section in payload["sections"] for item in section["commands"]}
    assert "coder" in commands
    assert "coder ui" in commands
    assert "coder list" in commands
    assert "coder resume" in commands


def test_coder_ui_help_mentions_workspace() -> None:
    result = runner.invoke(app, ["coder", "ui", "--help"])
    assert result.exit_code == 0
    plain_output = re.sub(r"\x1b\[[0-9;]*m", "", result.output).lower()
    assert "workspace" in plain_output
    assert "coder ui" in plain_output
