import json

from ai_team.ledger import RunLedger


def test_ledger_scrubs_absolute_repo_paths(tmp_path) -> None:
    ledger = RunLedger.create(tmp_path, "run")
    doc_subdir = "docs-root"
    absolute_file = str(tmp_path / doc_subdir / "README.md")
    payload = {
        "repo_root": str(tmp_path),
        "path": absolute_file,
        "nested": {"items": [absolute_file]},
    }
    ledger.write_json("run.json", payload)
    ledger.append_jsonl("tool_calls.jsonl", payload)

    run_payload = json.loads((ledger.run_dir / "run.json").read_text(encoding="utf-8"))
    assert run_payload["repo_root"] == "${REPO_ROOT}"
    assert run_payload["path"] == f"${{REPO_ROOT}}/{doc_subdir}/README.md"
    assert run_payload["nested"]["items"][0] == f"${{REPO_ROOT}}/{doc_subdir}/README.md"

    line = (ledger.run_dir / "tool_calls.jsonl").read_text(encoding="utf-8").strip().splitlines()[-1]
    jsonl_payload = json.loads(line)
    assert jsonl_payload["repo_root"] == "${REPO_ROOT}"
    assert jsonl_payload["path"] == f"${{REPO_ROOT}}/{doc_subdir}/README.md"
