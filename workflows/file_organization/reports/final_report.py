from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FileMoveRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    source: str
    target: str
    success: bool = True
    error: str = ""


class FileOrganizationReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    task_summary: str
    analyzed_files: int = 0
    proposed_moves: list[FileMoveRecord] = Field(default_factory=list)
    preview: str = ""
    applied_moves: list[FileMoveRecord] = Field(default_factory=list)
    run_id: str
    status: str = "done"
