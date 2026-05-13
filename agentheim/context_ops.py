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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


@dataclass
class RepositoryInventory:
    """Placeholder — forwarded from AICtx `models.inventory`."""

    pass


@dataclass
class ContextPlan:
    """Placeholder — forwarded from AICtx planner output."""

    pass


@dataclass
class GeneratedContext:
    """Placeholder — forwarded from AICtx writer output."""

    pass


@dataclass
class WriteReport:
    """Placeholder — forwarded from AICtx write result."""

    pass


@dataclass
class VerificationResult:
    """Placeholder — forwarded from AICtx verifier output."""

    pass


@dataclass
class ContextStatus:
    """Placeholder — forwarded from AICtx status output."""

    pass


@dataclass
class PublicDocsImpactReport:
    """Placeholder — forwarded from AICtx public-docs mapper output."""

    pass


class ContextOps(ABC):
    """Internal service interface for AICtx-derived context operations.

    Implementations live outside `core/` (e.g. in a future
    `agentheim/context_ops_impl.py`) and delegate to
    `agentheim.vendor.aictx` domain modules.
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
