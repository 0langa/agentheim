from __future__ import annotations

from pathlib import Path
from typing import Any

from config.config import load_team_config
from core.ledger import RunLedger
from core.model_registry import ModelRegistry
from core.policy_engine import PolicyEngine
from core.repo.scanner import inspect_repository
from core.schemas import AgentMessage
from core.tool_protocol import ToolRegistry
from workflows.documents.provider_map import DEFAULT_PROVIDER_MAP
from workflows.documents.reports.final_report import Citation, DocumentChatReport
from workflows.documents.reports.markdown import render_document_chat_report_markdown
from workflows.documents.workflows.documents import DocumentsWorkflow


def plan_task(
    query: str,
    repo_path: str | Path,
    write_ledger: bool = False,
) -> tuple[Any, str, Path | None]:
    """Prepare a document chat plan by scanning the repository.

    Returns the repo scan, the original query, and an optional ledger directory.
    """
    repo_root = Path(repo_path).resolve()
    scan = inspect_repository(repo_root)
    ledger_dir: Path | None = None
    if write_ledger:
        ledger = RunLedger.create(repo_root, "documents-plan")
        ledger.write_json(
            "run.json", {"action": "plan", "repo_name": scan.repo_name, "query": query}
        )
        ledger.write_json("repo_snapshot.json", scan.model_dump())
        ledger.write_json(
            "model_messages.json",
            {"messages": [AgentMessage(actor="user", content=query).model_dump()]},
        )
        ledger_dir = ledger.run_dir
    return scan, query, ledger_dir


def run_task(
    query: str,
    repo_path: str | Path,
    write_ledger: bool = True,
) -> tuple[DocumentChatReport, Path | None]:
    """Run the full documents workflow and produce a report.

    Returns the DocumentChatReport and an optional ledger directory.
    """
    repo_root = Path(repo_path).resolve()
    ledger: RunLedger | None = None
    ledger_dir: Path | None = None
    if write_ledger:
        ledger = RunLedger.create(repo_root, "documents-run")
        ledger.write_json(
            "run.json", {"action": "run", "repo_name": repo_root.name, "query": query}
        )
        ledger.write_json(
            "model_messages.json",
            {"messages": [AgentMessage(actor="user", content=query).model_dump()]},
        )
        ledger_dir = ledger.run_dir

    team_config = load_team_config()
    registry = ModelRegistry.from_team_config(team_config, provider_map=DEFAULT_PROVIDER_MAP)
    workflow = DocumentsWorkflow(
        model_registry=registry,
        tool_registry=ToolRegistry(),
        policy_engine=PolicyEngine(),
        ledger=ledger,
    )

    results = workflow.run(repo_root, metadata={"query": query})

    answer_result = next((r for r in results if r.step_id == "answer"), None)
    citations: list[Citation] = []
    answer_text = ""
    sources: list[str] = []
    status = "done" if workflow.verify(results) else "failed"

    if answer_result and answer_result.metadata.get("parsed"):
        parsed = answer_result.metadata["parsed"]
        answer_text = parsed.get("answer", "")
        for c in parsed.get("citations", []):
            citations.append(Citation(path=c.get("path", ""), quote=c.get("quote", "")))
        sources = sorted({c.path for c in citations})

    report = DocumentChatReport(
        query=query,
        answer=answer_text,
        citations=citations,
        sources=sources,
        run_id=ledger_dir.name if ledger_dir else "unknown",
        status=status,
    )

    if ledger:
        ledger.write_json("final_report.json", report.model_dump())
        ledger.write_text("final_report.md", render_document_chat_report_markdown(report))

    return report, ledger_dir
