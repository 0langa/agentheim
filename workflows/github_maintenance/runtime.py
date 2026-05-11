from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config.config import load_team_config
from core.public_api import ModelRegistry, RunLedger
from workflows.coding.provider_map import DEFAULT_PROVIDER_MAP
from workflows.github_maintenance.reports.final_report import IssueSummaryRecord, FinalReport
from workflows.github_maintenance.reports.markdown import render_final_report_markdown
from workflows.github_maintenance.workflows.github_maintenance import create_summarizer_agent, create_drafter_agent


def plan_task(issues_text: str, write_ledger: bool = False) -> tuple[Any, Path | None]:
    team_config = load_team_config()
    registry = ModelRegistry.from_team_config(team_config, provider_map=DEFAULT_PROVIDER_MAP)
    summarizer = create_summarizer_agent(registry)
    result = summarizer.run_summary(issues_text)
    ledger_dir: Path | None = None
    if write_ledger:
        ledger = RunLedger.create(Path(".").resolve(), "github_maintenance_plan")
        ledger.write_json("run.json", {"action": "plan"})
        ledger.write_text("issues.txt", issues_text)
        ledger.write_text("raw_model_output.txt", result.raw_output)
        if result.parsed_output is not None:
            ledger.write_json("plan.json", result.parsed_output)
        ledger_dir = ledger.run_dir
    return result.parsed_output, ledger_dir


def run_task(
    issues_text: str,
    *,
    write_ledger: bool = True,
) -> tuple[FinalReport, Path | None]:
    ledger: RunLedger | None = None
    ledger_dir: Path | None = None
    if write_ledger:
        ledger = RunLedger.create(Path(".").resolve(), "github_maintenance_run")
        ledger_dir = ledger.run_dir

    summary, _ = plan_task(issues_text)
    team_config = load_team_config()
    registry = ModelRegistry.from_team_config(team_config, provider_map=DEFAULT_PROVIDER_MAP)
    summarizer = create_summarizer_agent(registry)
    drafter = create_drafter_agent(registry)

    summary_result = summarizer.run_summary(issues_text)
    if not summary_result.success or summary_result.parsed_output is None:
        report = FinalReport(
            task_summary="Summarization failed",
            issues=[],
            remaining_risks=[summary_result.error or "unknown"],
            run_id=ledger.run_dir.name if ledger else "none",
            status="failed",
        )
        if ledger:
            ledger.write_json("final_report.json", report.model_dump())
            ledger.write_text("final_report.md", render_final_report_markdown(report))
        return report, ledger_dir

    issues = summary_result.parsed_output.get("issues", [])
    draft = drafter.run_draft(json.dumps(summary_result.parsed_output))
    pr_title = ""
    pr_body = ""
    remaining_risks: list[str] = []
    if draft.success and draft.parsed_output:
        pr_title = draft.parsed_output.get("pr_title", "")
        pr_body = draft.parsed_output.get("pr_body", "")
    else:
        remaining_risks = [draft.error or "drafting failed"]

    report = FinalReport(
        task_summary=f"GitHub maintenance run. Issues summarized: {len(issues)}",
        issues=[IssueSummaryRecord(number=i["number"], title=i["title"], summary=i["summary"]) for i in issues],
        pr_title=pr_title,
        pr_body=pr_body,
        remaining_risks=remaining_risks,
        run_id=ledger.run_dir.name if ledger else "none",
        status="done",
    )
    if ledger:
        ledger.write_json("final_report.json", report.model_dump())
        ledger.write_text("final_report.md", render_final_report_markdown(report))
    return report, ledger_dir
