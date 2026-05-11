from __future__ import annotations

from pydantic import BaseModel, Field


class IssueSummaryRecord(BaseModel):
    number: int
    title: str
    summary: str


class FinalReport(BaseModel):
    task_summary: str
    issues: list[IssueSummaryRecord] = Field(default_factory=list)
    pr_title: str = ""
    pr_body: str = ""
    remaining_risks: list[str] = Field(default_factory=list)
    run_id: str
    status: str = "done"
