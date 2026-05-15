from __future__ import annotations

from pathlib import Path

import pytest

from core.patching import PatchApplier


class TestPatchApplierMaxDiff:
    def test_max_diff_lines_rejects_large_patch(self, tmp_path: Path) -> None:
        applier = PatchApplier(tmp_path, max_diff_lines=5)
        target = tmp_path / "file.txt"
        target.write_text("line1\nline2\nline3\n", encoding="utf-8")
        long_text = "\n".join(f"line{i}" for i in range(100))
        file_changes = [{"path": "file.txt", "change_type": "edit", "patch": long_text}]
        result = applier.apply_changes(file_changes)
        assert not result.applied
        assert any("exceeds max diff lines" in e for e in result.errors)

    def test_max_diff_lines_allows_small_patch(self, tmp_path: Path) -> None:
        applier = PatchApplier(tmp_path, max_diff_lines=50)
        target = tmp_path / "file.txt"
        target.write_text("line1\nline2\nline3\n", encoding="utf-8")
        file_changes = [{"path": "file.txt", "change_type": "edit", "patch": "line1\nline2\nline3\nline4\n"}]
        result = applier.apply_changes(file_changes)
        assert result.applied
        assert not result.errors


class TestPatchApplierRollback:
    def test_rollback_restores_original_content(self, tmp_path: Path) -> None:
        applier = PatchApplier(tmp_path)
        target = tmp_path / "file.txt"
        original = "original content"
        target.write_text(original, encoding="utf-8")
        file_changes = [{"path": "file.txt", "change_type": "edit", "patch": "new content"}]
        result = applier.apply_changes(file_changes)
        assert result.applied
        assert target.read_text(encoding="utf-8") == "new content"
        applier.rollback(result.file_changes)
        assert target.read_text(encoding="utf-8") == original

    def test_rollback_deletes_created_file(self, tmp_path: Path) -> None:
        applier = PatchApplier(tmp_path)
        file_changes = [{"path": "new_file.txt", "change_type": "create", "patch": "created content"}]
        result = applier.apply_changes(file_changes)
        assert result.applied
        assert (tmp_path / "new_file.txt").exists()
        applier.rollback(result.file_changes)
        assert not (tmp_path / "new_file.txt").exists()
