from __future__ import annotations

import json
from pathlib import Path

from scripts.refresh_kimi_memory import build_memory_records, write_memory


def test_build_memory_records_includes_project_and_roadmap(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path
    (repo / "interfaces" / "cli").mkdir(parents=True)
    (repo / "interfaces" / "cli" / "product_commands.py").write_text("# setup exists\n", encoding="utf-8")

    def fake_git_summary(_repo: Path) -> tuple[str, str]:
        return "master", "clean working tree"

    def fake_pytest_count(_repo: Path) -> tuple[str, str]:
        return "1355 tests collected", "1355 tests collected\n"

    monkeypatch.setattr("scripts.refresh_kimi_memory._git_summary", fake_git_summary)
    monkeypatch.setattr("scripts.refresh_kimi_memory._run_pytest_count", fake_pytest_count)

    records = build_memory_records(repo)
    names = {record.get("name") for record in records if record.get("type") == "entity"}
    assert "Agentheim Project" in names
    assert "Agentheim V1 Roadmap" in names


def test_write_memory_rewrites_jsonl(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path
    (repo / "interfaces" / "cli").mkdir(parents=True)
    output = repo / ".kimi" / "memory.jsonl"

    monkeypatch.setattr("scripts.refresh_kimi_memory._git_summary", lambda _repo: ("master", "clean working tree"))
    monkeypatch.setattr("scripts.refresh_kimi_memory._run_pytest_count", lambda _repo: ("10 tests collected", "10 tests collected\n"))

    write_memory(repo, output)
    lines = output.read_text(encoding="utf-8").strip().splitlines()
    assert lines
    payloads = [json.loads(line) for line in lines]
    assert any(item.get("name") == "Agentheim Project" for item in payloads)
    assert any(item.get("name") == "Agentheim V1 Roadmap" for item in payloads)