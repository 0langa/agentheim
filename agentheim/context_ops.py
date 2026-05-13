"""ContextOps — Agentheim service interface for AICtx-derived context operations.

This module defines the boundary between Agentheim and the imported AICtx
subsystem (`agentheim.vendor.aictx`).  No code in `core/` should import from
`agentheim.vendor.aictx` directly; instead it should use `ContextOps` (or the
public façade that wraps it).

M1 deliverable: interface definition + module map.
M2 deliverable: concrete implementation that delegates to AICtx internals.
M7 deliverable: provider calls routed through Agentheim `providers/base.py`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RepositoryInventory:
    """Thin wrapper — forwards from AICtx `models.inventory`."""

    raw: Any = None

    @property
    def repo_root(self) -> str:
        return self.raw.repo_root if self.raw else ""

    @property
    def head_commit(self) -> str:
        return self.raw.head_commit if self.raw else ""


@dataclass
class ContextPlan:
    """Thin wrapper — forwards from AICtx planner output."""

    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def selected_files(self) -> list[str]:
        return self.raw.get("selected_files", [])


@dataclass
class GeneratedContext:
    """Container for generated context artifacts."""

    plan: ContextPlan = field(default_factory=ContextPlan)
    fact_packs: list[dict[str, Any]] = field(default_factory=list)
    inventory: RepositoryInventory = field(default_factory=RepositoryInventory)
    repo_root: Path | None = None


@dataclass
class WriteReport:
    """Report from context write operation."""

    generated_files: list[str] = field(default_factory=list)
    lockfile_path: str = ""
    patch_text: str = ""


@dataclass
class VerificationResult:
    """Result from context verification."""

    result: str = ""
    is_pass: bool = False
    raw: Any = None


@dataclass
class ContextStatus:
    """Status from stale-context detection."""

    is_stale: bool = False
    stale_sources: list[str] = field(default_factory=list)
    missing_sources: list[str] = field(default_factory=list)
    missing_generated: list[str] = field(default_factory=list)
    generated_mismatches: list[str] = field(default_factory=list)
    public_docs_impacts: dict[str, list[str]] = field(default_factory=dict)
    next_command: str | None = None


@dataclass
class PublicDocsImpactReport:
    """Report from public-docs impact mapping."""

    entries: list[dict[str, Any]] = field(default_factory=list)
    raw: Any = None


class ContextOps(ABC):
    """Internal service interface for AICtx-derived context operations.

    Implementations live outside `core/` (e.g. in `agentheim/context_ops_impl.py`)
    and delegate to `agentheim.vendor.aictx` domain modules.
    """

    @abstractmethod
    def scan(self, repo_root: Path) -> RepositoryInventory:
        """Produce a repository inventory."""
        ...

    @abstractmethod
    def plan(
        self,
        inventory: RepositoryInventory,
        scope: str = "full",
        existing_lock: Any | None = None,
    ) -> ContextPlan:
        """Plan context generation for the given inventory."""
        ...

    @abstractmethod
    def generate(
        self,
        repo_root: Path,
        plan: ContextPlan,
        provider: Any | None = None,
    ) -> GeneratedContext:
        """Generate deterministic context shards."""
        ...

    @abstractmethod
    def write(
        self,
        repo_root: Path,
        context: GeneratedContext,
        write_mode: str = "patch",
    ) -> WriteReport:
        """Write generated context to patch or working tree."""
        ...

    @abstractmethod
    def verify(self, repo_root: Path, strict: bool = False) -> VerificationResult:
        """Verify context lock against current repository state."""
        ...

    @abstractmethod
    def status(self, repo_root: Path, strict: bool = False) -> ContextStatus:
        """Return stale-context detection status."""
        ...

    @abstractmethod
    def public_docs_impact(
        self,
        repo_root: Path,
        scope: str = "full",
    ) -> PublicDocsImpactReport:
        """Map source changes to impacted public documentation."""
        ...
