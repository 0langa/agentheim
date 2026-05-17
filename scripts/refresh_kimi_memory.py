#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MEMORY_PATH = ROOT / ".kimi" / "memory.jsonl"


@dataclass(frozen=True)
class MemoryEntity:
    name: str
    entity_type: str
    observations: list[str]

    def to_record(self) -> dict[str, Any]:
        return {
            "type": "entity",
            "name": self.name,
            "entityType": self.entity_type,
            "observations": self.observations,
        }


def _run_pytest_count(repo_root: Path) -> tuple[str, str]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    summary = ""
    for line in reversed(result.stdout.splitlines()):
        if "test" in line.lower() and "collected" in line.lower():
            summary = line.strip()
            break
    if not summary:
        summary = "pytest collection summary unavailable"
    return summary, result.stdout


def _git_summary(repo_root: Path) -> tuple[str, str]:
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip() or "unknown"
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    tree = "clean working tree" if not status else f"dirty working tree ({len(status.splitlines())} paths)"
    return branch, tree


def _phase_status(repo_root: Path) -> list[str]:
    cli_file = repo_root / "interfaces" / "cli" / "product_commands.py"
    observations = [
        "Phase 1.1 COMPLETE: shared readiness service exists at interfaces/readiness.py",
        "Phase 1.2 COMPLETE: shared preset catalog exists at presets/catalog.py",
        "Phase 1.3 COMPLETE: shared RunView service exists at core/run_view.py",
        "Phase 1.4 COMPLETE: shared ErrorCatalog exists at core/error_catalog.py",
    ]
    if cli_file.exists():
        observations.append("Phase 2.1 COMPLETE: beginner setup command exists at interfaces/cli/product_commands.py")
        observations.append("Phase 2.1: setup registered under Getting Started help panel in interfaces/cli/cli.py")
        observations.append("Phase 2.1: setup supports provider/template/model/endpoint/api-key/profile/local/yes/json/dry-run flags")
        observations.append("Phase 2.1: setup binds planner, executor, verifier, context, and beginner preset roles automatically")
    else:
        observations.append("Phase 2.1 pending: beginner setup command not detected")
    return observations


def build_memory_records(repo_root: Path) -> list[dict[str, Any]]:
    branch, tree = _git_summary(repo_root)
    collected_summary, _ = _run_pytest_count(repo_root)
    records = [
        MemoryEntity(
            name="Agentheim Project",
            entity_type="Project",
            observations=[
                "Local-first, preset-driven AI automation platform version 0.1.0",
                "Python 3.12+ target, uses Pydantic v2, Typer, Rich, FastAPI",
                f"Repository at {repo_root}, branch {branch}, {tree}",
                f"Current test collection summary: {collected_summary}",
                "Cross-agent memory file is .kimi/memory.jsonl and is maintainer-only scaffolding",
                "AGENTS.md exists at root with architecture rules, product standards, coding conventions, and risk areas",
            ],
        ).to_record(),
        MemoryEntity(
            name="Agentheim V1 Roadmap",
            entity_type="Roadmap",
            observations=_phase_status(repo_root),
        ).to_record(),
        {
            "type": "relation",
            "from": "Agentheim Project",
            "to": "Agentheim V1 Roadmap",
            "relationType": "guided_by",
        },
    ]
    return records


def write_memory(repo_root: Path, path: Path = MEMORY_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    records = build_memory_records(repo_root)
    lines = [json.dumps(record, ensure_ascii=False) for record in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    output = write_memory(ROOT)
    print(f"updated {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())