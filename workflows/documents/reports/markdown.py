from __future__ import annotations

from workflows.documents.reports.final_report import DocumentChatReport


def render_document_chat_report_markdown(report: DocumentChatReport) -> str:
    citations = "\n".join(
        f'- `{c.path}`: "{c.quote}"' for c in report.citations
    ) or "- none"
    sources = "\n".join(f"- {s}" for s in report.sources) or "- none"
    return (
        f"# Document Chat Report\n\n"
        f"## Query\n{report.query}\n\n"
        f"## Answer\n{report.answer}\n\n"
        f"## Citations\n{citations}\n\n"
        f"## Sources\n{sources}\n\n"
        f"## Run ID\n`{report.run_id}`\n\n"
        f"## Status\n{report.status}\n"
    )
