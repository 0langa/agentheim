from __future__ import annotations

from pathlib import Path
from typing import Any

from core.public_api import ModelDescriptor, ModelRegistry, PolicyEngine, RunLedger, ToolRegistry
from workflows.base import AgentRole, ExecutionDAG, Step, StepContext, StepResult, Workflow
from workflows.file_organization.agents.analyzer import AnalyzerAgent, AnalyzerResult
from workflows.file_organization.agents.applier import ApplierAgent, ApplierResult
from workflows.file_organization.agents.base import load_prompt
from workflows.file_organization.agents.proposer import ProposerAgent, ProposerResult


class FileOrganizationWorkflow(Workflow):
    workflow_id = "file_organization"
    required_agents = [
        AgentRole(id="analyzer", capabilities=["scan", "classify"]),
        AgentRole(id="proposer", capabilities=["plan", "structure"]),
        AgentRole(id="applier", capabilities=["move", "rename"]),
    ]

    def __init__(
        self,
        model_registry: ModelRegistry,
        tool_registry: ToolRegistry,
        policy_engine: PolicyEngine,
        ledger: RunLedger,
    ) -> None:
        super().__init__(model_registry, tool_registry, policy_engine, ledger)
        self.dag = ExecutionDAG([
            Step(id="analyze", agent="analyzer", type="analyze", workspace_isolation=False),
            Step(id="propose", agent="proposer", type="propose", depends_on=["analyze"], workspace_isolation=False),
            Step(id="preview", agent="proposer", type="preview", depends_on=["propose"], workspace_isolation=False),
            Step(id="apply", agent="applier", type="apply", depends_on=["preview"], workspace_isolation=False),
        ])

        prompt_dir = Path(__file__).resolve().parent.parent / "prompts"

        analyzer_model = self._resolve_agent_model("indexer", ["file_read", "scan"])
        self._analyzer = AnalyzerAgent(
            provider=model_registry.create_provider(analyzer_model.config),
            role_config=analyzer_model.config,
            system_prompt=load_prompt(prompt_dir / "analyzer" / "system.md"),
            output_schema=AnalyzerResult,
        )

        proposer_model = self._resolve_agent_model("planner", ["plan", "structure"])
        self._proposer = ProposerAgent(
            provider=model_registry.create_provider(proposer_model.config),
            role_config=proposer_model.config,
            system_prompt=load_prompt(prompt_dir / "proposer" / "system.md"),
            output_schema=ProposerResult,
        )

        applier_model = self._resolve_agent_model("executor", ["code_edit", "move"])
        self._applier = ApplierAgent(
            provider=model_registry.create_provider(applier_model.config),
            role_config=applier_model.config,
            system_prompt=load_prompt(prompt_dir / "applier" / "system.md"),
            output_schema=ApplierResult,
        )

    def _resolve_agent_model(self, role: str, capabilities: list[str]) -> ModelDescriptor:
        last_error: Exception | None = None
        for cap in capabilities:
            try:
                return self.model_registry.resolve_model(role, cap)
            except ValueError as exc:
                last_error = exc
                continue
        # Fallback: search all roles for any matching capability
        for cap in capabilities:
            try:
                return self._resolve_any_role(cap)
            except ValueError:
                continue
        raise ValueError(
            f"No model found for role '{role}' with any capability in {capabilities}."
        ) from last_error

    def _resolve_any_role(self, capability: str) -> ModelDescriptor:
        for model in self.model_registry._models.values():
            if capability in model.capabilities:
                return ModelDescriptor(config=model, role=model.role, capability=capability)
        raise ValueError(f"No model found with capability '{capability}'.")

    def execute_step(self, step: Step, context: StepContext) -> StepResult:
        if step.id == "analyze":
            return self._execute_analyze(context)
        elif step.id == "propose":
            return self._execute_propose(context)
        elif step.id == "preview":
            return self._execute_preview(context)
        elif step.id == "apply":
            return self._execute_apply(context)
        return StepResult(step_id=step.id, success=False, output=f"Unknown step: {step.id}")

    def _execute_analyze(self, context: StepContext) -> StepResult:
        target_dir = Path(context.metadata.get("target_dir", context.repo_root))
        try:
            files = [str(f.relative_to(target_dir)) for f in target_dir.rglob("*") if f.is_file()]
        except Exception as exc:
            return StepResult(step_id="analyze", success=False, output=f"Failed to list directory: {exc}")

        prompt = self._analyzer.build_analyze_prompt(str(target_dir), files)
        result = self._analyzer.run_structured(prompt, max_output_tokens=2000)
        return StepResult(
            step_id="analyze",
            success=result.success,
            output=result.raw_output,
            metadata={"parsed": result.parsed_output} if result.parsed_output else {"error": result.error},
        )

    def _execute_propose(self, context: StepContext) -> StepResult:
        prior = context.prior_results.get("analyze")
        if not prior or not prior.success:
            return StepResult(step_id="propose", success=False, output="Missing or failed analyze step")

        parsed = prior.metadata.get("parsed")
        if not parsed:
            return StepResult(step_id="propose", success=False, output="No parsed analyze output")

        analysis = AnalyzerResult.model_validate(parsed)
        prompt = self._proposer.build_propose_prompt(analysis, str(context.metadata.get("task", "")))
        result = self._proposer.run_structured(prompt, max_output_tokens=2000)
        return StepResult(
            step_id="propose",
            success=result.success,
            output=result.raw_output,
            metadata={"parsed": result.parsed_output} if result.parsed_output else {"error": result.error},
        )

    def _execute_preview(self, context: StepContext) -> StepResult:
        prior = context.prior_results.get("propose")
        if not prior or not prior.success:
            return StepResult(step_id="preview", success=False, output="Missing or failed propose step")

        parsed = prior.metadata.get("parsed")
        if not parsed:
            return StepResult(step_id="preview", success=False, output="No parsed propose output")

        proposal = ProposerResult.model_validate(parsed)
        prompt = self._proposer.build_preview_prompt(proposal, str(context.metadata.get("task", "")))
        result = self._proposer.run_structured(prompt, max_output_tokens=2000)
        return StepResult(
            step_id="preview",
            success=result.success,
            output=result.raw_output,
            metadata={"parsed": result.parsed_output} if result.parsed_output else {"error": result.error},
        )

    def _execute_apply(self, context: StepContext) -> StepResult:
        propose_result = context.prior_results.get("propose")
        if not propose_result or not propose_result.success:
            return StepResult(step_id="apply", success=False, output="Missing or failed propose step")

        parsed_propose = propose_result.metadata.get("parsed")
        if not parsed_propose:
            return StepResult(step_id="apply", success=False, output="No parsed propose output")

        proposal = ProposerResult.model_validate(parsed_propose)
        prompt = self._applier.build_apply_prompt(proposal, context.repo_root, str(context.metadata.get("task", "")))
        result = self._applier.run_structured(prompt, max_output_tokens=2000)

        moves_executed: list[dict[str, Any]] = []
        dry_run = context.metadata.get("dry_run", False)

        if result.success and result.parsed_output:
            applier_result = ApplierResult.model_validate(result.parsed_output)
            for move in applier_result.moves:
                if dry_run:
                    moves_executed.append(move.model_dump())
                    continue
                try:
                    src = Path(context.repo_root) / move.source
                    dst = Path(context.repo_root) / move.target
                    if not src.exists():
                        moves_executed.append(
                            {**move.model_dump(), "success": False, "error": "Source file does not exist"}
                        )
                        continue
                    if self.ledger:
                        self.ledger.append_jsonl(
                            "file_changes.jsonl",
                            {"operation": "rename", "source": str(src), "target": str(dst)},
                        )
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    src.rename(dst)
                    moves_executed.append({**move.model_dump(), "success": True, "error": ""})
                except Exception as exc:
                    moves_executed.append({**move.model_dump(), "success": False, "error": str(exc)})
        else:
            moves_executed = [
                {"source": a.source, "target": a.target, "success": False, "error": "Applier agent failed"}
                for a in proposal.actions
            ]

        return StepResult(
            step_id="apply",
            success=result.success,
            output=result.raw_output,
            metadata={
                "parsed": result.parsed_output,
                "moves_executed": moves_executed,
            } if result.parsed_output else {"error": result.error, "moves_executed": moves_executed},
        )
