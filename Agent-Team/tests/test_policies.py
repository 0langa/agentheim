from ai_team.policies import CommandPolicy, can_auto_run, classify_command


def test_command_policy_classification() -> None:
    assert classify_command(["python", "-m", "pytest"]) == CommandPolicy.SAFE
    assert classify_command(["npm", "install"]) == CommandPolicy.INSTALL
    assert classify_command(["az", "deployment", "group", "create"]) == CommandPolicy.DEPLOY
    assert classify_command(["powershell", "Remove-Item", "foo"]) == CommandPolicy.DESTRUCTIVE
    assert can_auto_run(["python", "-m", "pytest"]) is True
    assert can_auto_run(["npm", "install"]) is False