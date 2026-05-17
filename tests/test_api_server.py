from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from core.events import EventType
from core.ledger import RunLedger
from interfaces.api_server import create_api_app
from interfaces.api_server.auth import _API_KEYS, _initialized


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    # Reset auth state for tests
    global _initialized
    _initialized = False
    _API_KEYS.clear()
    _API_KEYS.add("test-key")
    app = create_api_app(repo_root=tmp_path)
    return TestClient(app)


class TestHealth:
    def test_health_no_auth(self, client: TestClient) -> None:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["request_id"]
        assert "version" in data
        assert "components" in data
        assert response.headers["X-Request-ID"] == data["request_id"]

    def test_health_uses_supplied_request_id(self, client: TestClient) -> None:
        response = client.get("/api/health", headers={"X-Request-ID": "req-123"})
        assert response.status_code == 200
        assert response.json()["request_id"] == "req-123"
        assert response.headers["X-Request-ID"] == "req-123"


class TestPublicV1Routes:
    def test_status_route_returns_readiness_and_recent_runs(self, client: TestClient) -> None:
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["request_id"]
        assert "readiness" in data
        assert "recent_runs" in data

    def test_tasks_route_matches_catalog_shape(self, client: TestClient) -> None:
        response = client.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(item["preset_id"] == "research-report" for item in data)

    def test_task_run_route_returns_request_id(self, client: TestClient) -> None:
        from unittest.mock import patch
        from core.run_executor import RunExecutor

        RunExecutor.reset_instance()
        with patch("core.run_executor.RunExecutor.submit", return_value="task-run-1"):
            response = client.post(
                "/api/tasks/research-report/run",
                json={"inputs": {"topic": "AI"}},
                headers={"X-API-Key": "test-key"},
            )
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "request_id": data["request_id"],
            "run_id": "task-run-1",
            "status": "pending",
        }
        RunExecutor.reset_instance()

    def test_runs_route_lists_canonical_summaries(self, tmp_path: Path, client: TestClient) -> None:
        run_dir = tmp_path / ".ai-team" / "runs" / "test-run-list"
        run_dir.mkdir(parents=True)
        (run_dir / "final_report.md").write_text("# Report", encoding="utf-8")
        (run_dir / "run.json").write_text(
            json.dumps({"run_id": "test-run-list", "workflow_id": "coding", "preset_id": "codebase-assistant"}),
            encoding="utf-8",
        )
        (run_dir / "final_report.json").write_text(
            json.dumps({"run_id": "test-run-list", "task_summary": "Listed run", "status": "done"}),
            encoding="utf-8",
        )

        response = client.get("/api/runs")
        assert response.status_code == 200
        data = response.json()
        assert data["request_id"]
        assert any(run["run_id"] == "test-run-list" for run in data["runs"])

    def test_provider_setup_route_writes_profile_and_returns_readiness(self, tmp_path: Path, client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
        from config.config import ProfilesDocument, load_profiles_document
        from interfaces.readiness import ReadinessState, ReadinessStatus

        class DummySecretStore:
            def __init__(self) -> None:
                self.values: dict[str, str] = {}

            def set(self, ref: str, value: str) -> None:
                self.values[ref] = value

            def get(self, ref: str) -> str:
                return self.values[ref]

            def delete(self, ref: str) -> None:
                self.values.pop(ref, None)

        monkeypatch.setenv("AGENTHEIM_CONFIG_DIR", str(tmp_path / "config"))
        monkeypatch.setenv("AGENTHEIM_DATA_DIR", str(tmp_path / "data"))
        monkeypatch.setattr("interfaces.api_server.app.get_secret_store", lambda: DummySecretStore())
        monkeypatch.setattr(
            "interfaces.api_server.app.build_readiness_state",
            lambda profile=None, check_optional_integrations=True: ReadinessState(status=ReadinessStatus.ready),
        )

        response = client.post(
            "/api/providers/setup",
            json={
                "provider": "starter",
                "template": "openai_v1",
                "model": "gpt-4o-mini",
                "api_key": "secret",
                "profile": "default",
            },
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["request_id"]
        assert data["status"] == "written"
        assert data["profile"] == "default"

        document = load_profiles_document()
        assert isinstance(document, ProfilesDocument)
        assert "starter" in document.profiles["default"].providers


class TestAuth:
    def test_missing_api_key(self, client: TestClient) -> None:
        response = client.post("/api/memory/jsonl/test", json={"value": {"x": 1}})
        assert response.status_code == 401
        data = response.json()
        assert data["machine_code"]
        assert data["request_id"]

    def test_invalid_api_key(self, client: TestClient) -> None:
        response = client.post(
            "/api/memory/jsonl/test",
            json={"value": {"x": 1}},
            headers={"X-API-Key": "bad-key"},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["machine_code"]
        assert data["request_id"]

    def test_valid_api_key(self, client: TestClient) -> None:
        response = client.post(
            "/api/memory/jsonl/test",
            json={"value": {"x": 1}},
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200


class TestTools:
    def test_list_tools(self, client: TestClient) -> None:
        response = client.get("/api/tools")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        tool_ids = {t["tool_id"] for t in data}
        assert "filesystem" in tool_ids
        assert "local_db" in tool_ids
        assert "http.request" in tool_ids
        assert "memory" in tool_ids

    def test_tool_schema_has_parameters(self, client: TestClient) -> None:
        response = client.get("/api/tools")
        data = response.json()
        fs_tool = next(t for t in data if t["tool_id"] == "filesystem")
        assert "parameters" in fs_tool
        assert "operation" in fs_tool["parameters"]

    def test_invoke_tool_not_found(self, client: TestClient) -> None:
        response = client.post(
            "/api/tools/nonexistent/invoke",
            json={"params": {}},
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 404
        data = response.json()
        assert data["machine_code"]
        assert data["request_id"]

    def test_invoke_high_risk_blocked(self, client: TestClient) -> None:
        response = client.post(
            "/api/tools/shell.execute/invoke",
            json={"params": {"command": ["echo", "hi"]}},
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["machine_code"]
        assert data["request_id"]
        assert "blocked" in data["human_message"].lower() or "auth" in data["human_message"].lower()

    def test_invoke_filesystem_read(self, tmp_path: Path, client: TestClient) -> None:
        test_file = tmp_path / "hello.txt"
        test_file.write_text("world", encoding="utf-8")
        response = client.post(
            "/api/tools/filesystem/invoke",
            json={"params": {"operation": "read", "path": "hello.txt"}},
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] == "world"
        assert data["requires_approval"] is False

    def test_invoke_browser_blocked(self, client: TestClient) -> None:
        response = client.post(
            "/api/tools/browser/invoke",
            json={"params": {"operation": "navigate", "url": "https://example.com"}},
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 403

    def test_invoke_filesystem_write_returns_approval_request(self, tmp_path: Path, client: TestClient) -> None:
        response = client.post(
            "/api/tools/filesystem/invoke",
            json={"params": {"operation": "write", "path": "created.txt", "content": "new"}},
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert data["requires_approval"] is True
        assert data["policy"]["decision"] == "ask"
        assert data["approval_request"]["request_id"]
        assert not (tmp_path / "created.txt").exists()

    def test_grant_filesystem_write_executes_and_records_ledger(self, tmp_path: Path, client: TestClient) -> None:
        response = client.post(
            "/api/tools/filesystem/invoke",
            json={"params": {"operation": "write", "path": "created.txt", "content": "new"}},
            headers={"X-API-Key": "test-key"},
        )
        request_id = response.json()["approval_request"]["request_id"]

        grant = client.post(
            f"/api/tools/approvals/{request_id}/grant",
            headers={"X-API-Key": "test-key"},
        )
        assert grant.status_code == 200
        data = grant.json()
        assert data["status"] == "granted"
        assert data["success"] is True
        assert (tmp_path / "created.txt").read_text(encoding="utf-8") == "new"

        run_dirs = sorted((tmp_path / ".ai-team" / "runs").iterdir())
        ledger = RunLedger(repo_root=tmp_path, run_dir=run_dirs[-1])
        event_types = [event.event_type for event in ledger.read_ledger()]
        assert EventType.POLICY_EVALUATED in event_types
        assert EventType.APPROVAL_REQUESTED in event_types
        assert EventType.APPROVAL_GRANTED in event_types
        assert EventType.TOOL_RESULT_RECEIVED in event_types

    def test_deny_filesystem_write_records_denial(self, tmp_path: Path, client: TestClient) -> None:
        response = client.post(
            "/api/tools/filesystem/invoke",
            json={"params": {"operation": "write", "path": "created.txt", "content": "new"}},
            headers={"X-API-Key": "test-key"},
        )
        request_id = response.json()["approval_request"]["request_id"]

        deny = client.post(
            f"/api/tools/approvals/{request_id}/deny",
            headers={"X-API-Key": "test-key"},
        )
        assert deny.status_code == 200
        data = deny.json()
        assert data["status"] == "denied"
        assert data["error"] == "approval_denied"
        assert not (tmp_path / "created.txt").exists()

        run_dirs = sorted((tmp_path / ".ai-team" / "runs").iterdir())
        ledger = RunLedger(repo_root=tmp_path, run_dir=run_dirs[-1])
        event_types = [event.event_type for event in ledger.read_ledger()]
        assert EventType.APPROVAL_REQUESTED in event_types
        assert EventType.APPROVAL_DENIED in event_types


class TestWorkflows:
    def test_list_workflows(self, client: TestClient) -> None:
        response = client.get("/api/workflows")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        workflow_ids = {w["workflow_id"] for w in data}
        assert "research" in workflow_ids

    def test_get_workflow_detail(self, client: TestClient) -> None:
        response = client.get("/api/workflows/research")
        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == "research"
        assert "name" in data

    def test_get_workflow_not_found(self, client: TestClient) -> None:
        response = client.get("/api/workflows/nonexistent")
        assert response.status_code == 404


class TestPresets:
    def test_list_presets(self, client: TestClient) -> None:
        response = client.get("/api/presets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        preset_ids = {p["preset_id"] for p in data}
        assert "research-report" in preset_ids


class TestMemory:
    def test_read_missing_key(self, client: TestClient) -> None:
        response = client.get("/api/memory/jsonl/nonexistent_key_12345")
        assert response.status_code == 200
        data = response.json()
        assert data["found"] is False
        assert data["value"] is None

    def test_write_and_read(self, client: TestClient) -> None:
        key = "test_key_api"
        response = client.post(
            f"/api/memory/jsonl/{key}",
            json={"value": {"message": "hello"}},
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "written"

        response = client.get(f"/api/memory/jsonl/{key}")
        assert response.status_code == 200
        data = response.json()
        assert data["found"] is True
        assert data["value"] == {"message": "hello"}


class TestModels:
    def test_list_models(self, client: TestClient) -> None:
        response = client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestProviders:
    def test_list_providers(self, client: TestClient) -> None:
        response = client.get("/api/providers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        provider_ids = {p["provider_id"] for p in data}
        assert "openai_v1" in provider_ids

    def test_provider_templates_excludes_experimental(self, client: TestClient) -> None:
        response = client.get("/api/providers/templates")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for t in data:
            assert t["support_state"] != "experimental", (
                f"experimental template '{t['kind']}' leaked to API"
            )

    def test_provider_setup_requires_api_key_for_api_key_auth(self, client: TestClient) -> None:
        response = client.post(
            "/api/providers/setup",
            json={"provider": "starter", "template": "openai_v1", "model": "gpt-4o-mini"},
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["machine_code"]
        assert data["request_id"]


class TestRuns:
    def test_runs_list_empty(self, client: TestClient) -> None:
        response = client.get("/api/runs")
        assert response.status_code == 200
        data = response.json()
        assert data["runs"] == []

    def test_run_not_found(self, client: TestClient) -> None:
        response = client.get("/api/runs/nonexistent_run_12345")
        assert response.status_code == 404
        data = response.json()
        assert data["machine_code"]
        assert data["request_id"]

    def test_run_found(self, tmp_path: Path, client: TestClient) -> None:
        run_dir = tmp_path / ".ai-team" / "runs" / "test-run-1"
        run_dir.mkdir(parents=True)
        (run_dir / "final_report.md").write_text("# Report", encoding="utf-8")
        (run_dir / "run.json").write_text(
            json.dumps({"run_id": "test-run-1", "workflow_id": "coding", "preset_id": "codebase-assistant"}),
            encoding="utf-8",
        )
        (run_dir / "final_report.json").write_text(
            json.dumps({"run_id": "test-run-1", "task_summary": "Ship fix", "status": "done"}),
            encoding="utf-8",
        )
        response = client.get("/api/runs/test-run-1")
        assert response.status_code == 200
        data = response.json()
        assert data["run_id"] == "test-run-1"
        assert data["status"] == "completed"
        assert "final_report.md" in data["artifacts"]
        assert data["workflow_id"] == "coding"
        assert data["preset_id"] == "codebase-assistant"
        assert data["summary"] == "Ship fix"


class TestWorkflowExecution:
    def test_execute_workflow_not_found(self, client: TestClient) -> None:
        response = client.post(
            "/api/workflows/nonexistent/execute",
            json={"params": {}},
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 404

    def test_execute_workflow_returns_run_id(self, client: TestClient) -> None:
        from unittest.mock import patch
        from core.run_executor import RunExecutor
        RunExecutor.reset_instance()
        with patch("core.run_executor.RunExecutor.submit", return_value="test-run-123"):
            response = client.post(
                "/api/workflows/research/execute",
                json={"params": {"task": "test"}},
                headers={"X-API-Key": "test-key"},
            )
        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        assert data["status"] == "pending"
        RunExecutor.reset_instance()


class TestPresetExecution:
    def test_run_preset_not_found(self, client: TestClient) -> None:
        response = client.post(
            "/api/presets/nonexistent/run",
            json={"inputs": {}},
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 404

    def test_run_preset_returns_run_id(self, client: TestClient) -> None:
        from unittest.mock import patch
        from core.run_executor import RunExecutor
        RunExecutor.reset_instance()
        with patch("core.run_executor.RunExecutor.submit", return_value="test-run-456"):
            response = client.post(
                "/api/presets/research-report/run",
                json={"inputs": {"topic": "AI"}},
                headers={"X-API-Key": "test-key"},
            )
        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        assert data["status"] == "pending"
        RunExecutor.reset_instance()

    def test_run_preset_rejects_missing_required_inputs(self, client: TestClient) -> None:
        from unittest.mock import patch

        with patch("core.run_executor.RunExecutor.submit") as mock_submit:
            response = client.post(
                "/api/presets/research-report/run",
                json={"inputs": {}},
                headers={"X-API-Key": "test-key"},
            )
        assert response.status_code == 400
        data = response.json()
        assert data["machine_code"]
        assert data["request_id"]
        assert data["error"] == "missing_required_inputs"
        assert data["details"]["preset_id"] == "research-report"
        assert data["details"]["missing_inputs"] == ["topic"]
        mock_submit.assert_not_called()

    def test_task_run_rejects_missing_required_inputs(self, client: TestClient) -> None:
        response = client.post(
            "/api/tasks/research-report/run",
            json={"inputs": {}},
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["machine_code"]
        assert data["request_id"]
        assert data["error"] == "missing_required_inputs"
        assert data["details"]["missing_inputs"] == ["topic"]


class TestRunStreaming:
    def test_stream_run_not_found(self, client: TestClient) -> None:
        response = client.get("/api/runs/nonexistent_run_12345/stream")
        assert response.status_code == 404


class TestRunWebSocket:
    def test_websocket_run_not_found(self, client: TestClient) -> None:
        from starlette.websockets import WebSocketDisconnect

        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/api/runs/nonexistent_run_12345/ws") as ws:
                ws.receive_json()

    def test_websocket_receives_status_updates(self, client: TestClient) -> None:
        import threading
        import time
        from core.run_executor import RunExecutor

        # Use the existing singleton instance that the app factory captured.
        executor = RunExecutor()

        started = threading.Event()

        def _slow_task():
            started.set()
            time.sleep(0.5)
            return "done"

        run_id = executor.submit(_slow_task)
        started.wait(timeout=2.0)

        with client.websocket_connect(f"/api/runs/{run_id}/ws") as ws:
            msg1 = ws.receive_json()
            assert msg1["run_id"] == run_id
            assert msg1["status"] in ("pending", "running")

            msg2 = ws.receive_json()
            assert msg2["run_id"] == run_id
            assert msg2["status"] == "completed"
            assert msg2["artifacts"] == []

    def test_websocket_final_message_uses_canonical_run_summary(self, tmp_path: Path, client: TestClient) -> None:
        import threading
        import time
        from core.run_executor import RunExecutor

        executor = RunExecutor()
        started = threading.Event()

        class _Result:
            run_id = "persisted-run"

        def _task():
            started.set()
            run_dir = tmp_path / ".ai-team" / "runs" / "persisted-run"
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "run.json").write_text(
                json.dumps({"run_id": "persisted-run", "workflow_id": "coding"}),
                encoding="utf-8",
            )
            (run_dir / "final_report.json").write_text(
                json.dumps({"run_id": "persisted-run", "task_summary": "Canonical final payload", "status": "done"}),
                encoding="utf-8",
            )
            (run_dir / "final_report.md").write_text("# Report", encoding="utf-8")
            time.sleep(0.2)
            return _Result()

        run_id = executor.submit(_task)
        started.wait(timeout=2.0)

        with client.websocket_connect(f"/api/runs/{run_id}/ws") as ws:
            _ = ws.receive_json()
            final = ws.receive_json()
            assert final["run_id"] == "persisted-run"
            assert final["tracking_run_id"] == run_id
            assert final["status"] == "completed"
            assert final["summary"] == "Canonical final payload"


class TestMetrics:
    def test_metrics_endpoint(self, client: TestClient) -> None:
        response = client.get("/api/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        body = response.text
        assert "agentheim" in body.lower() or "#" in body


class TestOpenAPI:
    def test_openapi_schema(self, client: TestClient) -> None:
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "Agentheim API"
        paths = list(schema["paths"].keys())
        assert "/api/health" in paths
        assert "/api/status" in paths
        assert "/api/tasks" in paths
        assert "/api/tasks/{task_id}/run" in paths
        assert "/api/runs" in paths
        assert "/api/tools" in paths
        assert "/api/workflows" in paths
        assert "/api/presets" in paths
        assert "/api/providers" in paths
        assert "/api/providers/setup" in paths
        assert "/api/providers/templates" in paths
        assert "/api/workflows/{workflow_id}/execute" in paths
        assert "/api/presets/{preset_id}/run" in paths
        assert "/api/runs/{run_id}/stream" in paths
        assert "/api/metrics" in paths

    def test_openapi_marks_advanced_routes(self, client: TestClient) -> None:
        schema = client.get("/openapi.json").json()
        assert schema["paths"]["/api/workflows"]["get"]["description"].startswith("[Advanced route]")
        assert schema["paths"]["/api/presets"]["get"]["description"].startswith("[Advanced route]")

    def test_compatibility_routes_still_exist(self, client: TestClient) -> None:
        schema = client.get("/openapi.json").json()
        assert "/api/workflows" in schema["paths"]
        assert "/api/presets" in schema["paths"]
        assert "/api/providers/assign" in schema["paths"]

    def test_docs_endpoint(self, client: TestClient) -> None:
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
