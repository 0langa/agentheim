from __future__ import annotations

import json

from pydantic import BaseModel, Field
from pydantic import ValidationError

from core.json_repair import repair_json_text
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
    def build_prompt(self, topic: str, context_shards: dict[str, str] | None = None) -> str:
        shards_text = ""
        if context_shards:
            formatted = "\n\n".join(
                f"--- {name} ---\n{content}" for name, content in context_shards.items()
            )
            shards_text = f"\n\nProject context:\n{formatted}\n"
        return (
            f"Research topic: {topic}\n\n"
            f"{shards_text}"
            "Find relevant web sources. Return structured JSON with sources, "
            "search queries used, and raw findings."
        )

    def run_gather(self, topic: str, context_shards: dict[str, str] | None = None):
        prompt = self.build_prompt(topic, context_shards=context_shards)
        return self.run_structured(prompt, max_output_tokens=2500)

    def _parse(self, raw_output: str) -> GatherResult:
        data = json.loads(repair_json_text(raw_output))
        sources = data.get("sources")
        normalized_sources = []
        if isinstance(sources, list):
            for item in sources:
                if not isinstance(item, dict):
                    continue
                raw_relevance = item.get("relevance_score")
                if raw_relevance is None:
                    relevance_label = str(item.get("relevance", "")).lower()
                    raw_relevance = 8 if relevance_label == "high" else 6 if relevance_label == "medium" else 4
                title = str(item.get("title") or item.get("name") or item.get("url") or "Untitled source")
                url = str(item.get("url") or item.get("link") or "unknown")
                snippet = str(
                    item.get("snippet")
                    or item.get("description")
                    or item.get("summary")
                    or item.get("raw_findings")
                    or title
                )
                normalized_sources.append(
                    {
                        "url": url,
                        "title": title,
                        "snippet": snippet,
                        "relevance_score": max(1, min(10, int(raw_relevance))),
                    }
                )
        data["sources"] = normalized_sources
        search_queries = data.get("search_queries") or data.get("queries") or []
        if not isinstance(search_queries, list):
            search_queries = [str(search_queries)]
        data["search_queries"] = [str(item) for item in search_queries if str(item).strip()]
        raw_findings = data.get("raw_findings")
        if isinstance(raw_findings, list):
            data["raw_findings"] = "\n".join(
                f"{item.get('source', 'source')}: {item.get('content', '')}"
                for item in raw_findings
                if isinstance(item, dict)
            )
        elif isinstance(raw_findings, dict):
            data["raw_findings"] = json.dumps(raw_findings, ensure_ascii=False)
        elif raw_findings is None:
            data["raw_findings"] = str(data.get("summary", ""))
        try:
            return self.output_schema.model_validate(data)
        except (ValueError, ValidationError):
            raise
