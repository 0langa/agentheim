from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config.config import load_team_config
from core.public_api import ModelRegistry, RunLedger, build_context_pack, inspect_repository
from workflows.coding.provider_map import DEFAULT_PROVIDER_MAP
from workflows.docs_maintenance.reports.final_report import DocUpdateRecord, FinalReport
from workflows.docs_maintenance.reports.markdown import render_final_report_markdown
from workflows.docs_maintenance.workflows.docs_maintenance import create_detector_agent, create_updater_agent, create_aligner_agent


def plan_task(repo_path: str | Path, write_ledger: bool = False) -> tuple[str, Any, Path | None]:
    repo_root = Path(repo_path).resolve()
    scan = inspect_repository(repo_root)
    context_pack = build_context_pack(scan)
    team_config = load_team_config()
    registry = ModelRegistry.from_team_config(team_config, provider_map=DEFAULT_PROVIDER_MAP)
    detector = create_detector_agent(registry)
    prompt = f"Repository docs context:\n{context_pack}\n\nIdentify stale docs."
    result = detector.run_detection(prompt)
    ledger_dir: Path | None = None
    if write_ledger:
        ledger = RunLedger.create(repo_root, "docs_maintenance_plan")
        ledger.write_json("run.json", {"action": "plan", "repo_name": scan.repo_name})
        ledger.write_text("context_pack.md", context_pack)
        ledger.write_text("raw_model_output.txt", result.raw_output)
        if result.parsed_output is not None:
            ledger.write_json("plan.json", result.parsed_output)
        ledger_dir = ledger.run_dir
    return context_pack, result.parsed_output, ledger_dir


def run_task(
    repo_path: str | Path,
    *,
    mode: str = "apply",
    write_ledger: bool = True,
) -> tuple[FinalReport, Path | None]:
    repo_root = Path(repo_path).resolve()
    ledger: RunLedger | None = None
    ledger_dir: Path | None = None
    if write_ledger:
        ledger = RunLedger.create(repo_root, "docs_maintenance_run")
        ledger_dir = ledger.run_dir

    context_pack, plan, _ = plan_task(repo_root)
    team_config = load_team_config()
    registry = ModelRegistry.from_team_config(team_config, provider_map=DEFAULT_PROVIDER_MAP)
    detector = create_detector_agent(registry)
    updater = create_updater_agent(registry)
    aligner = create_aligner_agent(registry)

    detection = detector.run_detection(context_pack)
    if not detection.success or detection.parsed_output is None:
        report = FinalReport(
            task_summary="Detection failed",
            updated_docs=[],
            remaining_risks=[detection.error or "unknown"],
            run_id=ledger.run_dir.name if ledger else "none",
            status="failed",
        )
        if ledger:
            ledger.write_json("final_report.json", report.model_dump())
            ledger.write_text("final_report.md", render_final_report_markdown(report))
        return report, ledger_dir

    stale = detection.parsed_output.get("stale_docs", [])
    updates: list[DocUpdateRecord] = []
    for item in stale:
        update_result = updater.run_update(json.dumps(item))
        if update_result.success and update_result.parsed_output:
            for u in update_result.parsed_output.get("updates", []):
                path = repo_root / u["path"]
                if mode == "apply":
                    if ledger:
                        ledger.append_jsonl(
                            "file_changes.jsonl",
                            {"operation": "write_text", "path": str(path.relative_to(repo_root)), "size": len(u["new_content"])},
                        )
                    path.write_text(u["new_content"], encoding="utf-8")
                updates.append(DocUpdateRecord(doc_path=u["path"], status="updated", details="content rewritten"))
        else:
            updates.append(DocUpdateRecord(doc_path=item["path"], status="failed", details=update_result.error or "update failed"))

    align_input = json.dumps([u.model_dump() for u in updates])
    alignment = aligner.run_alignment(align_input)
    remaining_risks: list[str] = []
    if alignment.success and alignment.parsed_output:
        if not alignment.parsed_output.get("aligned", True):
            remaining_risks = [i["issue"] for i in alignment.parsed_output.get("issues", [])]
    else:
        remaining_risks = [alignment.error or "alignment failed"]

    report = FinalReport(
        task_summary=f"Docs maintenance run. Stale docs detected: {len(stale)}",
        updated_docs=updates,
        remaining_risks=remaining_risks,
        run_id=ledger.run_dir.name if ledger else "none",
        status="done",
    )
    if ledger:
        ledger.write_json("final_report.json", report.model_dump())
        ledger.write_text("final_report.md", render_final_report_markdown(report))
    return report, ledger_dir
