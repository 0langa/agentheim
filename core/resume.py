"""Resume support — list runs, load reports, and orchestrate resume from interruption.

The ``ResumeOrchestrator`` is the high-level entry point for resuming a workflow.
It replays the ledger, reconstructs ``prior`` results, and delegates the remainder
of execution to a ``WorkflowRunner``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.errors import ResumeError
from core.ledger import RunLedger
from core.replay_engine import ReplayEngine
from core.workflow_runner import WorkflowRunner
from workflows.base import Workflow


def list_runs(repo_root: str | Path) -> list[str]:
    """List run directory names under ``.ai-team/runs/``."""
    runs_dir = Path(repo_root) / ".ai-team" / "runs"
    if not runs_dir.exists():
        return []
    return sorted(item.name for item in runs_dir.iterdir() if item.is_dir())


def load_run(repo_root: str | Path, run_id: str) -> dict:
    """Load ``run.json`` for a given run."""
    run_dir = Path(repo_root) / ".ai-team" / "runs" / run_id
    run_json = run_dir / "run.json"
    if not run_json.exists():
        raise ResumeError(f"Run '{run_id}' not found.")
    return json.loads(run_json.read_text(encoding="utf-8"))


def load_final_report(repo_root: str | Path, run_id: str) -> dict:
    """Load ``final_report.json`` for a given run."""
    run_dir = Path(repo_root) / ".ai-team" / "runs" / run_id
    report_file = run_dir / "final_report.json"
    if not report_file.exists():
        raise ResumeError(f"Final report missing for run '{run_id}'.")
    return json.loads(report_file.read_text(encoding="utf-8"))


class ResumeOrchestrator:
    """Orchestrates resuming an interrupted workflow run.

    Usage::

        orchestrator = ResumeOrchestrator(repo_root)
        results = orchestrator.resume(run_id, workflow, runner)
    """

    def __init__(self, repo_root: str | Path) -> None:
        self.repo_root = Path(repo_root)

    def resume(
        self,
        run_id: str,
        workflow: Workflow,
        runner: WorkflowRunner,
        metadata: dict[str, Any] | None = None,
    ) -> list[Any]:
        """Resume *workflow* from the checkpoint saved in *run_id*.

        Steps:
        1. Validate the run directory exists.
        2. Attach the existing ledger to the workflow.
        3. Delegate to ``WorkflowRunner.run(..., resume_from=run_id)``.
        """
        run_dir = self.repo_root / ".ai-team" / "runs" / run_id
        if not run_dir.exists():
            raise ResumeError(f"Run '{run_id}' not found in {self.repo_root}.")

        # Attach existing ledger to workflow so runner can append events
        ledger = RunLedger(repo_root=self.repo_root, run_dir=run_dir)
        workflow.ledger = ledger

        return runner.run(
            workflow,
            repo_root=self.repo_root,
            metadata=metadata,
            resume_from=run_id,
        )
