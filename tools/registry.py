from __future__ import annotations

from pathlib import Path

from tools.browser import BrowserTool
from tools.filesystem import FilesystemTool
from tools.git import GitTool
from tools.local_db import LocalDBTool
from tools.shell import ShellTool
from tools.tests import TestTool


class ToolRegistry:
    def __init__(self, repo_root: str | Path) -> None:
        self.filesystem = FilesystemTool(repo_root)
        self.git = GitTool(repo_root)
        self.shell = ShellTool(repo_root)
        self.browser = BrowserTool(repo_root)
        self.local_db = LocalDBTool(repo_root)
        self.tests = TestTool(self.shell)