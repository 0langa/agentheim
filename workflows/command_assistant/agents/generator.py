from __future__ import annotations

import platform

from pydantic import BaseModel, Field

from core.schemas_runtime import AgentResult
from workflows.command_assistant.agents.base import BaseAgent


class GeneratedCommand(BaseModel):
    command: list[str] = Field(default_factory=list)
    explanation: str = ""
    safe: bool = True


class GeneratorAgent(BaseAgent[GeneratedCommand]):
    def run_generate(self, parsed_intent_json: str) -> AgentResult:
        system = platform.system().lower()
        shell_hint = "PowerShell" if system == "windows" else "POSIX shell"
        prompt = (
            "Generate a safe shell command for the following parsed intent.\n\n"
            f"{parsed_intent_json}\n\n"
            f"Target environment: {system} using {shell_hint}. Prefer commands valid in that shell.\n\n"
            "Return only valid JSON matching the GeneratedCommand schema."
        )
        return self.run_structured(prompt, max_output_tokens=800)
