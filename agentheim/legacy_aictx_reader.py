from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LegacyAictxReader:
    """Read old AICtx run artifacts from `.aictx/runs/` directories.

    M6 migrated transient storage to `.ai-team/runs/`. This reader
    provides backward compatibility for old runs.
    """

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)
        self.runs_dir = self.repo_root / ".aictx" / "runs"

    def list_runs(self) -> list[dict[str, Any]]:
        """List all runs in the legacy `.aictx/runs/` directory.

        Returns list of dicts with keys: run_id, created_at (from dir mtime), path.
        """
        if not self.runs_dir.exists():
            return []

        runs: list[dict[str, Any]] = []
        for path in self.runs_dir.iterdir():
            if path.is_dir():
                stat = path.stat()
                runs.append(
                    {
                        "run_id": path.name,
                        "created_at": stat.st_mtime,
                        "path": path,
                    }
                )

        runs.sort(key=lambda r: r["created_at"], reverse=True)
        return runs

    def _read_json(self, path: Path) -> dict[str, Any] | None:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def read_run_report(self, run_id: str) -> dict[str, Any] | None:
        """Read `run-report.json` from a legacy run directory."""
        return self._read_json(self.runs_dir / run_id / "run-report.json")

    def read_lockfile(self, run_id: str) -> dict[str, Any] | None:
        """Read `context.lock.json` from a legacy run's output directory."""
        return self._read_json(
            self.runs_dir / run_id / "out" / "docs" / "AIprojectcontext" / "context.lock.json"
        )

    def read_plan(self, run_id: str) -> dict[str, Any] | None:
        """Read `context-plan.json` from a legacy run directory."""
        return self._read_json(self.runs_dir / run_id / "context-plan.json")

    def read_inventory(self, run_id: str) -> dict[str, Any] | None:
        """Read `inventory.json` from a legacy run directory."""
        return self._read_json(self.runs_dir / run_id / "inventory.json")
