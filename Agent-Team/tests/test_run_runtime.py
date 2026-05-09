from pathlib import Path

import pytest

from ai_team.errors import ExecutionError
from ai_team.runtime import run_task


def test_run_task_blocks_dirty_repo_without_flag(tmp_path, monkeypatch) -> None:
    (tmp_path / "README.md").write_text("hello\n", encoding="utf-8")

    class DummyGit:
        def status(self) -> str:
            return " M README.md"

    class DummyRegistry:
        def __init__(self, _repo_root):
            self.git = DummyGit()

    monkeypatch.setattr("ai_team.runtime.load_team_config", lambda: object())
    monkeypatch.setattr("ai_team.runtime.ToolRegistry", DummyRegistry)

    with pytest.raises(ExecutionError):
        run_task("Add usage", tmp_path)
