from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from workflows.documents.agents.base import BaseAgent
from core.schemas_runtime import AgentResult


class DocumentEntry(BaseModel):
    path: str
    summary: str
    keywords: list[str] = Field(default_factory=list)


class IndexerOutput(BaseModel):
    documents: list[DocumentEntry] = Field(default_factory=list)


class IndexerAgent(BaseAgent[IndexerOutput]):
    def build_prompt(self, repo_root: Path, file_paths: list[Path]) -> str:
        lines: list[str] = []
        for rel_path in file_paths:
            full = repo_root / rel_path
            try:
                text = full.read_text(encoding="utf-8", errors="ignore")
                excerpt = text[:800]
                if len(text) > 800:
                    excerpt += "\n...[truncated]"
            except Exception:
                excerpt = "<unreadable>"
            lines.append(f"---\nFile: {rel_path.as_posix()}\n{excerpt}\n")
        files_block = "\n".join(lines)
        return (
            f"Repository root: {repo_root.name}\n\n"
            f"Documents to index:\n{files_block}\n"
            "Return only valid JSON matching IndexerOutput. "
            "For each document provide path, a short summary, and relevant keywords."
        )

    def run_index(self, repo_root: Path, file_paths: list[Path]) -> AgentResult:
        prompt = self.build_prompt(repo_root, file_paths)
        return self.run_structured(prompt, max_output_tokens=2500)
