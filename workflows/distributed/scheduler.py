"""Task scheduler for distributed workers."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

from workflows.distributed.protocol import TaskAssignment, WorkerRegistration, WorkerStatus


@dataclass
class _WorkerState:
    registration: WorkerRegistration
    last_heartbeat: float
    status: WorkerStatus
    current_task: str | None = None


class TaskScheduler:
    """Round-robin and capability-based task scheduler."""

    def __init__(self, heartbeat_timeout: float = 30.0) -> None:
        self._workers: dict[str, _WorkerState] = {}
        self._pending: list[TaskAssignment] = []
        self._completed: list[str] = []
        self._failed: dict[str, int] = {}
        self.heartbeat_timeout = heartbeat_timeout
        self._max_retries = 3

    def register_worker(self, reg: WorkerRegistration) -> None:
        self._workers[reg.worker_id] = _WorkerState(
            registration=reg,
            last_heartbeat=time.time(),
            status=WorkerStatus.IDLE,
        )

    def heartbeat(self, worker_id: str, status: WorkerStatus) -> None:
        if worker_id in self._workers:
            self._workers[worker_id].last_heartbeat = time.time()
            self._workers[worker_id].status = status

    def submit_task(self, task: TaskAssignment) -> None:
        self._pending.append(task)
        self._pending.sort(key=lambda t: t.priority, reverse=True)

    def next_assignment(self, worker_id: str) -> TaskAssignment | None:
        """Get the next task assignment for a worker."""
        if worker_id not in self._workers:
            return None
        worker = self._workers[worker_id]
        if worker.status != WorkerStatus.IDLE:
            return None

        # Find a task matching worker capabilities
        for i, task in enumerate(self._pending):
            if not task.task_type or task.task_type in worker.registration.capabilities:
                assigned = self._pending.pop(i)
                worker.status = WorkerStatus.BUSY
                worker.current_task = assigned.task_id
                return assigned

        return None

    def complete_task(self, worker_id: str, task_id: str, success: bool) -> None:
        if worker_id in self._workers:
            self._workers[worker_id].status = WorkerStatus.IDLE
            self._workers[worker_id].current_task = None
        if success:
            self._completed.append(task_id)
        else:
            self._failed[task_id] = self._failed.get(task_id, 0) + 1
            # Retry if under max retries
            if self._failed[task_id] < self._max_retries:
                # Re-queue with same priority
                self._pending.append(TaskAssignment(task_id=task_id, task_type="", priority=0))

    def prune_unhealthy_workers(self) -> list[str]:
        """Remove workers that haven't sent a heartbeat. Returns removed IDs."""
        now = time.time()
        removed = []
        for worker_id, state in list(self._workers.items()):
            if now - state.last_heartbeat > self.heartbeat_timeout:
                removed.append(worker_id)
                del self._workers[worker_id]
        return removed

    @property
    def worker_count(self) -> int:
        return len(self._workers)

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    @property
    def completed_count(self) -> int:
        return len(self._completed)
