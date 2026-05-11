from __future__ import annotations

import pytest

from presets import PRESET_REGISTRY


class TestPresetRegistry:
    def test_all_presets_registered(self) -> None:
        presets = PRESET_REGISTRY.list()
        ids = {p.preset_id for p in presets}
        expected = {
            "codebase-assistant",
            "local-document-chat",
            "research-report",
            "file-organizer",
            "docs-maintainer",
            "github-maintainer",
            "command-assistant",
        }
        assert expected <= ids, f"Missing presets: {expected - ids}"

    def test_preset_has_name_and_description(self) -> None:
        for preset in PRESET_REGISTRY.list():
            assert preset.name, f"Preset {preset.preset_id} missing name"
            assert preset.description, f"Preset {preset.preset_id} missing description"

    def test_preset_has_workflow_id(self) -> None:
        for preset in PRESET_REGISTRY.list():
            assert preset.workflow_id, f"Preset {preset.preset_id} missing workflow_id"

    def test_codebase_assistant_preset(self) -> None:
        preset = PRESET_REGISTRY.get("codebase-assistant")
        assert preset.workflow_id == "coding"
        assert len(preset.guided_questions) > 0

    def test_local_document_chat_preset(self) -> None:
        preset = PRESET_REGISTRY.get("local-document-chat")
        assert preset.workflow_id == "documents"

    def test_research_report_preset(self) -> None:
        preset = PRESET_REGISTRY.get("research-report")
        assert preset.workflow_id == "research"

    def test_file_organizer_preset(self) -> None:
        preset = PRESET_REGISTRY.get("file-organizer")
        assert preset.workflow_id == "file_organization"

    def test_docs_maintainer_preset(self) -> None:
        preset = PRESET_REGISTRY.get("docs-maintainer")
        assert preset.workflow_id == "docs_maintenance"

    def test_github_maintainer_preset(self) -> None:
        preset = PRESET_REGISTRY.get("github-maintainer")
        assert preset.workflow_id == "github_maintenance"

    def test_command_assistant_preset(self) -> None:
        preset = PRESET_REGISTRY.get("command-assistant")
        assert preset.workflow_id == "command_assistant"
