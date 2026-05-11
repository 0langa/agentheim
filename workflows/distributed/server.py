"""FastAPI coordinator server for distributed workers.

Provides HTTP endpoints for worker registration, heartbeats, task polling,
and result submission.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from workflows.distributed.protocol import (
    Heartbeat,
    TaskAssignment,
    TaskResult,
    WorkerRegistration,
    WorkerStatus,
)
from workflows.distributed.scheduler import TaskScheduler


class RegisterRequest(BaseModel):
    worker_id: str
    capabilities: list[str] = Field(default_factory=list)
    version: str = "1.0"


class HeartbeatRequest(BaseModel):
    worker_id: str
    status: str
    timestamp: float


class TaskSubmitRequest(BaseModel):
    task_id: str
    task_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: int = 0


class TaskCompleteRequest(BaseModel):
    worker_id: str
    task_id: str
    success: bool
    data: Any = None
    error: str | None = None


def create_coordinator_app() -> FastAPI:
    app = FastAPI(
        title="Agentheim Distributed Coordinator",
        description="Task coordinator for distributed worker pools",
        version="0.1.0",
    )
    scheduler = TaskScheduler(heartbeat_timeout=30.0)

    @app.post("/api/workers/register")
    def register_worker(req: RegisterRequest) -> dict[str, str]:
        reg = WorkerRegistration(
            worker_id=req.worker_id,
            capabilities=req.capabilities,
            version=req.version,
        )
        scheduler.register_worker(reg)
        return {"status": "registered", "worker_id": req.worker_id}

    @app.post("/api/workers/heartbeat")
    def heartbeat(req: HeartbeatRequest) -> dict[str, str]:
        try:
            status = WorkerStatus(req.status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {req.status}")
        scheduler.heartbeat(req.worker_id, status)
        return {"status": "ok"}

    @app.get("/api/workers/{worker_id}/task")
    def poll_task(worker_id: str) -> dict[str, Any]:
        scheduler.prune_unhealthy_workers()
        assignment = scheduler.next_assignment(worker_id)
        if assignment is None:
            return {"task": None}
        return {"task": assignment.to_json()}

    @app.post("/api/tasks/submit")
    def submit_task(req: TaskSubmitRequest) -> dict[str, str]:
        task = TaskAssignment(
            task_id=req.task_id,
            task_type=req.task_type,
            payload=req.payload,
            priority=req.priority,
        )
        scheduler.submit_task(task)
        return {"status": "submitted", "task_id": req.task_id}

    @app.post("/api/tasks/complete")
    def complete_task(req: TaskCompleteRequest) -> dict[str, str]:
        scheduler.complete_task(req.worker_id, req.task_id, req.success)
        return {"status": "ok"}

    @app.get("/api/status")
    def status() -> dict[str, Any]:
        scheduler.prune_unhealthy_workers()
        return {
            "workers": scheduler.worker_count,
            "pending": scheduler.pending_count,
            "completed": scheduler.completed_count,
        }

    return app
