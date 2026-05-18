from __future__ import annotations

from pathlib import Path

import pytest


def test_create_session_supports_empty_non_git_directory(tmp_path: Path) -> None:
    from workflows.coder.runtime import create_session

    session = create_session(tmp_path, trust_mode="ask")

    assert session.workspace_root == str(tmp_path.resolve())
    assert session.trust_mode == "ask"
    assert session.status == "idle"
    assert session.pending_approval is None


def test_read_only_mode_blocks_write_actions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from workflows.coder.models import CoderAction, CoderTurnPlan
    from workflows.coder.runtime import create_session, post_message

    monkeypatch.setattr(
        "workflows.coder.runtime._plan_turn",
        lambda *args, **kwargs: CoderTurnPlan(
            assistant_message="I will create hello.txt.",
            summary="Create hello file",
            actions=[
                CoderAction(
                    kind="write_file",
                    path="hello.txt",
                    content="hello",
                    summary="Create hello.txt",
                )
            ],
        ),
    )

    session = create_session(tmp_path, trust_mode="read_only")
    updated = post_message(tmp_path, session.session_id, "Create hello.txt")

    assert updated.status == "blocked"
    assert not (tmp_path / "hello.txt").exists()
    assert updated.pending_approval is None


def test_ask_mode_creates_pending_approval_for_writes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from workflows.coder.models import CoderAction, CoderTurnPlan
    from workflows.coder.runtime import create_session, post_message

    monkeypatch.setattr(
        "workflows.coder.runtime._plan_turn",
        lambda *args, **kwargs: CoderTurnPlan(
            assistant_message="I will create hello.txt.",
            summary="Create hello file",
            actions=[
                CoderAction(
                    kind="write_file",
                    path="hello.txt",
                    content="hello",
                    summary="Create hello.txt",
                )
            ],
        ),
    )

    session = create_session(tmp_path, trust_mode="ask")
    updated = post_message(tmp_path, session.session_id, "Create hello.txt")

    assert updated.status == "awaiting_approval"
    assert updated.pending_approval is not None
    assert updated.pending_approval.tool_id == "filesystem"
    assert not (tmp_path / "hello.txt").exists()


def test_workspace_mode_applies_writes_and_tracks_changed_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from workflows.coder.models import CoderAction, CoderTurnPlan
    from workflows.coder.runtime import create_session, post_message

    monkeypatch.setattr(
        "workflows.coder.runtime._plan_turn",
        lambda *args, **kwargs: CoderTurnPlan(
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
        ),
    )

    session = create_session(tmp_path, trust_mode="workspace")
    updated = post_message(tmp_path, session.session_id, "Create hello.txt")

    assert updated.status == "completed"
    assert (tmp_path / "hello.txt").read_text(encoding="utf-8") == "hello"
    assert "hello.txt" in updated.changed_files


def test_approve_request_executes_pending_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from workflows.coder.models import CoderAction, CoderTurnPlan
    from workflows.coder.runtime import approve_request, create_session, post_message

    monkeypatch.setattr(
        "workflows.coder.runtime._plan_turn",
        lambda *args, **kwargs: CoderTurnPlan(
            assistant_message="I will create hello.txt.",
            summary="Create hello file",
            actions=[
                CoderAction(
                    kind="write_file",
                    path="hello.txt",
                    content="hello",
                    summary="Create hello.txt",
                )
            ],
        ),
    )

    session = create_session(tmp_path, trust_mode="ask")
    updated = post_message(tmp_path, session.session_id, "Create hello.txt")
    approved = approve_request(tmp_path, session.session_id, updated.pending_approval.request_id, grant=True)

    assert approved.status == "completed"
    assert (tmp_path / "hello.txt").read_text(encoding="utf-8") == "hello"
    assert approved.pending_approval is None
