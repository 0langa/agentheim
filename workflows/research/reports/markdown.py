from __future__ import annotations

from workflows.research.reports.final_report import ResearchReport


def render_research_report_markdown(report: ResearchReport) -> str:
    sections = "\n\n".join(
        f"## {section.heading}\n\n{section.content}"
        for section in report.sections
    ) or "## No sections"
    sources = "\n".join(f"- {source}" for source in report.sources) or "- none"
    recommendations = "\n".join(f"- {rec}" for rec in report.recommendations) or "- none"
    return (
        f"# Research Report: {report.topic}\n\n"
        f"## Executive Summary\n\n{report.executive_summary}\n\n"
        f"{sections}\n\n"
        f"## Sources\n\n{sources}\n\n"
        f"## Confidence\n\n{report.confidence}\n\n"
        f"## Recommendations\n\n{recommendations}\n"
    )
