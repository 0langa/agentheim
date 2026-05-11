"""Feedback loop for self-improving agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FeedbackRecord:
    run_id: str
    success: bool
    correction: str = ""
    metric_delta: dict[str, float] = field(default_factory=dict)


class FeedbackLoop:
    """Captures success/failure signals and stores learned patterns."""

    def __init__(self) -> None:
        self._records: list[FeedbackRecord] = []

    def capture(self, run_id: str, success: bool, correction: str = "", **metrics: float) -> None:
        """Record feedback from a run."""
        self._records.append(
            FeedbackRecord(
                run_id=run_id,
                success=success,
                correction=correction,
                metric_delta=metrics,
            )
        )

    def summarize(self, n: int = 10) -> dict[str, Any]:
        """Summarize recent feedback."""
        recent = self._records[-n:]
        if not recent:
            return {"total": 0, "success_rate": 0.0, "common_corrections": []}

        success_count = sum(1 for r in recent if r.success)
        corrections: dict[str, int] = {}
        for r in recent:
            if r.correction:
                corrections[r.correction] = corrections.get(r.correction, 0) + 1

        return {
            "total": len(recent),
            "success_rate": success_count / len(recent),
            "common_corrections": sorted(corrections.items(), key=lambda x: x[1], reverse=True)[:5],
        }

    def to_memory(self) -> list[dict[str, Any]]:
        """Export records as memory-compatible dicts."""
        return [
            {
                "run_id": r.run_id,
                "success": r.success,
                "correction": r.correction,
                "metric_delta": r.metric_delta,
            }
            for r in self._records
        ]
