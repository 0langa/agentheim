from __future__ import annotations

import json

from pydantic import ValidationError
from pydantic import BaseModel, Field

from core.json_repair import repair_json_text
from workflows.file_organization.agents.base import BaseAgent


class FileClassification(BaseModel):
    path: str
    category: str
    confidence: float = Field(ge=0.0, le=1.0)


class AnalyzerResult(BaseModel):
    files: list[FileClassification]
    summary: str


class AnalyzerAgent(BaseAgent[AnalyzerResult]):
    def build_analyze_prompt(self, target_dir: str, files: list[str]) -> str:
        file_list = "\n".join(f"- {f}" for f in files) or "- none"
        return (
            f"Analyze the following directory: {target_dir}\n\n"
            f"Files found:\n{file_list}\n\n"
            "For each file, classify it into a category such as document, image, code, config, data, or archive. "
            "Return only valid JSON matching the required schema. Do not wrap in markdown."
        )

    def _parse(self, raw_output: str) -> AnalyzerResult:
        try:
            return super()._parse(raw_output)
        except (ValueError, ValidationError):
            data = json.loads(repair_json_text(raw_output))
            if isinstance(data, dict) and "files" not in data:
                files: list[dict[str, object]] = []
                for path, details in data.items():
                    if not isinstance(details, dict):
                        continue
                    files.append(
                        {
                            "path": path,
                            "category": details.get("category", "unknown"),
                            "confidence": details.get("confidence", 0.5),
                        }
                    )
                return AnalyzerResult(
                    files=files,
                    summary=f"Classified {len(files)} files.",
                )
            raise
