from __future__ import annotations

from pathlib import Path
from typing import Any

from agentheim.context_ops_impl import AictxContextOps
from agentheim.context_run_ledger import ContextRunLedger
from config.config import load_team_config
from core.public_api import (
    AIteamError,
    ModelRegistry,
    PolicyEngine,
    RunLedger,
    ToolRegistry,
)
from workflows.coding.provider_map import DEFAULT_PROVIDER_MAP
from workflows.research.reports.final_report import ResearchReport, Section
from workflows.research.reports.markdown import render_research_report_markdown
from workflows.research.workflows.research import ResearchWorkflow


class ResearchPlanningError(AIteamError):
    """Raised when research planning or execution fails."""


# Shard filenames considered relevant for research grounding.
_RELEVANT_SHARD_NAMES = [
    "ai-index.md",
    "project-state.md",
    "architecture.md",
    "public-docs-map.md",
    "workflows.md",
    "code-map.md",
]


def _load_context_shards(repo_root: Path) -> dict[str, str]:
    """Load relevant AICtx shards from docs/AIprojectcontext/."""
    context_dir = repo_root / "docs" / "AIprojectcontext"
    shards: dict[str, str] = {}
    if not context_dir.exists():
        return shards
    for name in _RELEVANT_SHARD_NAMES:
        path = context_dir / name
        if path.exists():
            shards[name] = path.read_text(encoding="utf-8")
    return shards


def _preflight_context(
    repo_root: Path,
    ledger: RunLedger,
) -> tuple[dict[str, str], str | None]:
    """Ensure context is fresh and return relevant shards plus optional warning."""
    ops = AictxContextOps()
    ctx_ledger = ContextRunLedger(ledger)

    status = ops.status(repo_root, strict=False)
    ctx_ledger.emit_status(status)

    warning: str | None = None

    if status.is_stale:
        warning = (
            "Project context was stale at the start of this research run. "
            "AICtx pipeline was triggered automatically."
        )
        ops.run_pipeline(
            repo_root,
            run_id="research-ctx",
            scope="changed",
            write_mode="apply",
        )

    shards = _load_context_shards(repo_root)
    if not shards:
        raise RuntimeError("No AICtx shards found.")

    return shards, warning


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

    shards, warning = _preflight_context(repo_root, ledger)

    team_config = load_team_config()
    registry = ModelRegistry.from_team_config(team_config, provider_map=DEFAULT_PROVIDER_MAP)
    tool_registry = ToolRegistry()
    policy_engine = PolicyEngine()

    workflow = ResearchWorkflow(registry, tool_registry, policy_engine, ledger)
    results = workflow.run(repo_root, metadata={"topic": topic, "context_shards": shards})

    if not workflow.verify(results):
        failed = [r.step_id for r in results if not r.success]
        raise ResearchPlanningError(f"Research workflow failed at steps: {failed}")

    report_step = results[-1]
    if not report_step.success or report_step.metadata.get("parsed") is None:
        raise ResearchPlanningError("Report generation failed with invalid output.")

    report = ResearchReport.model_validate(report_step.metadata["parsed"])

    if warning:
        warning_section = Section(heading="Context Warning", content=warning)
        report = ResearchReport(
            topic=report.topic,
            executive_summary=report.executive_summary,
            sections=[warning_section, *report.sections],
            sources=report.sources,
            confidence=report.confidence,
            recommendations=report.recommendations,
        )

    ledger.write_json("final_report.json", report.model_dump())
    ledger.write_text("final_report.md", render_research_report_markdown(report))
    return report, ledger.run_dir
