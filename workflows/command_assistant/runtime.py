from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config.config import load_team_config
from core.public_api import EventType, ModelRegistry, RunLedger
from workflows.coding.provider_map import DEFAULT_PROVIDER_MAP
from workflows.command_assistant.reports.final_report import CommandRecord, FinalReport
from workflows.command_assistant.reports.markdown import render_final_report_markdown
from workflows.command_assistant.workflows.command_assistant import create_parser_agent, create_generator_agent


def plan_task(user_input: str, write_ledger: bool = False) -> tuple[Any, Path | None]:
    team_config = load_team_config()
    registry = ModelRegistry.from_team_config(team_config, provider_map=DEFAULT_PROVIDER_MAP)
    parser = create_parser_agent(registry)
    result = parser.run_parse(user_input)
    ledger_dir: Path | None = None
    if write_ledger:
        ledger = RunLedger.create(Path(".").resolve(), "command_assistant_plan")
        ledger.write_json("run.json", {"action": "plan", "input": user_input})
        ledger.write_text("raw_model_output.txt", result.raw_output)
        if result.parsed_output is not None:
            ledger.write_json("plan.json", result.parsed_output)
        ledger_dir = ledger.run_dir
    return result.parsed_output, ledger_dir


def run_task(
    user_input: str,
    *,
    write_ledger: bool = True,
) -> tuple[FinalReport, Path | None]:
    ledger: RunLedger | None = None
    ledger_dir: Path | None = None
    if write_ledger:
        ledger = RunLedger.create(Path(".").resolve(), "command_assistant_run")
        ledger_dir = ledger.run_dir
        ledger.emit_event(
            EventType.RUN_INITIATED,
            payload={
                "workflow_id": "command_assistant",
                "repo_root": str(Path(".").resolve()),
                "metadata": {"user_input": user_input},
            },
        )

    parsed, _ = plan_task(user_input)
    team_config = load_team_config()
    registry = ModelRegistry.from_team_config(team_config, provider_map=DEFAULT_PROVIDER_MAP)
    parser = create_parser_agent(registry)
    generator = create_generator_agent(registry)

    parse_result = parser.run_parse(user_input)
    if not parse_result.success or parse_result.parsed_output is None:
        report = FinalReport(
            task_summary="Parsing failed",
            commands=[],
            run_id=ledger.run_dir.name if ledger else "none",
            status="failed",
        )
        if ledger:
            ledger.write_json("final_report.json", report.model_dump())
            ledger.write_text("final_report.md", render_final_report_markdown(report))
        return report, ledger_dir

    generate_result = generator.run_generate(json.dumps(parse_result.parsed_output))
    commands: list[CommandRecord] = []
    if generate_result.success and generate_result.parsed_output:
        commands.append(CommandRecord(
            command=generate_result.parsed_output.get("command", []),
            explanation=generate_result.parsed_output.get("explanation", ""),
            safe=generate_result.parsed_output.get("safe", True),
        ))
    else:
        commands.append(CommandRecord(command=[], explanation=generate_result.error or "generation failed", safe=False))

    report = FinalReport(
        task_summary=f"Command assistant run for: {user_input}",
        commands=commands,
        run_id=ledger.run_dir.name if ledger else "none",
        status="done",
    )
    if ledger:
        ledger.write_json("final_report.json", report.model_dump())
        ledger.write_text("final_report.md", render_final_report_markdown(report))
    return report, ledger_dir
