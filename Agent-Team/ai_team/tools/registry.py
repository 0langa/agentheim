from __future__ import annotations

from pathlib import Path

from ai_team.tools.filesystem import FilesystemTool
from ai_team.tools.git import GitTool
from ai_team.tools.shell import ShellTool
from ai_team.tools.tests import TestTool


class ToolRegistry:
    def __init__(self, repo_root: str | Path) -> None:
        self.filesystem = FilesystemTool(repo_root)
        self.git = GitTool(repo_root)
        self.shell = ShellTool(repo_root)
        self.tests = TestTool(self.shell)