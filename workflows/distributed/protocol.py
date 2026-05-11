"""Distributed worker protocol message schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WorkerStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


@dataclass
class WorkerRegistration:
    worker_id: str
    capabilities: list[str] = field(default_factory=list)
    version: str = "1.0"

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "WorkerRegistration",
            "worker_id": self.worker_id,
            "capabilities": self.capabilities,
            "version": self.version,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "WorkerRegistration":
        return cls(
            worker_id=data["worker_id"],
            capabilities=data.get("capabilities", []),
            version=data.get("version", "1.0"),
        )


@dataclass
class TaskAssignment:
    task_id: str
    task_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    priority: int = 0

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "TaskAssignment",
            "task_id": self.task_id,
            "task_type": self.task_type,
            "payload": self.payload,
            "priority": self.priority,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "TaskAssignment":
        return cls(
            task_id=data["task_id"],
            task_type=data["task_type"],
            payload=data.get("payload", {}),
            priority=data.get("priority", 0),
        )


@dataclass
class TaskResult:
    task_id: str
    success: bool
    data: Any = None
    error: str | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "TaskResult",
            "task_id": self.task_id,
            "success": self.success,
            "data": self.data,
            "error": self.error,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "TaskResult":
        return cls(
            task_id=data["task_id"],
            success=data["success"],
            data=data.get("data"),
            error=data.get("error"),
        )


@dataclass
class Heartbeat:
    worker_id: str
    status: WorkerStatus
    timestamp: float

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Heartbeat",
            "worker_id": self.worker_id,
            "status": self.status.value,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Heartbeat":
        return cls(
            worker_id=data["worker_id"],
            status=WorkerStatus(data.get("status", "idle")),
            timestamp=data.get("timestamp", 0.0),
        )
