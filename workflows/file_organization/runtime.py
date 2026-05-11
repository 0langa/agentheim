from __future__ import annotations

from pathlib import Path
from typing import Any

from config.config import load_team_config
from core.public_api import ModelRegistry, PolicyEngine, RunLedger, ToolRegistry
from workflows.base import StepContext, StepResult
from workflows.coding.provider_map import DEFAULT_PROVIDER_MAP
from workflows.file_organization.agents.proposer import ProposerResult
from workflows.file_organization.reports.final_report import FileMoveRecord, FileOrganizationReport
from workflows.file_organization.reports.markdown import render_file_organization_markdown
from workflows.file_organization.workflows.file_organization import FileOrganizationWorkflow


class FileOrganizationError(Exception):
    """Raised when file organization workflow fails."""


def plan_task(
    task_text: str,
    repo_path: str | Path,
    write_ledger: bool = False,
) -> tuple[StepResult, ProposerResult | None, Path | None]:
    repo_root = Path(repo_path).resolve()
    team_config = load_team_config()
    registry = ModelRegistry.from_team_config(team_config, provider_map=DEFAULT_PROVIDER_MAP)

    ledger: RunLedger | None = None
    ledger_dir: Path | None = None
    if write_ledger:
        ledger = RunLedger.create(repo_root, "file_organization_plan")
        ledger.write_json("run.json", {"action": "plan", "task": task_text})
        ledger_dir = ledger.run_dir

    workflow = FileOrganizationWorkflow(
        model_registry=registry,
        tool_registry=ToolRegistry(),
        policy_engine=PolicyEngine(),
        ledger=ledger,
    )

    context = StepContext(
        run_id=ledger.run_dir.name if ledger else "plan",
        step_id="init",
        repo_root=repo_root,
        tools=ToolRegistry(),
        policy=PolicyEngine(),
        ledger=ledger,
        metadata={"task": task_text, "target_dir": str(repo_root)},
    )

    analyze_step = workflow.dag.steps["analyze"]
    analyze_result = workflow.execute_step(analyze_step, context)
    context.prior_results["analyze"] = analyze_result
    context.step_id = "propose"

    propose_step = workflow.dag.steps["propose"]
    propose_result = workflow.execute_step(propose_step, context)

    if ledger:
        ledger.write_text("raw_analyze_output.txt", analyze_result.output)
        ledger.write_text("raw_propose_output.txt", propose_result.output)
        if analyze_result.metadata.get("parsed"):
            ledger.write_json("analyze.json", analyze_result.metadata["parsed"])
        if propose_result.metadata.get("parsed"):
            ledger.write_json("propose.json", propose_result.metadata["parsed"])

    parsed = propose_result.metadata.get("parsed")
    plan = ProposerResult.model_validate(parsed) if parsed else None
    return analyze_result, plan, ledger_dir


def run_task(
    task_text: str,
    repo_path: str | Path,
    *,
    dry_run: bool = False,
) -> tuple[FileOrganizationReport, Path]:
    repo_root = Path(repo_path).resolve()
    ledger = RunLedger.create(repo_root, "file_organization_run")
    ledger.write_json("run.json", {"action": "run", "task": task_text, "dry_run": dry_run})

    team_config = load_team_config()
    registry = ModelRegistry.from_team_config(team_config, provider_map=DEFAULT_PROVIDER_MAP)

    workflow = FileOrganizationWorkflow(
        model_registry=registry,
        tool_registry=ToolRegistry(),
        policy_engine=PolicyEngine(),
        ledger=ledger,
    )

    metadata = {"task": task_text, "target_dir": str(repo_root), "dry_run": dry_run}
    results = workflow.run(repo_root, metadata=metadata)

    report = _build_report(results, ledger)
    ledger.write_json("final_report.json", report.model_dump())
    ledger.write_text("final_report.md", render_file_organization_markdown(report))
    return report, ledger.run_dir


def _build_report(results: list[StepResult], ledger: RunLedger) -> FileOrganizationReport:
    analyze_parsed: dict[str, Any] = {}
    propose_parsed: dict[str, Any] = {}
    preview_parsed: dict[str, Any] = {}
    apply_metadata: dict[str, Any] = {}

    for r in results:
        if r.step_id == "analyze" and r.metadata.get("parsed"):
            analyze_parsed = r.metadata["parsed"]
        elif r.step_id == "propose" and r.metadata.get("parsed"):
            propose_parsed = r.metadata["parsed"]
        elif r.step_id == "preview" and r.metadata.get("parsed"):
            preview_parsed = r.metadata["parsed"]
        elif r.step_id == "apply":
            apply_metadata = r.metadata

    analyzed_files = len(analyze_parsed.get("files", [])) if analyze_parsed else 0
    task_summary = propose_parsed.get("new_structure_summary", "") if propose_parsed else ""
    preview = (
        preview_parsed.get("preview", "")
        if preview_parsed
        else (propose_parsed.get("preview", "") if propose_parsed else "")
    )

    proposed_moves = [
        FileMoveRecord(source=a["source"], target=a["target"])
        for a in propose_parsed.get("actions", [])
    ] if propose_parsed else []

    applied_moves = [
        FileMoveRecord(
            source=m["source"],
            target=m["target"],
            success=m.get("success", False),
            error=m.get("error", ""),
        )
        for m in apply_metadata.get("moves_executed", [])
    ] if apply_metadata else []

    success = all(r.success for r in results)
    return FileOrganizationReport(
        task_summary=task_summary,
        analyzed_files=analyzed_files,
        proposed_moves=proposed_moves,
        preview=preview,
        applied_moves=applied_moves,
        run_id=ledger.run_dir.name,
        status="done" if success else "failed",
    )
