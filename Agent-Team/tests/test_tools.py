import pytest

from ai_team.tools.filesystem import RepoSandbox
from ai_team.tools.shell import ShellTool


def test_repo_sandbox_blocks_escape(tmp_path) -> None:
    sandbox = RepoSandbox(tmp_path)
    with pytest.raises(ValueError):
        sandbox.resolve("..")


def test_shell_tool_blocks_install_and_destructive(tmp_path) -> None:
    shell = ShellTool(tmp_path)
    with pytest.raises(ValueError):
        shell.run(["npm", "install"])
    with pytest.raises(ValueError):
        shell.run(["powershell", "Remove-Item", "-Recurse", "."])