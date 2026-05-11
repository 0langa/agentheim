from __future__ import annotations

from workflows.command_assistant.reports.final_report import FinalReport


def render_final_report_markdown(report: FinalReport) -> str:
    lines: list[str] = []
    for c in report.commands:
        lines.append(f"- `{' '.join(c.command)}` — {c.explanation} (safe={c.safe})")
    commands = "\n".join(lines) or "- none"
    return (
        f"# Command Assistant Report\n\n"
        f"## Summary\n{report.task_summary}\n\n"
        f"## Commands\n{commands}\n\n"
        f"## Run id\n`{report.run_id}`\n"
    )
