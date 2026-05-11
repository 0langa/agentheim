"""In-process worker pool for distributed task execution."""

from __future__ import annotations

import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any, Callable

from workflows.distributed.protocol import TaskAssignment, TaskResult


def _execute_task(payload: dict[str, Any]) -> tuple[bool, Any, str | None]:
    """Default task executor."""
    try:
        result = {"echo": payload}
        return True, result, None
    except Exception as exc:
        return False, None, str(exc)


class WorkerPool:
    """Process-based worker pool for executing tasks in isolation."""

    def __init__(self, max_workers: int | None = None, use_threads: bool = False) -> None:
        self.max_workers = max_workers or (multiprocessing.cpu_count() or 2)
        self._executor: ProcessPoolExecutor | ThreadPoolExecutor | None = None
        self._handlers: dict[str, Callable[[dict[str, Any]], Any]] = {}
        self._use_threads = use_threads

    def register_handler(self, task_type: str, handler: Callable[[dict[str, Any]], Any]) -> None:
        """Register a handler function for a task type."""
        self._handlers[task_type] = handler

    def start(self) -> None:
        if self._executor is None:
            if self._use_threads:
                self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
            else:
                self._executor = ProcessPoolExecutor(max_workers=self.max_workers)

    def stop(self) -> None:
        if self._executor is not None:
            self._executor.shutdown(wait=True)
            self._executor = None

    def submit(self, assignment: TaskAssignment) -> TaskResult:
        """Submit a task for execution. Blocks until complete."""
        if self._executor is None:
            self.start()

        handler = self._handlers.get(assignment.task_type, _execute_task)
        try:
            future = self._executor.submit(handler, assignment.payload)
            result_data = future.result(timeout=300)
            if isinstance(result_data, tuple) and len(result_data) == 3:
                success, data, error = result_data
                return TaskResult(
                    task_id=assignment.task_id,
                    success=success,
                    data=data,
                    error=error,
                )
            return TaskResult(
                task_id=assignment.task_id,
                success=True,
                data=result_data,
            )
        except Exception as exc:
            return TaskResult(
                task_id=assignment.task_id,
                success=False,
                error=str(exc),
            )

    def __enter__(self) -> "WorkerPool":
        self.start()
        return self

    def __exit__(self, *args: Any) -> None:
        self.stop()
