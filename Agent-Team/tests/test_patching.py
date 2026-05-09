import pytest

from ai_team.errors import PatchApplicationError
from ai_team.patching import PatchApplier


def test_patch_path_validation_blocks_repo_escape(tmp_path) -> None:
    applier = PatchApplier(tmp_path)
    with pytest.raises(PatchApplicationError):
        applier.validate_relative_path("..\\outside.txt")


def test_patch_apply_rejects_out_of_scope_file(tmp_path) -> None:
    applier = PatchApplier(tmp_path)
    result = applier.apply_changes(
        [{"path": "README.md", "change_type": "modify", "summary": "update", "patch": "hello"}],
        allowed_files=["docs/README.md"],
    )
    assert result.applied is False
    assert any("outside work order scope" in item for item in result.errors)