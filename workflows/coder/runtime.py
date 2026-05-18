from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from config.config import ModelRole, load_team_config
from core.public_api import (
    ApprovalRequest,
    EventType,
    PolicyConfig,
    PolicyEngine,
    RiskLevel,
    RunLedger,
    ToolContext,
    ToolInvoker,
    build_model_registry,
    inspect_repository,
    repair_json_text,
    safe_project_path,
    safe_run_id,
)
from providers.base import ModelRequest
from tools.registry import create_core_tool_registry
from workflows.coder.models import (
    ActivityKind,
    CoderAction,
    CoderActivity,
    CoderMessage,
    CoderSession,
    CoderTurnPlan,
    PendingApproval,
    SessionStatus,
    TrustMode,
)


WORKFLOW_ID = "coder"
PRESET_ID = "coder"
SAFE_COMMANDS = ("python", "pytest", "git", "npm", "node", "pip", "poetry", "cargo", "go", "dotnet")


def _utcnow() -> str:
    return datetime.now(tz=UTC).isoformat()


def _session_paths(workspace_root: Path, session_id: str) -> dict[str, Path]:
    run_dir = workspace_root / ".ai-team" / "runs" / safe_run_id(session_id)
    return {
        "run_dir": run_dir,
        "session": run_dir / "session.json",
        "transcript": run_dir / "transcript.jsonl",
        "activity": run_dir / "activity.jsonl",
        "final_report": run_dir / "final_report.json",
        "final_report_md": run_dir / "final_report.md",
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _policy_config(trust_mode: TrustMode) -> PolicyConfig:
    risk_rules = {
        RiskLevel.NONE: "allow",
        RiskLevel.LOW: "allow",
        RiskLevel.MEDIUM: "ask",
        RiskLevel.HIGH: "ask",
        RiskLevel.CRITICAL: "deny",
    }
    if trust_mode == TrustMode.READ_ONLY:
        risk_rules[RiskLevel.MEDIUM] = "deny"
        risk_rules[RiskLevel.HIGH] = "deny"
    elif trust_mode == TrustMode.WORKSPACE:
        risk_rules[RiskLevel.MEDIUM] = "allow"
        risk_rules[RiskLevel.HIGH] = "allow"
    return PolicyConfig(
        risk_rules=risk_rules,
        command_allowlist=list(SAFE_COMMANDS),
        network_allowed=False,
        local_only=True,
    )


def _tool_context(workspace_root: Path) -> ToolContext:
    return ToolContext(
        workspace=workspace_root,
        allowed_paths=[str(workspace_root)],
        denied_paths=[str(workspace_root / ".git")],
        allowed_commands=list(SAFE_COMMANDS),
        network_allowed=False,
    )


def _load_session(workspace_root: Path, session_id: str) -> CoderSession:
    paths = _session_paths(workspace_root, session_id)
    data = json.loads(paths["session"].read_text(encoding="utf-8"))
    session = CoderSession.model_validate(data)
    transcript: list[CoderMessage] = []
    if paths["transcript"].exists():
        for line in paths["transcript"].read_text(encoding="utf-8").splitlines():
            if line.strip():
                transcript.append(CoderMessage.model_validate(json.loads(line)))
    activities: list[CoderActivity] = []
    if paths["activity"].exists():
        for line in paths["activity"].read_text(encoding="utf-8").splitlines():
            if line.strip():
                activities.append(CoderActivity.model_validate(json.loads(line)))
    return session.model_copy(update={"transcript": transcript, "activities": activities})


def _save_session(workspace_root: Path, session: CoderSession) -> CoderSession:
    paths = _session_paths(workspace_root, session.session_id)
    paths["run_dir"].mkdir(parents=True, exist_ok=True)
    _write_json(paths["session"], session.model_dump(mode="json"))
    _write_json(
        paths["final_report"],
        {
            "status": (
                "blocked"
                if session.status in {SessionStatus.AWAITING_APPROVAL, SessionStatus.BLOCKED}
                else "done" if session.status == SessionStatus.COMPLETED
                else "running" if session.status == SessionStatus.RUNNING
                else "pending"
            ),
            "task_summary": session.current_summary or "Coder session",
            "summary": session.current_assistant_message or "Coder session ready.",
            "changed_files": session.changed_files,
            "next_command_suggestions": [f"agentheim coder resume {session.session_id} --workspace {workspace_root}"],
        },
    )
    paths["final_report_md"].write_text(
        "\n".join(
            [
                f"# Coder Session {session.session_id}",
                "",
                f"- Status: {session.status.value}",
                f"- Workspace: {session.workspace_root}",
                f"- Trust mode: {session.trust_mode.value}",
                "",
                session.current_assistant_message or "Coder session ready.",
            ]
        ),
        encoding="utf-8",
    )
    return session


def _append_message(workspace_root: Path, session_id: str, message: CoderMessage) -> None:
    _append_jsonl(_session_paths(workspace_root, session_id)["transcript"], message.model_dump(mode="json"))


def _append_activity(workspace_root: Path, session_id: str, activity: CoderActivity) -> None:
    _append_jsonl(_session_paths(workspace_root, session_id)["activity"], activity.model_dump(mode="json"))


def _record_activity(workspace_root: Path, session: CoderSession, kind: ActivityKind, message: str, details: dict[str, str] | None = None) -> CoderSession:
    activity = CoderActivity(kind=kind, message=message, created_at=_utcnow(), details=details or {})
    _append_activity(workspace_root, session.session_id, activity)
    activities = [*session.activities, activity]
    return session.model_copy(update={"activities": activities, "updated_at": activity.created_at})


def _set_status(session: CoderSession, status: SessionStatus) -> CoderSession:
    return session.model_copy(update={"status": status, "updated_at": _utcnow()})


def _workspace_scan_summary(workspace_root: Path) -> tuple[dict[str, Any], bool]:
    scan = inspect_repository(workspace_root)
    summary = {
        "repo_name": scan.repo_name,
        "languages": scan.languages,
        "manifests": scan.manifests,
        "warnings": scan.warnings,
        "file_count": len(scan.files),
        "git_available": scan.git.is_git_repo,
    }
    return summary, scan.git.is_git_repo


def _open_ledger(workspace_root: Path, session_id: str) -> RunLedger:
    ledger = RunLedger(repo_root=workspace_root, run_dir=_session_paths(workspace_root, session_id)["run_dir"])
    if (ledger.run_dir / "ledger.jsonl").exists():
        ledger._restore_sequence_from_ledger()  # type: ignore[attr-defined]
    return ledger


def _plan_turn(workspace_root: Path, session: CoderSession, prompt: str) -> CoderTurnPlan:
    workspace_summary, _ = _workspace_scan_summary(workspace_root)
    try:
        config = load_team_config()
        registry = build_model_registry(config)
        planner_model = registry.resolve_model(ModelRole.PLANNER.value, "json")
        provider = registry.create_provider(planner_model.config)
        request = ModelRequest(
            role=planner_model.config.role,
            system_prompt=(
                "You are Agentheim Coder. Return only valid JSON matching this schema: "
                '{"assistant_message":"string","summary":"string","actions":[{"kind":"list_files|read_file|write_file|run_command","summary":"string","path":"optional string","content":"optional string","command":["optional","command"]}],"next_actions":["string"]}. '
                "Prefer bounded local workspace actions. Do not use network actions."
            ),
            user_prompt=(
                f"Workspace summary: {json.dumps(workspace_summary)}\n"
                f"Trust mode: {session.trust_mode.value}\n"
                f"Transcript tail: {[m.model_dump(mode='json') for m in session.transcript[-6:]]}\n"
                f"User prompt: {prompt}"
            ),
            temperature=0.0,
            max_output_tokens=3000,
        )
        response = provider.invoke(request)
        data = json.loads(repair_json_text(response.content))
        return CoderTurnPlan.model_validate(data)
    except Exception:
        lowered = prompt.lower()
        actions: list[CoderAction] = []
        if "create " in lowered and ".txt" in lowered:
            filename = prompt.split()[-1]
            actions.append(CoderAction(kind="write_file", path=filename, content="", summary=f"Create {filename}"))
        return CoderTurnPlan(
            assistant_message="I reviewed the workspace and prepared the next local steps.",
            summary="Workspace reviewed",
            actions=actions,
            next_actions=["Review the proposed actions and continue the session."],
        )


def _create_invoker(workspace_root: Path, trust_mode: TrustMode) -> ToolInvoker:
    registry = create_core_tool_registry(workspace_root)
    policy_engine = PolicyEngine(_policy_config(trust_mode))
    return ToolInvoker(registry=registry, policy_engine=policy_engine)


def _invoke_action(
    workspace_root: Path,
    ledger: RunLedger,
    session: CoderSession,
    action: CoderAction,
) -> tuple[CoderSession, bool]:
    invoker = _create_invoker(workspace_root, session.trust_mode)
    context = _tool_context(workspace_root)

    tool_id = "filesystem"
    params: dict[str, Any]
    activity_kind = ActivityKind.THINKING
    if action.kind == "list_files":
        params = {"operation": "list", "path": action.path or "."}
        activity_kind = ActivityKind.SCANNING
    elif action.kind == "read_file":
        params = {"operation": "read", "path": action.path or "."}
        activity_kind = ActivityKind.SCANNING
    elif action.kind == "write_file":
        params = {"operation": "write", "path": action.path or ".", "content": action.content or ""}
        activity_kind = ActivityKind.EDITING
    elif action.kind == "run_command":
        tool_id = "shell.execute"
        params = {"command": action.command, "timeout_seconds": 120}
        activity_kind = ActivityKind.RUNNING
    else:
        session = _record_activity(workspace_root, session, ActivityKind.BLOCKED, f"Unsupported action kind: {action.kind}")
        return _set_status(session, SessionStatus.FAILED), False

    session = _record_activity(workspace_root, session, activity_kind, action.summary or action.kind)
    result = invoker.invoke(tool_id, params, context, ledger=ledger)
    if result.requires_approval:
        request_id = uuid4().hex
        risk_level = result.policy.risk_level.value if result.policy else "medium"
        reason = result.policy.reason if result.policy else "approval required"
        ledger.emit_event(
            EventType.APPROVAL_REQUESTED,
            tool_id=tool_id,
            payload={"request_id": request_id, "params": params, "risk_level": risk_level, "reason": reason},
        )
        pending = PendingApproval(
            request_id=request_id,
            tool_id=tool_id,
            params=params,
            risk_level=risk_level,
            reason=reason,
            action_index=session.next_action_index,
        )
        session = session.model_copy(update={"pending_approval": pending})
        session = _record_activity(workspace_root, session, ActivityKind.AWAITING_APPROVAL, reason)
        return _set_status(session, SessionStatus.AWAITING_APPROVAL), False
    if not result.success:
        session = _record_activity(workspace_root, session, ActivityKind.BLOCKED, result.error or f"{tool_id} failed")
        return _set_status(session, SessionStatus.BLOCKED), False

    changed_files = list(session.changed_files)
    if action.kind == "write_file" and action.path and action.path not in changed_files:
        changed_files.append(action.path)
    session = session.model_copy(
        update={
            "changed_files": changed_files,
            "next_action_index": session.next_action_index + 1,
            "updated_at": _utcnow(),
        }
    )
    return session, True


def _complete_turn(workspace_root: Path, ledger: RunLedger, session: CoderSession) -> CoderSession:
    message = CoderMessage(role="assistant", content=session.current_assistant_message or "Coder turn completed.", created_at=_utcnow())
    _append_message(workspace_root, session.session_id, message)
    session = session.model_copy(update={"transcript": [*session.transcript, message], "updated_at": message.created_at})
    session = _record_activity(workspace_root, session, ActivityKind.COMPLETED, session.current_summary or "Turn completed")
    ledger.emit_event(EventType.RUN_COMPLETED, payload={"workflow_id": WORKFLOW_ID, "status": "completed"})
    return _set_status(session, SessionStatus.COMPLETED)


def _run_actions(workspace_root: Path, ledger: RunLedger, session: CoderSession) -> CoderSession:
    while session.next_action_index < len(session.planned_actions):
        action = session.planned_actions[session.next_action_index]
        session, should_continue = _invoke_action(workspace_root, ledger, session, action)
        if not should_continue:
            return session
    return _complete_turn(workspace_root, ledger, session)


def create_session(workspace_root: str | Path, *, trust_mode: str = "ask") -> CoderSession:
    workspace = safe_project_path(workspace_root)
    trust = TrustMode(trust_mode)
    scan_summary, git_available = _workspace_scan_summary(workspace)
    ledger = RunLedger.create(workspace, "coder")
    session = CoderSession(
        session_id=ledger.run_dir.name,
        workspace_root=str(workspace),
        trust_mode=trust,
        created_at=_utcnow(),
        updated_at=_utcnow(),
        git_available=git_available,
    )
    ledger.write_json(
        "run.json",
        {
            "run_id": session.session_id,
            "workflow_id": WORKFLOW_ID,
            "preset_id": PRESET_ID,
            "repo_root": str(workspace),
            "created_at": session.created_at,
            "trust_mode": trust.value,
            "status": session.status.value,
            "workspace_summary": scan_summary,
        },
    )
    ledger.emit_event(
        EventType.RUN_INITIATED,
        payload={"workflow_id": WORKFLOW_ID, "repo_root": str(workspace), "metadata": {"trust_mode": trust.value}},
    )
    _save_session(workspace, session)
    return session


def get_session(workspace_root: str | Path, session_id: str) -> CoderSession:
    workspace = safe_project_path(workspace_root)
    return _load_session(workspace, session_id)


def list_sessions(workspace_root: str | Path) -> list[CoderSession]:
    workspace = safe_project_path(workspace_root)
    runs_dir = workspace / ".ai-team" / "runs"
    if not runs_dir.exists():
        return []
    sessions: list[CoderSession] = []
    for run_dir in sorted(runs_dir.iterdir(), reverse=True):
        run_json = run_dir / "run.json"
        session_json = run_dir / "session.json"
        if not run_json.exists() or not session_json.exists():
            continue
        try:
            run_data = json.loads(run_json.read_text(encoding="utf-8"))
        except Exception:
            continue
        if run_data.get("workflow_id") != WORKFLOW_ID:
            continue
        try:
            sessions.append(_load_session(workspace, run_dir.name))
        except Exception:
            continue
    sessions.sort(key=lambda item: item.updated_at, reverse=True)
    return sessions


def post_message(workspace_root: str | Path, session_id: str, prompt: str) -> CoderSession:
    workspace = safe_project_path(workspace_root)
    session = _load_session(workspace, session_id)
    user_message = CoderMessage(role="user", content=prompt, created_at=_utcnow())
    _append_message(workspace, session.session_id, user_message)
    session = session.model_copy(update={"transcript": [*session.transcript, user_message]})
    session = _set_status(session, SessionStatus.RUNNING)
    session = _record_activity(workspace, session, ActivityKind.THINKING, "Planning next turn.")
    session = _record_activity(workspace, session, ActivityKind.SCANNING, "Scanning workspace state.")

    ledger = _open_ledger(workspace, session_id)
    try:
        plan = _plan_turn(workspace, session, prompt)
    except Exception as exc:
        ledger.emit_event(EventType.RUN_FAILED, payload={"workflow_id": WORKFLOW_ID, "reason": str(exc), "error_type": type(exc).__name__})
        session = session.model_copy(update={"current_summary": "Coder turn failed", "current_assistant_message": str(exc)})
        session = _set_status(session, SessionStatus.FAILED)
        return _save_session(workspace, session)

    session = session.model_copy(
        update={
            "current_user_prompt": prompt,
            "current_assistant_message": plan.assistant_message,
            "current_summary": plan.summary,
            "planned_actions": plan.actions,
            "next_action_index": 0,
            "pending_approval": None,
            "updated_at": _utcnow(),
        }
    )
    session = _run_actions(workspace, ledger, session)
    return _save_session(workspace, session)


def approve_request(workspace_root: str | Path, session_id: str, request_id: str, *, grant: bool) -> CoderSession:
    workspace = safe_project_path(workspace_root)
    session = _load_session(workspace, session_id)
    pending = session.pending_approval
    if pending is None or pending.request_id != request_id:
        raise ValueError(f"Approval request '{request_id}' not found for session '{session_id}'.")

    ledger = _open_ledger(workspace, session_id)
    if not grant:
        ledger.emit_event(EventType.APPROVAL_DENIED, tool_id=pending.tool_id, payload={"request_id": request_id})
        session = session.model_copy(update={"pending_approval": None})
        session = _record_activity(workspace, session, ActivityKind.BLOCKED, "Approval denied.")
        session = _set_status(session, SessionStatus.BLOCKED)
        return _save_session(workspace, session)

    ledger.emit_event(EventType.APPROVAL_GRANTED, tool_id=pending.tool_id, payload={"request_id": request_id})
    invoker = _create_invoker(workspace, session.trust_mode)
    result = invoker.invoke(
        pending.tool_id,
        pending.params,
        _tool_context(workspace),
        ledger=ledger,
        granted_request=ApprovalRequest(
            request_id=request_id,
            tool_id=pending.tool_id,
            action=str(pending.params.get("operation", "invoke")),
            target=str(pending.params.get("path", pending.params.get("command", pending.tool_id))),
            risk_level=RiskLevel(pending.risk_level),
            justification=pending.reason,
            params_redacted=pending.params,
            timestamp=_utcnow(),
            decision="allow",
            policy_id="coder_approval_override",
            override_possible=False,
        ),
    )
    if not result.success:
        session = session.model_copy(update={"pending_approval": None})
        session = _record_activity(workspace, session, ActivityKind.BLOCKED, result.error or "Approved action failed.")
        session = _set_status(session, SessionStatus.BLOCKED)
        return _save_session(workspace, session)

    changed_files = list(session.changed_files)
    path = str(pending.params.get("path", ""))
    if pending.tool_id == "filesystem" and path and path not in changed_files:
        changed_files.append(path)
    session = session.model_copy(
        update={
            "pending_approval": None,
            "changed_files": changed_files,
            "next_action_index": pending.action_index + 1,
            "updated_at": _utcnow(),
        }
    )
    session = _run_actions(workspace, ledger, _set_status(session, SessionStatus.RUNNING))
    return _save_session(workspace, session)
