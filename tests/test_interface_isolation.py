"""Tests that interface files import only from core.public_api (not core internals)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest


# Explicitly exempt files that have a documented justification for importing
# directly from core internals. New exemptions require an inline comment
# explaining why core.public_api cannot satisfy the need.
EXEMPT_FILES: dict[str, str] = {
    # Add justified exemptions here with a comment explaining why.
}


def _discover_interface_files() -> list[str]:
    """Return all Python files under interfaces/ as repo-relative POSIX paths."""
    repo_root = Path(__file__).parent.parent
    interface_dir = repo_root / "interfaces"
    return sorted(
        str(p.relative_to(repo_root)).replace("\\", "/")
        for p in interface_dir.rglob("*.py")
    )


def _collect_core_imports(source_path: Path) -> list[tuple[int, str]]:
    """Return (line_no, module_name) for all core.* imports in a file."""
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith("core."):
                imports.append((node.lineno, node.module))
    return imports


class TestInterfaceIsolation:
    @pytest.mark.parametrize("rel_path", _discover_interface_files())
    def test_no_direct_core_imports(self, rel_path: str) -> None:
        path = Path(__file__).parent.parent / rel_path
        if not path.exists():
            pytest.skip(f"{rel_path} does not exist")

        core_imports = _collect_core_imports(path)

        # Allowed: core.public_api itself
        disallowed = [(line, mod) for line, mod in core_imports if mod != "core.public_api"]

        if rel_path in EXEMPT_FILES:
            pytest.skip(f"{rel_path} is exempt: {EXEMPT_FILES[rel_path]}")

        assert not disallowed, (
            f"{rel_path} imports directly from core internals: "
            f"{[(line, mod) for line, mod in disallowed]}"
        )

    def test_public_api_has_all_needed_symbols(self) -> None:
        """Smoke test: ensure public_api can be imported and has key symbols."""
        from core import public_api

        required = [
            "RunLedger",
            "ModelRegistry",
            "PolicyEngine",
            "ToolRegistry",
            "RunExecutor",
            "Event",
            "WorkflowRunner",
        ]
        for name in required:
            assert hasattr(public_api, name), f"core.public_api missing {name}"
