from __future__ import annotations

from pathlib import Path
from typing import Any

from workflows.base import AgentRole, ExecutionDAG, Step, StepContext, StepResult, Workflow
from workflows.documents.agents.base import load_prompt
from workflows.documents.agents.indexer import IndexerAgent, IndexerOutput
from workflows.documents.agents.retriever import RetrieverAgent, RetrieverOutput
from workflows.documents.agents.answerer import AnswerAgent, AnswererOutput
from core.public_api import ModelRegistry


WORKFLOW_ID = "documents"


def _prompt_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "prompts"


def _collect_text_files(repo_root: Path) -> list[Path]:
    excluded = {
        ".git",
        ".ai-team",
        ".pytest_cache",
        "node_modules",
        "__pycache__",
        "dist",
        "build",
        ".venv",
        ".next",
        "coverage",
    }
    excluded_suffixes = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".zip",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".pdf",
    }
    results: list[Path] = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root)
        if any(part in excluded for part in rel.parts):
            continue
        if path.suffix.lower() in excluded_suffixes:
            continue
        results.append(rel)
    return sorted(results)


def create_indexer_agent(registry: ModelRegistry) -> IndexerAgent:
    model = registry.resolve_model("indexer", "file_read")
    provider = registry.create_provider(model.config)
    prompt_path = _prompt_dir() / "indexer" / "system.md"
    return IndexerAgent(
        provider=provider,
        role_config=model.config,
        system_prompt=load_prompt(prompt_path),
        output_schema=IndexerOutput,
    )


def create_retriever_agent(registry: ModelRegistry) -> RetrieverAgent:
    model = registry.resolve_model("retriever", "search")
    provider = registry.create_provider(model.config)
    prompt_path = _prompt_dir() / "retriever" / "system.md"
    return RetrieverAgent(
        provider=provider,
        role_config=model.config,
        system_prompt=load_prompt(prompt_path),
        output_schema=RetrieverOutput,
    )


def create_answerer_agent(registry: ModelRegistry) -> AnswerAgent:
    model = registry.resolve_model("answerer", "synthesize")
    provider = registry.create_provider(model.config)
    prompt_path = _prompt_dir() / "answerer" / "system.md"
    return AnswerAgent(
        provider=provider,
        role_config=model.config,
        system_prompt=load_prompt(prompt_path),
        output_schema=AnswererOutput,
    )


class DocumentsWorkflow(Workflow):
    workflow_id = WORKFLOW_ID
    required_agents = [
        AgentRole(id="indexer", capabilities=["file_read", "embedding_index"]),
        AgentRole(id="retriever", capabilities=["search", "summarize"]),
        AgentRole(id="answerer", capabilities=["synthesize", "cite"]),
    ]

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
                Step(id="index", agent="indexer", type="index"),
                Step(id="retrieve", agent="retriever", type="retrieve", depends_on=["index"]),
                Step(id="answer", agent="answerer", type="answer", depends_on=["retrieve"]),
            ]
        )

    def execute_step(self, step: Step, context: StepContext) -> StepResult:
        if step.id == "index":
            return self._execute_index(step, context)
        if step.id == "retrieve":
            return self._execute_retrieve(step, context)
        if step.id == "answer":
            return self._execute_answer(step, context)
        return StepResult(step_id=step.id, success=False, output=f"Unknown step {step.id}")

    def _execute_index(self, step: Step, context: StepContext) -> StepResult:
        repo_root = context.repo_root
        file_paths = _collect_text_files(repo_root)[:50]

        agent = create_indexer_agent(self.model_registry)
        result = agent.run_index(repo_root, file_paths)

        file_contents: dict[str, str] = {}
        for rel in file_paths:
            try:
                file_contents[rel.as_posix()] = (repo_root / rel).read_text(
                    encoding="utf-8", errors="ignore"
                )
            except Exception:
                file_contents[rel.as_posix()] = ""

        metadata: dict[str, Any] = {"file_contents": file_contents}
        if result.parsed_output is not None:
            metadata["parsed"] = result.parsed_output

        return StepResult(
            step_id=step.id,
            success=result.success,
            output=result.raw_output,
            metadata=metadata,
        )

    def _execute_retrieve(self, step: Step, context: StepContext) -> StepResult:
        query = context.metadata.get("query", "")
        prior = context.prior_results.get("index")
        if prior is None:
            return StepResult(step_id=step.id, success=False, output="Missing index result")

        file_contents = prior.metadata.get("file_contents", {})
        agent = create_retriever_agent(self.model_registry)
        result = agent.run_retrieve(query, file_contents)

        metadata: dict[str, Any] = {}
        if result.parsed_output is not None:
            metadata["parsed"] = result.parsed_output

        return StepResult(
            step_id=step.id,
            success=result.success,
            output=result.raw_output,
            metadata=metadata,
        )

    def _execute_answer(self, step: Step, context: StepContext) -> StepResult:
        query = context.metadata.get("query", "")
        prior = context.prior_results.get("retrieve")
        if prior is None:
            return StepResult(step_id=step.id, success=False, output="Missing retrieve result")

        chunks: list[dict[str, Any]] = []
        parsed = prior.metadata.get("parsed", {})
        if isinstance(parsed, dict):
            chunks = parsed.get("chunks", [])
        agent = create_answerer_agent(self.model_registry)
        result = agent.run_answer(query, chunks)

        metadata: dict[str, Any] = {}
        if result.parsed_output is not None:
            metadata["parsed"] = result.parsed_output

        return StepResult(
            step_id=step.id,
            success=result.success,
            output=result.raw_output,
            metadata=metadata,
        )

    def generate_report(self, results: list[StepResult]) -> str:
        lines = [f"# Workflow Report: {self.workflow_id}", ""]
        for r in results:
            status = "PASS" if r.success else "FAIL"
            lines.append(f"- **{r.step_id}**: {status}")
            if r.output:
                lines.append(f"  {r.output[:200]}")
        return "\n".join(lines)
