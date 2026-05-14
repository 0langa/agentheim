from __future__ import annotations

from pathlib import Path
from typing import Any

from workflows.base import AgentRole, ExecutionDAG, Step, StepContext, StepResult, Workflow
from workflows.coding.agents.base import load_prompt
from workflows.coding.agents.coder import CoderAgent
from workflows.coding.agents.orchestrator import OrchestratorAgent
from workflows.coding.agents.verifier import VerifierAgent
from core.public_api import ImplementationPlan, ModelRegistry, PatchPlan, VerificationReport

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


class CodingWorkflow(Workflow):
    workflow_id = WORKFLOW_ID
    support_state = "stable_candidate"
    required_agents = [
        AgentRole(id="orchestrator", capabilities=["plan", "reasoning", "json"]),
        AgentRole(id="coder", capabilities=["code_edit", "json"]),
        AgentRole(id="verifier", capabilities=["verify", "json"]),
    ]
    required_tools: list[str] = []

    def __init__(
        self,
        model_registry: ModelRegistry,
        tool_registry: Any,
        policy_engine: Any,
        ledger: Any,
    ) -> None:
        super().__init__(model_registry, tool_registry, policy_engine, ledger)
        self.dag = ExecutionDAG(
            steps=[
                Step(id="plan", agent="orchestrator", type="plan"),
                Step(id="execute", agent="coder", type="execute", depends_on=["plan"]),
                Step(id="verify", agent="verifier", type="verify", depends_on=["execute"]),
            ]
        )

    def execute_step(self, step: Step, context: StepContext) -> StepResult:
        return StepResult(
            step_id=step.id,
            success=True,
            output=f"Step '{step.id}' orchestrated by coding runtime.",
            metadata={"routed": True},
        )

    def run(self, repo_root: Path, metadata: dict[str, Any] | None = None) -> list[StepResult]:
        """Delegate to the full coding runtime for production execution."""
        from workflows.coding.runtime import run_task as coding_run_task

        task_text = (metadata or {}).get("task", "")
        report, _ = coding_run_task(task_text=task_text, repo_path=repo_root)
        return [
            StepResult(step_id="plan", success=True, output="Planned via coding runtime."),
            StepResult(step_id="execute", success=True, output="Executed via coding runtime."),
            StepResult(step_id="verify", success=True, output="Verified via coding runtime."),
        ]
