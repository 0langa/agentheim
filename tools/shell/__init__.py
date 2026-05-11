"""Shell tool implementing ToolProtocol.

Command execution with allowlist/denylist enforcement and classification.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from core.errors import ToolSafetyError
from core.policies import CommandPolicy, can_auto_run, classify_command
from core.tool_protocol import BaseTool, ParamSchema, ReturnSchema, RiskLevel, ToolContext, ToolResult, ToolSchema


class ShellResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    command: list[str]
    returncode: int
    stdout: str
    stderr: str


class ShellTool(BaseTool):
    """Shell command execution with safety policies."""

    SAFE_PREFIXES = {"python", "pytest", "dotnet", "cargo", "go", "git", "npm", "node", "pip", "poetry"}

    def __init__(self, repo_root: str | Path = ".") -> None:
        self.repo_root = Path(repo_root).resolve()
        schema = ToolSchema(
            description="Execute shell commands within the workspace.",
            parameters={
                "command": ParamSchema(type="array", description="Command as list of strings", required=True),
                "timeout_seconds": ParamSchema(type="integer", description="Timeout in seconds", default=120, required=False),
            },
            returns=ReturnSchema(type="object", description="{returncode, stdout, stderr}"),
        )
        super().__init__("shell.execute", schema, RiskLevel.HIGH)

    def invoke(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        valid, err = self.validate_params(params)
        if not valid:
            return ToolResult(success=False, error=err)

        command = params.get("command", [])
        timeout = params.get("timeout_seconds", 120)

        if not command:
            return ToolResult(success=False, error="Command cannot be empty.")

        # Enforce context command policies
        if not context.command_allowed(command):
            return ToolResult(success=False, error="Command blocked by policy.")

        # Additional prefix check
        first = command[0].lower()
        if first not in self.SAFE_PREFIXES:
            return ToolResult(success=False, error=f"Command prefix '{first}' is not in the safe prefix list.")

        # Classify command
        policy = classify_command(command)
        if policy in {CommandPolicy.DESTRUCTIVE, CommandPolicy.DEPLOY}:
            return ToolResult(success=False, error=f"Command classified as {policy.value}; blocked.")

        try:
            result = subprocess.run(
                command,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            shell_result = ShellResult(
                command=command,
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )
            return ToolResult(
                success=True,
                data=shell_result,
                metadata={
                    "policy": policy.value,
                    "auto_runnable": can_auto_run(command),
                },
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error=f"Command timed out after {timeout}s")
        except FileNotFoundError:
            return ToolResult(success=False, error=f"Command not found: {command[0]}")
        except OSError as exc:
            return ToolResult(success=False, error=str(exc))
