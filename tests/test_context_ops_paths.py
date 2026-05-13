"""Tests for M6 path migration in AictxContextOps."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentheim.context_ops import CleanResult, ContextPlan, GeneratedContext
from agentheim.context_ops_impl import AictxContextOps


class TestWriteUsesAiTeamRuns:
    def test_write_uses_ai_team_runs(self, tmp_path: Path) -> None:
        ops = AictxContextOps()
        context = GeneratedContext(
            plan=ContextPlan(raw={"selected_files": ["a.py"]}),
            repo_root=tmp_path,
        )

        mock_inventory = MagicMock()
        mock_lock = MagicMock()

        with (
            patch("agentheim.context_ops_impl.scan_repository", return_value=mock_inventory),
            patch("agentheim.context_ops_impl.write_context_scaffold", return_value=[]),
            patch("agentheim.context_ops_impl.build_context_lock", return_value=mock_lock),
            patch("agentheim.context_ops_impl.write_lockfile") as mock_write_lockfile,
            patch("agentheim.vendor.aictx.context.pipeline._build_patch", return_value="patch text"),
            patch("agentheim.vendor.aictx.io.files.safe_write") as mock_safe_write,
        ):
            report = ops.write(tmp_path, context)

        ai_team_runs = tmp_path / ".ai-team" / "runs" / "agentheim-ctx"
        assert ai_team_runs.exists()
        assert (ai_team_runs / "out").exists()
        assert report.lockfile_path.endswith("context.lock.json")
        mock_write_lockfile.assert_called_once()
        mock_safe_write.assert_called_once()


class TestCleanUsesAiTeamRuns:
    def test_clean_uses_ai_team_runs(self, tmp_path: Path) -> None:
        runs_dir = tmp_path / ".ai-team" / "runs"
        run1 = runs_dir / "run1"
        run2 = runs_dir / "run2"
        run1.mkdir(parents=True)
        run2.mkdir(parents=True)
        (run1 / "file.txt").write_text("keep", encoding="utf-8")

        ops = AictxContextOps()
        result = ops.clean(tmp_path, keep_runs=0)

        assert not run1.exists()
        assert not run2.exists()
        assert result.removed_count == 2
        assert sorted(result.removed_paths) == ["run1", "run2"]
        assert result.kept_count == 0

    def test_clean_with_run_id(self, tmp_path: Path) -> None:
        runs_dir = tmp_path / ".ai-team" / "runs"
        run1 = runs_dir / "run1"
        run2 = runs_dir / "run2"
        run1.mkdir(parents=True)
        run2.mkdir(parents=True)

        ops = AictxContextOps()
        result = ops.clean(tmp_path, run_id="run1")

        assert not run1.exists()
        assert run2.exists()
        assert result.removed_count == 1
        assert result.removed_paths == ["run1"]
        assert result.kept_count == 1


class TestCleanIgnoresAictxRuns:
    def test_clean_ignores_aictx_runs(self, tmp_path: Path) -> None:
        aictx_runs = tmp_path / ".aictx" / "runs"
        legacy_run = aictx_runs / "legacy-run"
        legacy_run.mkdir(parents=True)
        (legacy_run / "artifact.json").write_text("{}", encoding="utf-8")

        ai_team_runs = tmp_path / ".ai-team" / "runs"
        ai_run = ai_team_runs / "ai-run"
        ai_run.mkdir(parents=True)

        ops = AictxContextOps()
        result = ops.clean(tmp_path, keep_runs=0)

        assert legacy_run.exists()
        assert not ai_run.exists()
        assert result.removed_count == 1
        assert result.removed_paths == ["ai-run"]
