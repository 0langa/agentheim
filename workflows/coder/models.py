from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TrustMode(StrEnum):
    READ_ONLY = "read_only"
    ASK = "ask"
    WORKSPACE = "workspace"


class SessionStatus(StrEnum):
    IDLE = "idle"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class ActivityKind(StrEnum):
    THINKING = "thinking"
    SCANNING = "scanning"
    EDITING = "editing"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class CoderMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    role: Literal["user", "assistant", "system"]
    content: str
    created_at: str


class CoderAction(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: Literal["list_files", "read_file", "write_file", "run_command"]
    summary: str = ""
    path: str | None = None
    content: str | None = None
    command: list[str] = Field(default_factory=list)


class CoderTurnPlan(BaseModel):
    model_config = ConfigDict(frozen=True)

    assistant_message: str
    summary: str
    actions: list[CoderAction] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


class CoderActivity(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: ActivityKind
    message: str
    created_at: str
    details: dict[str, str] = Field(default_factory=dict)


class PendingApproval(BaseModel):
    model_config = ConfigDict(frozen=True)

    request_id: str
    tool_id: str
    params: dict[str, object] = Field(default_factory=dict)
    risk_level: str
    reason: str
    action_index: int
    status: Literal["pending", "granted", "denied"] = "pending"


class CoderSession(BaseModel):
    session_id: str
    workspace_root: str
    trust_mode: TrustMode
    status: SessionStatus = SessionStatus.IDLE
    created_at: str
    updated_at: str
    transcript: list[CoderMessage] = Field(default_factory=list)
    activities: list[CoderActivity] = Field(default_factory=list)
    changed_files: list[str] = Field(default_factory=list)
    pending_approval: PendingApproval | None = None
    current_user_prompt: str | None = None
    current_assistant_message: str | None = None
    current_summary: str = ""
    planned_actions: list[CoderAction] = Field(default_factory=list)
    next_action_index: int = 0
    git_available: bool = False

