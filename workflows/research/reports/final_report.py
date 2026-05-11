from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Section(BaseModel):
    model_config = ConfigDict(frozen=True)

    heading: str = Field(min_length=1)
    content: str = Field(min_length=1)


class ResearchReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    topic: str = Field(min_length=1)
    executive_summary: str = Field(min_length=1)
    sections: list[Section] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    confidence: str = Field(default="medium")
    recommendations: list[str] = Field(default_factory=list)
