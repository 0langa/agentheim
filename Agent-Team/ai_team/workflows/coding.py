from __future__ import annotations

from pathlib import Path

from ai_team.agents.base import load_prompt
from ai_team.agents.coder import CoderAgent
from ai_team.agents.orchestrator import OrchestratorAgent
from ai_team.agents.verifier import VerifierAgent
from ai_team.core.model_registry import ModelRegistry
from ai_team.schemas import ImplementationPlan, PatchPlan, VerificationReport

WORKFLOW_ID = "coding"


def _prompt_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "prompts"


def create_orchestrator_agent(registry: ModelRegistry) -> OrchestratorAgent:
    model = registry.resolve_model("planner", "plan")
    provider = registry.create_provider(model.config)
    prompt_path = _prompt_dir() / "orchestrator" / "system.md"
    return OrchestratorAgent(
        provider=provider,
        role_config=model.config,
        system_prompt=load_prompt(prompt_path),
        output_schema=ImplementationPlan,
    )


def create_coder_agent(registry: ModelRegistry) -> CoderAgent:
    model = registry.resolve_model("executor", "code_edit")
    provider = registry.create_provider(model.config)
    prompt_path = _prompt_dir() / "coder" / "system.md"
    return CoderAgent(
        provider=provider,
        role_config=model.config,
        system_prompt=load_prompt(prompt_path),
        output_schema=PatchPlan,
    )


def create_verifier_agent(registry: ModelRegistry) -> VerifierAgent:
    model = registry.resolve_model("verifier", "verify")
    provider = registry.create_provider(model.config)
    prompt_path = _prompt_dir() / "verifier" / "system.md"
    return VerifierAgent(
        provider=provider,
        role_config=model.config,
        system_prompt=load_prompt(prompt_path),
        output_schema=VerificationReport,
    )
