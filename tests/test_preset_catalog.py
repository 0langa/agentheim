from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from interfaces.api_server import create_api_app
from interfaces.api_server.auth import _API_KEYS, _initialized
from interfaces.cli.cli import app as cli_app
from interfaces.web_ui import create_app as create_web_app
from presets import PRESET_REGISTRY
from presets.catalog import CATALOG, PresetCatalog, PresetCatalogItem, QuestionSchema


runner = CliRunner()


@pytest.fixture
def api_client(tmp_path) -> TestClient:
    global _initialized
    _initialized = False
    _API_KEYS.clear()
    _API_KEYS.add("test-key")
    app = create_api_app(repo_root=tmp_path)
    return TestClient(app)


@pytest.fixture
def web_client(tmp_path) -> TestClient:
    app = create_web_app(repo_root=tmp_path)
    return TestClient(app)


class TestCatalogGroupingAndOrdering:
    def test_recommended_presets_come_first(self) -> None:
        items = CATALOG.list()
        tiers = [item.product_tier for item in items]
        # All recommended should appear before any advanced
        first_advanced = next((i for i, t in enumerate(tiers) if t == "advanced"), len(tiers))
        last_recommended = next((i for i in range(len(tiers) - 1, -1, -1) if tiers[i] == "recommended"), -1)
        assert last_recommended < first_advanced, f"Recommended presets should come before advanced: {tiers}"

    def test_all_registered_presets_in_catalog(self) -> None:
        registry_ids = {p.preset_id for p in PRESET_REGISTRY.list()}
        catalog_ids = {item.preset_id for item in CATALOG.list()}
        assert registry_ids == catalog_ids

    def test_recommended_tier_has_exact_four(self) -> None:
        recommended = CATALOG.recommended()
        ids = {item.preset_id for item in recommended}
        assert ids == {
            "coder",
            "codebase-assistant",
            "local-document-chat",
            "command-assistant",
            "context-maintainer",
        }

    def test_advanced_tier_has_exact_four(self) -> None:
        advanced = CATALOG.advanced()
        ids = {item.preset_id for item in advanced}
        assert ids == {
            "research-report",
            "docs-maintainer",
            "file-organizer",
            "github-maintainer",
        }

    def test_no_hidden_tier_presets(self) -> None:
        hidden = CATALOG.list_by_tier("hidden")
        assert hidden == []

    def test_catalog_ordering_is_stable(self) -> None:
        first = CATALOG.list()
        second = CATALOG.list()
        assert [item.preset_id for item in first] == [item.preset_id for item in second]


class TestCatalogMetadata:
    def test_all_items_have_metadata(self) -> None:
        for item in CATALOG.list():
            assert item.preset_id, f"Missing preset_id"
            assert item.workflow_id, f"Missing workflow_id"
            assert item.name, f"Missing name"
            assert item.description, f"Missing description"
            assert item.product_tier in ("recommended", "advanced", "hidden")
            assert item.support_state
            assert item.estimated_time, f"{item.preset_id} missing estimated_time"
            assert item.output_kind, f"{item.preset_id} missing output_kind"
            assert item.example_inputs, f"{item.preset_id} missing example_inputs"

    def test_recommended_presets_have_recommended_for(self) -> None:
        for item in CATALOG.recommended():
            assert item.recommended_for, f"{item.preset_id} missing recommended_for"

    def test_codebase_assistant_metadata(self) -> None:
        item = CATALOG.get("codebase-assistant")
        assert item.product_tier == "recommended"
        assert item.estimated_time == "2-10 minutes"
        assert item.output_kind == "patch + report"
        assert "task" in item.example_inputs

    def test_research_report_requires_web_search(self) -> None:
        item = CATALOG.get("research-report")
        assert item.product_tier == "advanced"
        assert "web_search" in item.requires_integrations

    def test_github_maintainer_requires_github(self) -> None:
        item = CATALOG.get("github-maintainer")
        assert item.product_tier == "advanced"
        assert "github" in item.requires_integrations


