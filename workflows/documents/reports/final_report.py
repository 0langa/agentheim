from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Citation(BaseModel):
    model_config = ConfigDict(frozen=True)

    path: str
    quote: str


class DocumentChatReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    query: str
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    run_id: str
    status: str = "done"
