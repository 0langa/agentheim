"""Tests for AictxContextOps M2 implementation.

Covers scan, plan, generate, write, verify, status, and public_docs_impact.
Uses dry_run LLM provider to avoid network calls.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentheim.context_ops_impl import AictxContextOps
from agentheim.vendor.aictx.config import AictxConfig
from agentheim.vendor.aictx.llm.dry_run import DryRunProvider

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def ops() -> AictxContextOps:
    config = AictxConfig()
    config.llm.provider = "dry_run"
    config.llm.model = "dry_run"
    return AictxContextOps(config=config)


# ------------------------------------------------------------------
# scan
# ------------------------------------------------------------------


def test_scan_returns_inventory(ops: AictxContextOps) -> None:
    inventory = ops.scan(REPO_ROOT)
    assert inventory.raw is not None
    assert inventory.repo_root == str(REPO_ROOT)
    assert len(inventory.raw.files) > 0


def test_inventory_has_manifests_and_docs(ops: AictxContextOps) -> None:
    inventory = ops.scan(REPO_ROOT)
    assert len(inventory.raw.manifests) > 0
    assert any(m.path == "pyproject.toml" for m in inventory.raw.manifests)
    assert len(inventory.raw.docs) > 0


# ------------------------------------------------------------------
# plan
# ------------------------------------------------------------------


def test_plan_returns_selected_files(ops: AictxContextOps) -> None:
    inventory = ops.scan(REPO_ROOT)
    plan = ops.plan(inventory, scope="full")
    assert len(plan.selected_files) > 0
    assert "pyproject.toml" in plan.selected_files or any(
        "pyproject" in f for f in plan.selected_files
    )


def test_plan_changed_scope(ops: AictxContextOps) -> None:
    inventory = ops.scan(REPO_ROOT)
    plan = ops.plan(inventory, scope="changed")
    # With no existing lockfile, changed scope falls back to changed_files=[]
    # so it may be empty or minimal
    assert isinstance(plan.selected_files, list)


# ------------------------------------------------------------------
# generate
# ------------------------------------------------------------------


def test_generate_with_dry_run(ops: AictxContextOps) -> None:
    inventory = ops.scan(REPO_ROOT)
    plan = ops.plan(inventory, scope="full")
    provider = DryRunProvider()
    context = ops.generate(REPO_ROOT, plan, provider=provider)
    assert len(context.fact_packs) > 0
    assert all("name" in pack for pack in context.fact_packs)


# ------------------------------------------------------------------
# write
# ------------------------------------------------------------------


def test_write_generates_files(ops: AictxContextOps, tmp_path: Path) -> None:
    # Use a minimal synthetic repo to avoid polluting the real one
    repo = tmp_path / "synthetic"
    repo.mkdir()
    (repo / "README.md").write_text("# Test\n")
    (repo / "pyproject.toml").write_text('[project]\nname = "test"\n')
    src = repo / "src"
    src.mkdir()
    (src / "main.py").write_text("def main(): pass\n")
    import subprocess
    subprocess.run(["git", "init", str(repo)], check=False, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@test.com"], check=False, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=False, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=False, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "init"], check=False, capture_output=True)

    inventory = ops.scan(repo)
    plan = ops.plan(inventory, scope="full")
    provider = DryRunProvider()
    context = ops.generate(repo, plan, provider=provider)
    report = ops.write(repo, context, write_mode="patch")

    assert len(report.generated_files) > 0
    assert any("context.lock.json" in f for f in report.generated_files)
    assert report.patch_text is not None


# ------------------------------------------------------------------
# verify
# ------------------------------------------------------------------


def test_verify_without_lockfile(ops: AictxContextOps, tmp_path: Path) -> None:
    repo = tmp_path / "no_lock"
    repo.mkdir()
    (repo / "README.md").write_text("# Test\n")

    result = ops.verify(repo, strict=False)
    assert result.result == "FAIL_LOCK_MISMATCH"
    assert result.is_pass is False


def test_verify_with_lockfile(ops: AictxContextOps, tmp_path: Path) -> None:
    repo = tmp_path / "with_lock"
    repo.mkdir()
    (repo / "README.md").write_text("# Test\n")
    import subprocess
    subprocess.run(["git", "init", str(repo)], check=False, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@test.com"], check=False, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=False, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=False, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "init"], check=False, capture_output=True)

    # Generate context first to create lockfile
    inventory = ops.scan(repo)
    plan = ops.plan(inventory, scope="full")
    provider = DryRunProvider()
    context = ops.generate(repo, plan, provider=provider)
    ops.write(repo, context, write_mode="apply")

    result = ops.verify(repo, strict=False)
    assert result.result == "PASS"
    assert result.is_pass is True


# ------------------------------------------------------------------
# status
# ------------------------------------------------------------------


def test_status_without_lockfile(ops: AictxContextOps, tmp_path: Path) -> None:
    repo = tmp_path / "status_no_lock"
    repo.mkdir()
    (repo / "README.md").write_text("# Test\n")

    status = ops.status(repo, strict=False)
    assert status.is_stale is True
    assert status.next_command is not None


# ------------------------------------------------------------------
# public_docs_impact
# ------------------------------------------------------------------


def test_public_docs_impact(ops: AictxContextOps, tmp_path: Path) -> None:
    repo = tmp_path / "docs_repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Test\n")
    docs = repo / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("# Guide\n")
    import subprocess
    subprocess.run(["git", "init", str(repo)], check=False, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@test.com"], check=False, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=False, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=False, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "init"], check=False, capture_output=True)

    report = ops.public_docs_impact(repo, scope="full")
    assert len(report.entries) > 0
