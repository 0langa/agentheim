from __future__ import annotations

from workflows.docs_maintenance.reports.final_report import FinalReport


def render_final_report_markdown(report: FinalReport) -> str:
    docs = "\n".join(f"- {d.doc_path}: {d.status} ({d.details})" for d in report.updated_docs) or "- none"
    risks = "\n".join(f"- {r}" for r in report.remaining_risks) or "- none"
    return (
        f"# Docs Maintenance Report\n\n"
        f"## Summary\n{report.task_summary}\n\n"
        f"## Updated docs\n{docs}\n\n"
        f"## Remaining risks\n{risks}\n\n"
        f"## Run id\n`{report.run_id}`\n"
    )
