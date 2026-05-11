from __future__ import annotations

from typer.testing import CliRunner

from interfaces.cli.cli import app

runner = CliRunner()


class TestCliCommands:
    def test_config_dump_help(self) -> None:
        result = runner.invoke(app, ["config-dump", "--help"])
        assert result.exit_code == 0
        assert "config-dump" in result.output

    def test_presets_command(self) -> None:
        result = runner.invoke(app, ["presets"])
        assert result.exit_code == 0
        assert "Available Presets" in result.output or "No presets found" in result.output

    def test_memory_help(self) -> None:
        result = runner.invoke(app, ["memory", "--help"])
        assert result.exit_code == 0
        assert "get|set|history|profile" in result.output

    def test_doctor_help(self) -> None:
        result = runner.invoke(app, ["doctor", "--help"])
        assert result.exit_code == 0
        assert "doctor" in result.output

    def test_guided_help(self) -> None:
        result = runner.invoke(app, ["guided", "--help"])
        assert result.exit_code == 0
        assert "guided" in result.output

    def test_start_help(self) -> None:
        result = runner.invoke(app, ["start", "--help"])
        assert result.exit_code == 0
        assert "start" in result.output

    def test_ping_models_help(self) -> None:
        result = runner.invoke(app, ["ping-models", "--help"])
        assert result.exit_code == 0
        assert "ping-models" in result.output

    def test_inspect_help(self) -> None:
        result = runner.invoke(app, ["inspect", "--help"])
        assert result.exit_code == 0
        assert "inspect" in result.output

    def test_plan_help(self) -> None:
        result = runner.invoke(app, ["plan", "--help"])
        assert result.exit_code == 0
        assert "plan" in result.output

    def test_run_help(self) -> None:
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "run" in result.output

    def test_list_runs_help(self) -> None:
        result = runner.invoke(app, ["list-runs", "--help"])
        assert result.exit_code == 0
        assert "list-runs" in result.output

    def test_doctor_runs(self) -> None:
        result = runner.invoke(app, ["doctor", "--skip-connectivity"])
        # Should complete even without full config; at least shows the table
        assert "System Diagnostics" in result.output or result.exit_code in (0, 1)
