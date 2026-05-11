from __future__ import annotations

from pathlib import Path
from typing import Any

from config.config import load_team_config
from core.public_api import AIteamError, ModelRegistry, PolicyEngine, RunLedger, ToolRegistry
from workflows.coding.provider_map import DEFAULT_PROVIDER_MAP
from workflows.research.reports.final_report import ResearchReport
from workflows.research.reports.markdown import render_research_report_markdown
from workflows.research.workflows.research import ResearchWorkflow


class ResearchPlanningError(AIteamError):
    """Raised when research planning or execution fails."""


def plan_task(topic: str, write_ledger: bool = False) -> tuple[str, Path | None]:
    """Plan a research task. Returns the topic and optional ledger directory."""
    ledger_dir: Path | None = None
    if write_ledger:
        ledger = RunLedger.create(Path(".").resolve(), "research_plan")
        ledger.write_json("run.json", {"action": "plan", "topic": topic})
        ledger_dir = ledger.run_dir
    return topic, ledger_dir


def run_task(topic: str) -> tuple[ResearchReport, Path]:
    """Run the full research workflow and return the report and ledger path."""
    repo_root = Path(".").resolve()
    ledger = RunLedger.create(repo_root, "research")
    ledger.write_json("run.json", {"action": "run", "topic": topic})

    team_config = load_team_config()
    registry = ModelRegistry.from_team_config(team_config, provider_map=DEFAULT_PROVIDER_MAP)
    tool_registry = ToolRegistry()
    policy_engine = PolicyEngine()

    workflow = ResearchWorkflow(registry, tool_registry, policy_engine, ledger)
    results = workflow.run(repo_root, metadata={"topic": topic})

    if not workflow.verify(results):
        failed = [r.step_id for r in results if not r.success]
        raise ResearchPlanningError(f"Research workflow failed at steps: {failed}")

    report_step = results[-1]
    if not report_step.success or report_step.metadata.get("parsed") is None:
        raise ResearchPlanningError("Report generation failed with invalid output.")

    report = ResearchReport.model_validate(report_step.metadata["parsed"])
    ledger.write_json("final_report.json", report.model_dump())
    ledger.write_text("final_report.md", render_research_report_markdown(report))
    return report, ledger.run_dir
