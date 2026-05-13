"""ContextOps — Agentheim service interface for AICtx-derived context operations.

This module defines the boundary between Agentheim and the AICtx
package (`aictx`).  No code in `core/` should import from `aictx`
directly; instead it should use `ContextOps` (or the public façade that
wraps it).

M1 deliverable: interface definition + module map.
M2 deliverable: concrete implementation that delegates to AICtx internals.
M2.5 deliverable: expand ABC with init, clean, run_pipeline, public_docs_update.
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
    """Report from context write or pipeline run.

    M2.5 enrichment: carries AICtx telemetry when produced by
    ``run_pipeline`` so callers do not lose timing/entropy data.
    """

    generated_files: list[str] = field(default_factory=list)
    lockfile_path: str = ""
    patch_text: str = ""
    # Telemetry populated by run_pipeline()
    run_report: Any = None
    timing: Any = None
    entropy: Any = None


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


@dataclass
class CleanResult:
    """Result from a clean operation."""

    removed_count: int = 0
    kept_count: int = 0
    removed_paths: list[str] = field(default_factory=list)


class ContextOps(ABC):
    """Internal service interface for AICtx-derived context operations.

    Implementations live outside `core/` (e.g. in `agentheim/context_ops_impl.py`)
    and delegate to the `aictx` package.
    """

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    def init(self, repo_root: Path) -> None:
        """Initialize *repo_root* for context processing.

        Creates ``.aictxignore``, context directory, and baseline
        ``context.lock.json``.
        """
        ...

    @abstractmethod
    def clean(
        self,
        repo_root: Path,
        *,
        run_id: str | None = None,
        keep_runs: int | None = None,
    ) -> CleanResult:
        """Remove generated run artifacts.

        Either *run_id* (single run) or *keep_runs* (retain newest N)
        must be provided.  Returns counts of removed / kept paths.
        """
        ...

    # ------------------------------------------------------------------
    # Phase-1 context generation (granular)
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # End-to-end pipeline
    # ------------------------------------------------------------------

    @abstractmethod
    def run_pipeline(
        self,
        repo_root: Path,
        run_id: str,
        scope: str = "full",
        write_mode: str = "patch",
        allow_ai: bool = False,
        allow_dirty: bool = False,
    ) -> WriteReport:
        """Run the full local Phase-1 context generation pipeline.

        Returns a :class:`WriteReport` enriched with AICtx telemetry
        (``run_report``, ``timing``, ``entropy``).
        """
        ...

    # ------------------------------------------------------------------
    # Verification & status
    # ------------------------------------------------------------------

    @abstractmethod
    def verify(self, repo_root: Path, strict: bool = False) -> VerificationResult:
        """Verify context lock against current repository state."""
        ...

    @abstractmethod
    def status(self, repo_root: Path, strict: bool = False) -> ContextStatus:
        """Return stale-context detection status."""
        ...

    # ------------------------------------------------------------------
    # Public docs
    # ------------------------------------------------------------------

    @abstractmethod
    def public_docs_impact(
        self,
        repo_root: Path,
        scope: str = "full",
    ) -> PublicDocsImpactReport:
        """Map source changes to impacted public documentation."""
        ...

    @abstractmethod
    def public_docs_update(
        self,
        repo_root: Path,
        scope: str = "changed",
        write_mode: str = "patch",
    ) -> Path | None:
        """Generate patches for impacted public docs.

        Returns path to the generated patch, or ``None`` when no docs
        are impacted.
        """
        ...
