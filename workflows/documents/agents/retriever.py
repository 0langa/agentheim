from __future__ import annotations

from pydantic import BaseModel, Field

from workflows.documents.agents.base import BaseAgent
from core.schemas_runtime import AgentResult


class RetrievalChunk(BaseModel):
    path: str
    excerpt: str
    relevance_score: float = Field(ge=0.0, le=1.0)


class RetrieverOutput(BaseModel):
    chunks: list[RetrievalChunk] = Field(default_factory=list)


class RetrieverAgent(BaseAgent[RetrieverOutput]):
    def build_prompt(self, query: str, file_contents: dict[str, str]) -> str:
        lines: list[str] = []
        for path, content in file_contents.items():
            excerpt = content[:1200]
            if len(content) > 1200:
                excerpt += "\n...[truncated]"
            lines.append(f"---\nFile: {path}\n{excerpt}\n")
        docs_block = "\n".join(lines)
        return (
            f"User query: {query}\n\n"
            f"Indexed documents:\n{docs_block}\n"
            "Return only valid JSON matching RetrieverOutput. "
            "Select the most relevant chunks (up to 5) with excerpts and relevance scores."
        )

    def run_retrieve(self, query: str, file_contents: dict[str, str]) -> AgentResult:
        prompt = self.build_prompt(query, file_contents)
        return self.run_structured(prompt, max_output_tokens=2500)
