from __future__ import annotations

from workflows.file_organization.reports.final_report import FileOrganizationReport


def render_file_organization_markdown(report: FileOrganizationReport) -> str:
    proposed = "\n".join(f"- {m.source} -> {m.target}" for m in report.proposed_moves) or "- none"
    applied = "\n".join(
        f"- {m.source} -> {m.target}" + (f" (error: {m.error})" if not m.success else "")
        for m in report.applied_moves
    ) or "- none"
    return (
        f"# File Organization Report\n\n"
        f"**Status:** {report.status}\n\n"
        f"**Run ID:** `{report.run_id}`\n\n"
        f"## Summary\n{report.task_summary}\n\n"
        f"## Analyzed Files\n{report.analyzed_files}\n\n"
        f"## Proposed Moves\n{proposed}\n\n"
        f"## Preview\n{report.preview}\n\n"
        f"## Applied Moves\n{applied}\n"
    )
