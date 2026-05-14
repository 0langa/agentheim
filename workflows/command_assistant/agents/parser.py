from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from core.schemas_runtime import AgentResult
from workflows.command_assistant.agents.base import BaseAgent


class ParsedIntent(BaseModel):
    action: str
    target: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)


class ParserAgent(BaseAgent[ParsedIntent]):
    def run_parse(self, user_input: str) -> AgentResult:
        prompt = (
            "Parse the following user request into a structured intent.\n\n"
            f"{user_input}\n\n"
            "Return only valid JSON matching the ParsedIntent schema."
        )
        return self.run_structured(prompt, max_output_tokens=800)