class TestQuestionSchema:
    def test_questions_have_key_type_text(self) -> None:
        item = CATALOG.get("research-report")
        assert item.questions
        topic = next(q for q in item.questions if q.key == "topic")
        assert topic.type == "text"
        assert topic.text == "Research topic?"

    def test_questions_have_options_when_choices(self) -> None:
        item = CATALOG.get("codebase-assistant")
        mode = next(q for q in item.questions if q.key == "mode")
        assert mode.options == ["apply", "auto", "ci"]

    def test_question_schema_serializes_cleanly(self) -> None:
        q = QuestionSchema(key="x", type="text", text="Test", default=".")
        data = q.model_dump()
        assert data["key"] == "x"
        assert data["type"] == "text"
        assert "__dict__" not in data


class TestCatalogDefaults:
    def test_codebase_assistant_defaults(self) -> None:
        item = CATALOG.get("codebase-assistant")
        assert item.default_config.get("mode") == "apply"
        assert item.default_config.get("allow_dirty") is False

    def test_research_report_defaults(self) -> None:
        item = CATALOG.get("research-report")
        assert item.default_config == {}


class TestCliApiWebParity:
    def test_cli_presets_list_includes_all_catalog_items(self) -> None:
        result = runner.invoke(cli_app, ["presets"])
        assert result.exit_code == 0
        for item in CATALOG.list():
            # Rich may truncate long IDs in table cells
            assert item.preset_id[:10] in result.output or item.name in result.output

    def test_cli_shows_recommended_tier(self) -> None:
        result = runner.invoke(cli_app, ["presets"])
        assert result.exit_code == 0
        assert "recommended" in result.output

    def test_api_returns_same_preset_ids_as_catalog(self, api_client: TestClient) -> None:
        response = api_client.get("/api/presets", headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
        data = response.json()
        api_ids = {p["preset_id"] for p in data}
        catalog_ids = {item.preset_id for item in CATALOG.list()}
        assert api_ids == catalog_ids

    def test_api_returns_product_tier(self, api_client: TestClient) -> None:
        response = api_client.get("/api/presets", headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
        data = response.json()
        for p in data:
            assert "product_tier" in p
            assert p["product_tier"] in ("recommended", "advanced", "hidden")

    def test_web_ui_returns_same_preset_ids_as_catalog(self, web_client: TestClient) -> None:
        response = web_client.get("/api/presets")
        assert response.status_code == 200
        data = response.json()
        web_ids = {p["preset_id"] for p in data}
        catalog_ids = {item.preset_id for item in CATALOG.list()}
        assert web_ids == catalog_ids

    def test_web_ui_returns_product_tier(self, web_client: TestClient) -> None:
        response = web_client.get("/api/presets")
        assert response.status_code == 200
        data = response.json()
        for p in data:
            assert "product_tier" in p
            assert p["product_tier"] in ("recommended", "advanced", "hidden")

    def test_api_and_web_have_same_tier_for_each_preset(self, api_client: TestClient, web_client: TestClient) -> None:
        api_data = api_client.get("/api/presets", headers={"X-API-Key": "test-key"}).json()
        web_data = web_client.get("/api/presets").json()
        api_tiers = {p["preset_id"]: p["product_tier"] for p in api_data}
        web_tiers = {p["preset_id"]: p["product_tier"] for p in web_data}
        assert api_tiers == web_tiers

    def test_api_returns_question_schema_not_raw_dict(self, api_client: TestClient) -> None:
        response = api_client.get("/api/presets", headers={"X-API-Key": "test-key"})
        data = response.json()
        research = next(p for p in data if p["preset_id"] == "research-report")
        assert "questions" in research
        question = research["questions"][0]
        assert "key" in question
        assert "type" in question
        assert "text" in question
        assert "__dict__" not in question

    def test_web_returns_question_schema_not_raw_dict(self, web_client: TestClient) -> None:
        response = web_client.get("/api/presets")
        data = response.json()
        research = next(p for p in data if p["preset_id"] == "research-report")
        assert "questions" in research
        question = research["questions"][0]
        assert "key" in question
        assert "type" in question
        assert "text" in question
        assert "__dict__" not in question
