from __future__ import annotations

from pydantic import BaseModel, Field

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
