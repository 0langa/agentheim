from __future__ import annotations

from pydantic import BaseModel, Field


class DocUpdateRecord(BaseModel):
    doc_path: str
    status: str
    details: str = ""


class FinalReport(BaseModel):
    task_summary: str
    updated_docs: list[DocUpdateRecord] = Field(default_factory=list)
    remaining_risks: list[str] = Field(default_factory=list)
    run_id: str
    status: str = "done"
