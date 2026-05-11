"""Workflow adapters — bridge Phase 2 shim API to Phase 3 core protocols.

These thin wrappers let the existing runtime code keep its calling conventions
while routing through the new mediated tool and policy system.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.ledger import RunLedger
from core.model_registry import ModelDescriptor, ModelRegistry
from core.policy_engine import PolicyConfig, PolicyEngine
from core.tool_protocol import ToolContext, ToolRegistry as CoreToolRegistry, ToolResult


def model_resolve(registry: ModelRegistry, role: str, required_capability: str) -> ModelDescriptor:
    """Resolve a role + capability to a model descriptor."""
    return registry.resolve_model(role, required_capability)


def ledger_append(ledger: RunLedger, name: str, payload: dict[str, Any]) -> None:
    """Append a payload to a JSON-lines artifact."""
    ledger.append_jsonl(name, payload)


# Cache tool registries and policy engines per repo root
_tool_registries: dict[Path, CoreToolRegistry] = {}
_policy_engines: dict[Path, PolicyEngine] = {}


def _get_tool_registry(repo_root: Path) -> CoreToolRegistry:
    """Lazy-load a ToolRegistry with all standard tools."""
    repo_root = repo_root.resolve()
    if repo_root not in _tool_registries:
        registry = CoreToolRegistry()

        from tools.filesystem import FilesystemTool
        from tools.git import GitTool
        from tools.http import HttpTool
        from tools.memory import MemoryTool
        from tools.shell import ShellTool

        registry.register(FilesystemTool(repo_root))
        registry.register(ShellTool(repo_root))
        registry.register(GitTool(repo_root))
        registry.register(HttpTool())
        registry.register(MemoryTool())

        _tool_registries[repo_root] = registry
    return _tool_registries[repo_root]


def _get_policy_engine(repo_root: Path) -> PolicyEngine:
    """Lazy-load a PolicyEngine with default config."""
    repo_root = repo_root.resolve()
    if repo_root not in _policy_engines:
        config = PolicyConfig(
            path_boundaries_allowed=[str(repo_root)],
            command_allowlist=["git", "python", "pytest", "dotnet", "cargo", "go", "npm", "node", "pip", "poetry"],
            command_denylist=["rm -rf /", "sudo", "chmod 777", "mkfs", "dd"],
            network_allowed=False,
            delete_allowed=False,
        )
        _policy_engines[repo_root] = PolicyEngine(config)
    return _policy_engines[repo_root]


def _make_context(repo_root: Path) -> ToolContext:
    """Create a ToolContext for the given repo root."""
    return ToolContext(
        allowed_paths=[str(repo_root)],
        denied_paths=[str(repo_root / ".git"), str(repo_root / ".ai-team" / "run.lock")],
        workspace=repo_root,
    )


def tool_invoke(
    tool_name: str,
    *,
    repo_root: Path | None = None,
    **kwargs: Any,
) -> Any:
    """Invoke a tool by name (Phase 2 shim API preserved).

    Under the hood this routes through ToolRegistry + PolicyEngine.
    """
    if repo_root is None:
        raise ValueError("repo_root is required for tool invocation")

    registry = _get_tool_registry(repo_root)
    policy = _get_policy_engine(repo_root)
    context = _make_context(repo_root)

    tool = registry.get(tool_name)

    # Evaluate policy
    decision = policy.evaluate(tool_name, kwargs, context, tool.risk_level)
    if decision.decision == "deny":
        raise RuntimeError(f"Tool '{tool_name}' denied by policy: {decision.reason}")
    if decision.decision == "ask":
        # In non-interactive mode, deny asks for HIGH/CRITICAL, allow MEDIUM
        if decision.risk_level.value in {"high", "critical"}:
            raise RuntimeError(f"Tool '{tool_name}' requires approval: {decision.reason}")

    result = tool.invoke(kwargs, context)
    if not result.success:
        raise RuntimeError(f"Tool '{tool_name}' failed: {result.error}")

    return result.data


def policy_evaluate(command: list[str], context: dict | None = None) -> dict:
    """Evaluate a command against the policy engine (Phase 2 shim API preserved).

    Returns a dict matching the canonical PolicyDecision shape:
        { "decision": "allow" | "block" | "prompt", "policy": "...", "reason": "..." }
    """
    from core.policies import CommandPolicy, classify_command

    policy = classify_command(command)
    if policy == CommandPolicy.SAFE:
        return {
            "decision": "allow",
            "policy": policy.value,
            "reason": "Command classified as safe for automatic execution.",
        }
    if policy == CommandPolicy.INSTALL:
        return {
            "decision": "prompt",
            "policy": policy.value,
            "reason": "Installation command requires user confirmation.",
        }
    if policy in {CommandPolicy.DESTRUCTIVE, CommandPolicy.DEPLOY}:
        return {
            "decision": "block",
            "policy": policy.value,
            "reason": f"Command classified as {policy.value}; blocked by safety policy.",
        }
    return {
        "decision": "block",
        "policy": policy.value,
        "reason": "Unknown policy classification; blocked by default.",
    }
