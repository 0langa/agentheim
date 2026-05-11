from __future__ import annotations

from pydantic import BaseModel, Field


class CommandRecord(BaseModel):
    command: list[str] = Field(default_factory=list)
    explanation: str = ""
    safe: bool = True


class FinalReport(BaseModel):
    task_summary: str
    commands: list[CommandRecord] = Field(default_factory=list)
    run_id: str
    status: str = "done"
