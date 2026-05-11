from __future__ import annotations

from workflows.github_maintenance.reports.final_report import FinalReport


def render_final_report_markdown(report: FinalReport) -> str:
    issues = "\n".join(f"- #{i.number}: {i.title} — {i.summary}" for i in report.issues) or "- none"
    risks = "\n".join(f"- {r}" for r in report.remaining_risks) or "- none"
    return (
        f"# GitHub Maintenance Report\n\n"
        f"## Summary\n{report.task_summary}\n\n"
        f"## Issues\n{issues}\n\n"
        f"## Draft PR\n**{report.pr_title}**\n\n{report.pr_body}\n\n"
        f"## Remaining risks\n{risks}\n\n"
        f"## Run id\n`{report.run_id}`\n"
    )
