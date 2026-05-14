from __future__ import annotations

from pathlib import Path

from workflows.base import Workflow, Step, StepContext, StepResult, ExecutionDAG, AgentRole
from workflows.command_assistant.agents.base import load_prompt
from workflows.command_assistant.agents.parser import ParserAgent, ParsedIntent
from workflows.command_assistant.agents.generator import GeneratorAgent, GeneratedCommand
from core.public_api import ModelRegistry

WORKFLOW_ID = "command_assistant"


def _prompt_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "prompts"


def create_parser_agent(registry: ModelRegistry) -> ParserAgent:
    model = registry.resolve_model("planner", "plan")
    provider = registry.create_provider(model.config)
    return ParserAgent(
        provider=provider,
        role_config=model.config,
        system_prompt=load_prompt(_prompt_dir() / "parser" / "system.md"),
        output_schema=ParsedIntent,
    )


def create_generator_agent(registry: ModelRegistry) -> GeneratorAgent:
    model = registry.resolve_model("executor", "code_edit")
    provider = registry.create_provider(model.config)
    return GeneratorAgent(
        provider=provider,
        role_config=model.config,
        system_prompt=load_prompt(_prompt_dir() / "generator" / "system.md"),
        output_schema=GeneratedCommand,
    )


class CommandAssistantWorkflow(Workflow):
    workflow_id = WORKFLOW_ID
    support_state = "stable_candidate"
    required_agents = [
        AgentRole(id="parser", capabilities=["parse"]),
        AgentRole(id="generator", capabilities=["generate"]),
    ]

    def __init__(self, model_registry, tool_registry, policy_engine, ledger):
        super().__init__(model_registry, tool_registry, policy_engine, ledger)
        self.parser = create_parser_agent(model_registry)
        self.generator = create_generator_agent(model_registry)
        self.dag = ExecutionDAG([
            Step(id="parse", agent="parser", type="parse"),
            Step(id="generate", agent="generator", type="generate", depends_on=["parse"]),
        ])

    def execute_step(self, step: Step, context: StepContext) -> StepResult:
        if step.agent == "parser":
            user_input = context.metadata.get("user_input", "")
            result = self.parser.run_parse(user_input)
            return StepResult(step_id=step.id, success=result.success, output=result.raw_output)
        elif step.agent == "generator":
            parsed = context.prior_results.get("parse", StepResult(step_id="parse", success=True, output="")).output
            result = self.generator.run_generate(parsed)
            return StepResult(step_id=step.id, success=result.success, output=result.raw_output)
        return StepResult(step_id=step.id, success=False, output="Unknown agent")
