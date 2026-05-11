from __future__ import annotations

from pathlib import Path

from workflows.base import Workflow, Step, StepContext, StepResult, ExecutionDAG, AgentRole
from workflows.github_maintenance.agents.base import load_prompt
from workflows.github_maintenance.agents.summarizer import SummarizerAgent, SummaryResult
from workflows.github_maintenance.agents.drafter import DrafterAgent, DraftResult
from core.public_api import ModelRegistry

WORKFLOW_ID = "github_maintenance"


def _prompt_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "prompts"


def create_summarizer_agent(registry: ModelRegistry) -> SummarizerAgent:
    model = registry.resolve_model("planner", "plan")
    provider = registry.create_provider(model.config)
    return SummarizerAgent(
        provider=provider,
        role_config=model.config,
        system_prompt=load_prompt(_prompt_dir() / "summarizer" / "system.md"),
        output_schema=SummaryResult,
    )


def create_drafter_agent(registry: ModelRegistry) -> DrafterAgent:
    model = registry.resolve_model("executor", "code_edit")
    provider = registry.create_provider(model.config)
    return DrafterAgent(
        provider=provider,
        role_config=model.config,
        system_prompt=load_prompt(_prompt_dir() / "drafter" / "system.md"),
        output_schema=DraftResult,
    )


class GitHubMaintenanceWorkflow(Workflow):
    workflow_id = WORKFLOW_ID
    required_agents = [
        AgentRole(id="summarizer", capabilities=["summarize"]),
        AgentRole(id="drafter", capabilities=["draft"]),
    ]

    def __init__(self, model_registry, tool_registry, policy_engine, ledger):
        super().__init__(model_registry, tool_registry, policy_engine, ledger)
        self.summarizer = create_summarizer_agent(model_registry)
        self.drafter = create_drafter_agent(model_registry)
        self.dag = ExecutionDAG([
            Step(id="summarize", agent="summarizer", type="summarize"),
            Step(id="draft", agent="drafter", type="draft", depends_on=["summarize"]),
        ])

    def execute_step(self, step: Step, context: StepContext) -> StepResult:
        if step.agent == "summarizer":
            issues_text = context.metadata.get("issues_text", "")
            result = self.summarizer.run_summary(issues_text)
            return StepResult(step_id=step.id, success=result.success, output=result.raw_output)
        elif step.agent == "drafter":
            summary = context.prior_results.get("summarize", StepResult(step_id="summarize", success=True, output="")).output
            result = self.drafter.run_draft(summary)
            return StepResult(step_id=step.id, success=result.success, output=result.raw_output)
        return StepResult(step_id=step.id, success=False, output="Unknown agent")
