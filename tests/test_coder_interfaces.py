from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from interfaces.api_server import create_api_app
from interfaces.api_server.auth import _API_KEYS, _initialized
from interfaces.web_ui import create_app as create_web_app
from workflows.coder.models import CoderAction, CoderTurnPlan


@pytest.fixture
def web_client(tmp_path: Path) -> TestClient:
    app = create_web_app(repo_root=tmp_path)
    return TestClient(app)


@pytest.fixture
def api_client(tmp_path: Path) -> TestClient:
    global _initialized
    _initialized = False
    _API_KEYS.clear()
    _API_KEYS.add("test-key")
    app = create_api_app(repo_root=tmp_path)
    return TestClient(app)


def _workspace_plan(*args, **kwargs) -> CoderTurnPlan:
    return CoderTurnPlan(
        assistant_message="I created hello.txt.",
        summary="Create hello file",
        actions=[
            CoderAction(
                kind="write_file",
                path="hello.txt",
                content="hello",
                summary="Create hello.txt",
            )
        ],
    )


def _ask_plan(*args, **kwargs) -> CoderTurnPlan:
    return CoderTurnPlan(
        assistant_message="I can create hello.txt after approval.",
        summary="Create hello file",
        actions=[
            CoderAction(
                kind="write_file",
                path="hello.txt",
                content="hello",
                summary="Create hello.txt",
            )
        ],
    )


def test_web_coder_page_route(web_client: TestClient) -> None:
    response = web_client.get("/coder")
    assert response.status_code == 200
    assert "Agentheim Coder" in response.text


def test_web_coder_session_lifecycle(tmp_path: Path, web_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("workflows.coder.runtime._plan_turn", _workspace_plan)

    created = web_client.post(
        "/api/coder/sessions",
        json={"workspace_root": str(tmp_path), "trust_mode": "workspace"},
    )
    assert created.status_code == 200
    session_id = created.json()["session_id"]

    posted = web_client.post(
        f"/api/coder/sessions/{session_id}/messages",
        json={"prompt": "Create hello.txt"},
    )
    assert posted.status_code == 200
    payload = posted.json()
    assert payload["status"] == "completed"
    assert (tmp_path / "hello.txt").read_text(encoding="utf-8") == "hello"

    loaded = web_client.get(f"/api/coder/sessions/{session_id}")
    assert loaded.status_code == 200
    session = loaded.json()
    assert len(session["transcript"]) >= 2

    run = web_client.get(f"/api/runs/{session_id}")
    assert run.status_code == 200
    run_payload = run.json()
    assert run_payload["workflow_id"] == "coder"
    assert run_payload["preset_id"] == "coder"


def test_web_coder_approval_flow(tmp_path: Path, web_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("workflows.coder.runtime._plan_turn", _ask_plan)

    created = web_client.post(
        "/api/coder/sessions",
        json={"workspace_root": str(tmp_path), "trust_mode": "ask"},
    )
    session_id = created.json()["session_id"]

    posted = web_client.post(
        f"/api/coder/sessions/{session_id}/messages",
        json={"prompt": "Create hello.txt"},
    )
    assert posted.status_code == 200
    approval = posted.json()["pending_approval"]
    assert approval["request_id"]

    granted = web_client.post(f"/api/coder/sessions/{session_id}/approvals/{approval['request_id']}/grant")
    assert granted.status_code == 200
    assert granted.json()["status"] == "completed"
    assert (tmp_path / "hello.txt").read_text(encoding="utf-8") == "hello"


def test_web_coder_websocket_returns_snapshot(tmp_path: Path, web_client: TestClient) -> None:
    created = web_client.post(
        "/api/coder/sessions",
        json={"workspace_root": str(tmp_path), "trust_mode": "ask"},
    )
    session_id = created.json()["session_id"]

    with web_client.websocket_connect(f"/api/coder/sessions/{session_id}/ws") as ws:
        payload = ws.receive_json()
        assert payload["session_id"] == session_id
        assert payload["status"] == "idle"


def test_api_coder_session_endpoints(tmp_path: Path, api_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("workflows.coder.runtime._plan_turn", _workspace_plan)

    created = api_client.post(
        "/api/coder/sessions",
        json={"workspace_root": str(tmp_path), "trust_mode": "workspace"},
        headers={"X-API-Key": "test-key"},
    )
    assert created.status_code == 200
    session_id = created.json()["session_id"]

    listed = api_client.get("/api/coder/sessions", headers={"X-API-Key": "test-key"})
    assert listed.status_code == 200
    assert any(item["session_id"] == session_id for item in listed.json())

    posted = api_client.post(
        f"/api/coder/sessions/{session_id}/messages",
        json={"prompt": "Create hello.txt"},
        headers={"X-API-Key": "test-key"},
    )
    assert posted.status_code == 200
    assert posted.json()["status"] == "completed"
    assert (tmp_path / "hello.txt").exists()
