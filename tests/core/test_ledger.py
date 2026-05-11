from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.ledger import RunLedger


class TestRunLedger:
    def test_create_makes_directory(self, tmp_path: Path) -> None:
        ledger = RunLedger.create(tmp_path, "test-run")
        assert ledger.run_dir.exists()
        assert ledger.repo_root == tmp_path

    def test_create_makes_jsonl_files(self, tmp_path: Path) -> None:
        ledger = RunLedger.create(tmp_path, "test-run")
        assert (ledger.run_dir / "tool_calls.jsonl").exists()
        assert (ledger.run_dir / "state_transitions.jsonl").exists()

    def test_write_json(self, tmp_path: Path) -> None:
        ledger = RunLedger.create(tmp_path, "test-run")
        path = ledger.write_json("data.json", {"key": "value"})
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["key"] == "value"

    def test_write_text(self, tmp_path: Path) -> None:
        ledger = RunLedger.create(tmp_path, "test-run")
        path = ledger.write_text("notes.md", "# Hello")
        assert path.exists()
        assert path.read_text(encoding="utf-8") == "# Hello"

    def test_append_jsonl(self, tmp_path: Path) -> None:
        ledger = RunLedger.create(tmp_path, "test-run")
        ledger.append_jsonl("events.jsonl", {"event": "start"})
        ledger.append_jsonl("events.jsonl", {"event": "end"})
        lines = (ledger.run_dir / "events.jsonl").read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0])["event"] == "start"
        assert json.loads(lines[1])["event"] == "end"

    def test_sanitize_value_replaces_repo_root(self, tmp_path: Path) -> None:
        ledger = RunLedger.create(tmp_path, "test-run")
        path = ledger.write_json("paths.json", {"root": str(tmp_path), "nested": str(tmp_path / "sub" / "file.txt")})
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["root"] == "${REPO_ROOT}"
        assert data["nested"] == "${REPO_ROOT}/sub/file.txt"

    def test_sanitize_value_no_repo_root(self, tmp_path: Path) -> None:
        ledger = RunLedger.create(tmp_path, "test-run")
        path = ledger.write_json("plain.json", {"name": "hello"})
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["name"] == "hello"
