from __future__ import annotations

import json

from pydantic import BaseModel, Field
from pydantic import ValidationError

from core.json_repair import repair_json_text
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

    def _parse(self, raw_output: str) -> RetrieverOutput:
        data = json.loads(repair_json_text(raw_output))

        # Case 1: Model returns a list directly ([{"chunk": "..."}] or [{"path": "..."}])
        if isinstance(data, list):
            normalized = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                chunk_text = item.get("chunk") or item.get("excerpt") or item.get("text") or item.get("quote") or ""
                path = item.get("path") or item.get("file") or item.get("document") or item.get("source") or ""
                score = max(0.0, min(1.0, float(item.get("relevance_score") or item.get("score") or 0.8)))
                if chunk_text or path:
                    normalized.append({"path": path, "excerpt": chunk_text, "relevance_score": score})
            if normalized:
                return RetrieverOutput.model_validate({"chunks": normalized})

        # Case 2: Expected {"chunks": [...]}
        if isinstance(data, dict):
            chunks = data.get("chunks")
            if isinstance(chunks, list) and chunks:
                return RetrieverOutput.model_validate({"chunks": chunks})

            # Case 3: Aliases {"results": [...]} or {"retrieved_chunks": [...]}
            alias_chunks = data.get("results") or data.get("retrieved_chunks")
            if isinstance(alias_chunks, list):
                normalized = []
                for item in alias_chunks:
                    if not isinstance(item, dict):
                        continue
                    path = (
                        item.get("path")
                        or item.get("file")
                        or item.get("document")
                        or item.get("document_id")
                        or item.get("source")
                        or ""
                    )
                    excerpt = (
                        item.get("excerpt")
                        or item.get("quote")
                        or item.get("text")
                        or item.get("chunk")
                        or ""
                    )
                    normalized.append(
                        {
                            "path": path,
                            "excerpt": excerpt,
                            "relevance_score": max(
                                0.0,
                                min(
                                    1.0,
                                    float(item.get("relevance_score") or item.get("score") or 0.0),
                                ),
                            ),
                        }
                    )
                return RetrieverOutput.model_validate({"chunks": normalized})

        try:
            return self.output_schema.model_validate(data)
        except (ValueError, ValidationError):
            raise
