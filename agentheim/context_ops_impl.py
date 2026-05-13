"""Concrete ContextOps implementation delegating to AICtx internals.

M2 deliverable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentheim.context_ops import (
    ContextOps,
    ContextPlan,
    ContextStatus,
    GeneratedContext,
    PublicDocsImpactReport,
    RepositoryInventory,
    VerificationResult,
    WriteReport,
)
from agentheim.vendor.aictx.config import AictxConfig
from agentheim.vendor.aictx.context.fact_extractor import extract_facts
from agentheim.vendor.aictx.context.lockfile import load_lockfile, write_lockfile
from agentheim.vendor.aictx.context.planner import plan_context
from agentheim.vendor.aictx.context.pipeline import _build_patch
from agentheim.vendor.aictx.context.writer import build_context_lock, write_context_scaffold
from agentheim.vendor.aictx.llm.providers import create_model_provider
from agentheim.vendor.aictx.models.inventory import RepositoryInventory as AictxRepositoryInventory
from agentheim.vendor.aictx.public_docs.mapper import build_public_docs_map
from agentheim.vendor.aictx.scan.scanner import scan_repository
from agentheim.vendor.aictx.verify.verifier import verify_detailed


class AictxContextOps(ContextOps):
    """Delegate ContextOps methods to AICtx internals."""

    def __init__(self, config: AictxConfig | None = None) -> None:
        self.config = config or AictxConfig()

    def scan(self, repo_root: Path) -> RepositoryInventory:
        raw = scan_repository(repo_root)
        return RepositoryInventory(raw=raw)

    def plan(
        self,
        inventory: RepositoryInventory,
        scope: str = "full",
        existing_lock: Any | None = None,
    ) -> ContextPlan:
        repo_root = Path(inventory.repo_root) if inventory.repo_root else Path.cwd()
        context_dir = repo_root / self.config.project.context_dir
        agents_md = repo_root / self.config.project.agents_file
        plan_dict = plan_context(
            inventory=inventory.raw,
            existing_context_dir=context_dir if context_dir.exists() else None,
            existing_agents_md=agents_md if agents_md.exists() else None,
            scope=scope,
            config=self.config,
            existing_lock=existing_lock,
            changed_files=[],
        )
        return ContextPlan(raw=plan_dict)

    def generate(
        self,
        repo_root: Path,
        plan: ContextPlan,
        provider: Any | None = None,
    ) -> GeneratedContext:
        if provider is None:
            provider = create_model_provider(self.config.llm, allow_ai=False)
        fact_packs = extract_facts(
            repo_root=repo_root,
            plan=plan.raw,
            provider=provider,
            run_id="agentheim-ctx",
        )
        return GeneratedContext(
            plan=plan,
            fact_packs=fact_packs,
            repo_root=repo_root,
        )

    def write(
        self,
        repo_root: Path,
        context: GeneratedContext,
        write_mode: str = "patch",
    ) -> WriteReport:
        from agentheim.vendor.aictx.io.files import safe_write

        # Re-scan to get fresh inventory for lockfile
        inventory_raw = scan_repository(repo_root)
        out_dir = repo_root / ".aictx" / "runs" / "agentheim-ctx" / "out"
        out_dir.mkdir(parents=True, exist_ok=True)

        generated_paths = write_context_scaffold(
            repo_root=repo_root,
            out_dir=out_dir,
            inventory=inventory_raw,
            plan=context.plan.raw,
            fact_packs=context.fact_packs,
        )

        lock = build_context_lock(
            repo_root=repo_root,
            out_dir=out_dir,
            inventory=inventory_raw,
            plan=context.plan.raw,
            fact_packs=context.fact_packs,
            generated_paths=generated_paths,
            model_provider=self.config.llm.provider,
            model_name=self.config.llm.model,
            existing_lock=None,
            changed_files=[],
            preserve_existing_sections=False,
        )

        staged_context_dir = out_dir / self.config.project.context_dir
        write_lockfile(staged_context_dir, lock)
        generated_paths.append(staged_context_dir / "context.lock.json")

        patch_text = _build_patch(repo_root=repo_root, out_dir=out_dir)
        patch_path = repo_root / ".aictx" / "runs" / "agentheim-ctx" / "aictx.patch"
        safe_write(patch_path, patch_text)

        if write_mode == "apply":
            from agentheim.vendor.aictx.context.pipeline import _apply_out_dir
            _apply_out_dir(repo_root=repo_root, out_dir=out_dir)

        return WriteReport(
            generated_files=[p.relative_to(out_dir).as_posix() for p in generated_paths],
            lockfile_path=f"{self.config.project.context_dir}/context.lock.json",
            patch_text=patch_text,
        )

    def verify(self, repo_root: Path, strict: bool = False) -> VerificationResult:
        report = verify_detailed(repo_root, strict=strict)
        return VerificationResult(
            result=report.result,
            is_pass=report.result == "PASS",
            raw=report,
        )

    def status(self, repo_root: Path, strict: bool = False) -> ContextStatus:
        report = verify_detailed(repo_root, strict=strict)
        return ContextStatus(
            is_stale=report.result != "PASS",
            stale_sources=report.stale_sources,
            missing_sources=report.missing_sources,
            missing_generated=report.missing_generated,
            generated_mismatches=report.generated_mismatches,
            public_docs_impacts=report.public_docs_impacts,
            next_command=report.next_command,
        )

    def public_docs_impact(
        self,
        repo_root: Path,
        scope: str = "full",
    ) -> PublicDocsImpactReport:
        docs_map = build_public_docs_map(repo_root)
        return PublicDocsImpactReport(
            entries=[entry.model_dump(mode="json") for entry in docs_map.entries],
            raw=docs_map,
        )
