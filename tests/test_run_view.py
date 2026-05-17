from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.events import Event, EventType
from core.ledger import RunLedger
from core.run_view import RunView, build_run_view, list_run_views
from core.errors import ResumeError


def _write_run_json(run_dir: Path, **fields) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(
        json.dumps({"run_id": run_dir.name, **fields}), encoding="utf-8"
    )


def _write_final_report(run_dir: Path, status: str, **fields) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "final_report.json").write_text(
        json.dumps({"status": status, **fields}), encoding="utf-8"
    )


def _write_ledger_with_initiated(run_dir: Path, workflow_id: str = "coding") -> RunLedger:
    run_dir.mkdir(parents=True, exist_ok=True)
    ledger = RunLedger(repo_root=run_dir.parent.parent, run_dir=run_dir)
    ledger.append_event(
        EventType.RUN_INITIATED,
        payload={"workflow_id": workflow_id, "repo_root": str(run_dir.parent.parent)},
    )
    return ledger


class TestCompletedRun:
    def test_completed_run_view(self, tmp_path: Path) -> None:
        run_dir = tmp_path / ".ai-team" / "runs" / "run-1"
        _write_run_json(run_dir, workflow_id="coding", preset_id="codebase-assistant")
        _write_final_report(run_dir, "completed", task_summary="Fixed auth bug")
        ledger = _write_ledger_with_initiated(run_dir, workflow_id="coding")
        ledger.append_event(
            EventType.RUN_COMPLETED,
            payload={"status": "completed"}
        )

        view = build_run_view(tmp_path, "run-1")
        assert view.run_id == "run-1"
        assert view.status == "completed"
        assert view.summary == "Fixed auth bug"
        assert view.workflow_id == "coding"
        assert view.preset_id == "codebase-assistant"
        assert view.resume_available is True
        assert view.report_path is not None
        assert any("report" in a.lower() for a in view.next_actions)


class TestFailedRun:
    def test_failed_run_view(self, tmp_path: Path) -> None:
        run_dir = tmp_path / ".ai-team" / "runs" / "run-fail"
        _write_run_json(run_dir, workflow_id="coding")
        _write_final_report(run_dir, "failed", task_summary="Auth fix failed")
        ledger = _write_ledger_with_initiated(run_dir, workflow_id="coding")
        ledger.append_event(
            EventType.RUN_FAILED,
            payload={"error_type": "ProviderError", "reason": "401 Unauthorized"}
        )

        view = build_run_view(tmp_path, "run-fail")
        assert view.status == "failed"
        assert view.resume_available is True
        assert any("doctor" in a.lower() for a in view.next_actions)
        assert any("resume" in a.lower() for a in view.next_actions)


class TestBlockedRun:
    def test_blocked_run_view(self, tmp_path: Path) -> None:
        run_dir = tmp_path / ".ai-team" / "runs" / "run-blocked"
        _write_run_json(run_dir, workflow_id="coding")
        _write_final_report(run_dir, "blocked", task_summary="Blocked by risk", remaining_risks=["high risk"])
        ledger = _write_ledger_with_initiated(run_dir, workflow_id="coding")

        view = build_run_view(tmp_path, "run-blocked")
        assert view.status == "blocked"
        assert view.resume_available is True
        assert any("resume" in a.lower() for a in view.next_actions)


class TestMissingReport:
    def test_run_without_final_report(self, tmp_path: Path) -> None:
        run_dir = tmp_path / ".ai-team" / "runs" / "run-noreport"
        _write_run_json(run_dir, workflow_id="coding")
        _write_ledger_with_initiated(run_dir, workflow_id="coding")

        view = build_run_view(tmp_path, "run-noreport")
        assert view.run_id == "run-noreport"
        assert view.status == "running"
        assert view.report_path is None


class TestMissingRun:
    def test_missing_run_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ResumeError, match="not found"):
            build_run_view(tmp_path, "nonexistent-run")


class TestResumableRun:
    def test_resumable_when_ledger_and_workflow_present(self, tmp_path: Path) -> None:
        run_dir = tmp_path / ".ai-team" / "runs" / "run-resume"
        _write_run_json(run_dir, workflow_id="coding")
        _write_final_report(run_dir, "failed")
        _write_ledger_with_initiated(run_dir, workflow_id="coding")

        view = build_run_view(tmp_path, "run-resume")
        assert view.resume_available is True

    def test_not_resumable_without_ledger(self, tmp_path: Path) -> None:
        run_dir = tmp_path / ".ai-team" / "runs" / "run-no-ledger"
        _write_run_json(run_dir, workflow_id="coding")
        _write_final_report(run_dir, "failed")

        view = build_run_view(tmp_path, "run-no-ledger")
        assert view.resume_available is False

    def test_not_resumable_without_workflow_id(self, tmp_path: Path) -> None:
        run_dir = tmp_path / ".ai-team" / "runs" / "run-no-wf"
        _write_run_json(run_dir)
        _write_final_report(run_dir, "failed")
        ledger = RunLedger(repo_root=tmp_path, run_dir=run_dir)
        ledger.append_event(EventType.RUN_INITIATED, payload={})

        view = build_run_view(tmp_path, "run-no-wf")
        assert view.resume_available is False


class TestListRunViews:
    def test_lists_all_runs(self, tmp_path: Path) -> None:
        for name in ("run-a", "run-b"):
            run_dir = tmp_path / ".ai-team" / "runs" / name
            _write_run_json(run_dir, workflow_id="coding")
            _write_final_report(run_dir, "completed")
            _write_ledger_with_initiated(run_dir, workflow_id="coding")

        views = list_run_views(tmp_path)
        ids = {v.run_id for v in views}
        assert ids == {"run-a", "run-b"}

    def test_skips_broken_runs_gracefully(self, tmp_path: Path) -> None:
        run_dir = tmp_path / ".ai-team" / "runs" / "run-broken"
        run_dir.mkdir(parents=True)
        (run_dir / "run.json").write_text("not json", encoding="utf-8")

        views = list_run_views(tmp_path)
        assert len(views) == 1
        assert views[0].run_id == "run-broken"
        assert views[0].status == "unknown"


class TestJsonContract:
    def test_run_view_serializes_to_dict(self, tmp_path: Path) -> None:
        run_dir = tmp_path / ".ai-team" / "runs" / "run-json"
        _write_run_json(run_dir, workflow_id="coding")
        _write_final_report(run_dir, "completed")
        _write_ledger_with_initiated(run_dir, workflow_id="coding")

        view = build_run_view(tmp_path, "run-json")
        data = view.model_dump(mode="json")
        assert isinstance(data, dict)
        assert data["run_id"] == "run-json"
        assert "status" in data
        assert "summary" in data
        assert "workflow_id" in data
        assert "preset_id" in data
        assert "started_at" in data
        assert "completed_at" in data
        assert "report_path" in data
        assert "artifact_dir" in data
        assert "resume_available" in data
        assert "next_actions" in data
        assert isinstance(data["next_actions"], list)
