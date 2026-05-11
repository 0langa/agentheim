from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from workflows.documents.agents.base import BaseAgent
from core.schemas_runtime import AgentResult


class Citation(BaseModel):
    path: str
    quote: str


class AnswererOutput(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)


class AnswerAgent(BaseAgent[AnswererOutput]):
    def build_prompt(self, query: str, chunks: list[dict[str, Any]]) -> str:
        lines: list[str] = []
        for chunk in chunks:
            lines.append(
                f"---\nSource: {chunk.get('path', 'unknown')}\n"
                f"Excerpt: {chunk.get('excerpt', '')}\n"
            )
        chunks_block = "\n".join(lines)
        return (
            f"User query: {query}\n\n"
            f"Retrieved chunks:\n{chunks_block}\n"
            "Return only valid JSON matching AnswererOutput. "
            "Synthesize a concise answer and include citations with exact quotes from the sources."
        )

    def run_answer(self, query: str, chunks: list[dict[str, Any]]) -> AgentResult:
        prompt = self.build_prompt(query, chunks)
        return self.run_structured(prompt, max_output_tokens=2500)
