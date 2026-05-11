from __future__ import annotations

from pydantic import BaseModel, Field

from workflows.research.agents.base import BaseAgent


class Source(BaseModel):
    url: str = Field(min_length=1)
    title: str = Field(min_length=1)
    snippet: str = Field(min_length=1)
    relevance_score: int = Field(default=5, ge=1, le=10)


class GatherResult(BaseModel):
    sources: list[Source] = Field(default_factory=list)
    search_queries: list[str] = Field(default_factory=list)
    raw_findings: str = Field(default="")


class GathererAgent(BaseAgent[GatherResult]):
    def build_prompt(self, topic: str) -> str:
        return (
            f"Research topic: {topic}\n\n"
            "Find relevant web sources. Return structured JSON with sources, "
            "search queries used, and raw findings."
        )

    def run_gather(self, topic: str):
        prompt = self.build_prompt(topic)
        return self.run_structured(prompt, max_output_tokens=2500)
