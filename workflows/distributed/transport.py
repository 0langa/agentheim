"""HTTP transport client for distributed workers.

Connects to a coordinator server over HTTP for registration, heartbeats,
task polling, and result submission.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from workflows.distributed.protocol import (
    Heartbeat,
    TaskAssignment,
    TaskResult,
    WorkerRegistration,
    WorkerStatus,
)

logger = logging.getLogger(__name__)


class CoordinatorClient:
    """HTTP client for communicating with the coordinator server."""

    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = None

    def _request(self, method: str, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        import requests

        url = f"{self.base_url}{path}"
        try:
            resp = requests.request(
                method, url, json=json, timeout=self.timeout
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.warning("Coordinator request failed: %s %s — %s", method, path, exc)
            raise

    def register(self, reg: WorkerRegistration) -> None:
        self._request(
            "POST",
            "/api/workers/register",
            {
                "worker_id": reg.worker_id,
                "capabilities": reg.capabilities,
                "version": reg.version,
            },
        )

    def heartbeat(self, beat: Heartbeat) -> None:
        self._request(
            "POST",
            "/api/workers/heartbeat",
            {
                "worker_id": beat.worker_id,
                "status": beat.status.value,
                "timestamp": beat.timestamp,
            },
        )

    def poll_task(self, worker_id: str) -> TaskAssignment | None:
        data = self._request("GET", f"/api/workers/{worker_id}/task")
        task_data = data.get("task")
        if task_data is None:
            return None
        return TaskAssignment.from_json(task_data)

    def submit_result(self, result: TaskResult, worker_id: str) -> None:
        self._request(
            "POST",
            "/api/tasks/complete",
            {
                "worker_id": worker_id,
                "task_id": result.task_id,
                "success": result.success,
                "data": result.data,
                "error": result.error,
            },
        )


class RemoteWorker:
    """Worker that connects to a coordinator over HTTP and executes tasks."""

    def __init__(
        self,
        worker_id: str,
        coordinator_url: str,
        capabilities: list[str] | None = None,
    ) -> None:
        self.worker_id = worker_id
        self.client = CoordinatorClient(coordinator_url)
        self.capabilities = capabilities or []
        self._running = False

    def register(self) -> None:
        reg = WorkerRegistration(
            worker_id=self.worker_id,
            capabilities=self.capabilities,
        )
        self.client.register(reg)
        logger.info("Worker %s registered with coordinator", self.worker_id)

    def run(self, handler: Any) -> None:
        """Poll for tasks and execute them using *handler*."""
        self._running = True
        self.register()
        while self._running:
            try:
                self.client.heartbeat(
                    Heartbeat(
                        worker_id=self.worker_id,
                        status=WorkerStatus.IDLE,
                        timestamp=time.time(),
                    )
                )
                assignment = self.client.poll_task(self.worker_id)
                if assignment is not None:
                    logger.info("Worker %s received task %s", self.worker_id, assignment.task_id)
                    try:
                        result_data = handler(assignment.payload)
                        result = TaskResult(
                            task_id=assignment.task_id,
                            success=True,
                            data=result_data,
                        )
                    except Exception as exc:
                        result = TaskResult(
                            task_id=assignment.task_id,
                            success=False,
                            error=str(exc),
                        )
                    self.client.submit_result(result, self.worker_id)
                else:
                    time.sleep(2.0)
            except Exception as exc:
                logger.warning("Worker %s poll loop error: %s", self.worker_id, exc)
                time.sleep(5.0)

    def stop(self) -> None:
        self._running = False
