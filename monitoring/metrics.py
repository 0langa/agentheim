"""Metrics collection for observability."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RunMetrics:
    run_id: str
    start_time: float
    end_time: float | None = None
    tool_calls: int = 0
    errors: int = 0
    token_usage: int = 0


class MetricsCollector:
    """Collects and exports run-level metrics."""

    def __init__(self) -> None:
        self._runs: dict[str, RunMetrics] = {}
        self._total_tool_calls = 0
        self._total_errors = 0

    def start_run(self, run_id: str) -> None:
        self._runs[run_id] = RunMetrics(run_id=run_id, start_time=time.time())

    def end_run(self, run_id: str) -> None:
        if run_id in self._runs:
            self._runs[run_id].end_time = time.time()

    def record_tool_call(self, run_id: str) -> None:
        if run_id in self._runs:
            self._runs[run_id].tool_calls += 1
        self._total_tool_calls += 1

    def record_error(self, run_id: str) -> None:
        if run_id in self._runs:
            self._runs[run_id].errors += 1
        self._total_errors += 1

    def record_tokens(self, run_id: str, count: int) -> None:
        if run_id in self._runs:
            self._runs[run_id].token_usage += count

    def get_run_metrics(self, run_id: str) -> dict[str, Any] | None:
        m = self._runs.get(run_id)
        if m is None:
            return None
        duration = (m.end_time or time.time()) - m.start_time
        return {
            "run_id": m.run_id,
            "duration_seconds": round(duration, 2),
            "tool_calls": m.tool_calls,
            "errors": m.errors,
            "token_usage": m.token_usage,
        }

    def get_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = [
            "# TYPE agent_runs_total counter",
            f"agent_runs_total {len(self._runs)}",
            "# TYPE agent_tool_calls_total counter",
            f"agent_tool_calls_total {self._total_tool_calls}",
            "# TYPE agent_errors_total counter",
            f"agent_errors_total {self._total_errors}",
        ]
        return "\n".join(lines) + "\n"
