from __future__ import annotations

from pathlib import Path

from scripts.install_git_hooks import HOOKS_DIR, ROOT


def test_hooks_dir_points_to_repo_githooks() -> None:
    assert HOOKS_DIR == ROOT / ".githooks"
    assert HOOKS_DIR.name == ".githooks"
