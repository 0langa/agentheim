"""Hooks for integrating self-improving feedback into the runtime."""

from __future__ import annotations

import logging
from typing import Any

from agents.self_improving.feedback_loop import FeedbackLoop
from agents.self_improving.strategies import (
    ImprovementStrategy,
    ParameterTuningStrategy,
    PromptEvolutionStrategy,
    ToolSelectionStrategy,
)

logger = logging.getLogger(__name__)


class SelfImprovingHook:
    """Captures run feedback and applies improvement strategies."""

    def __init__(self) -> None:
        self.feedback = FeedbackLoop()
        self.strategies: list[ImprovementStrategy] = [
            PromptEvolutionStrategy(),
            ParameterTuningStrategy(),
            ToolSelectionStrategy(),
        ]
        self._state: dict[str, Any] = {
            "prompt": "",
            "params": {},
            "tool_scores": {},
        }

    def on_run_complete(self, run_id: str, success: bool, error: str | None = None, **metrics: float) -> None:
        """Record feedback from a completed run."""
        correction = error or ""
        self.feedback.capture(run_id, success, correction=correction, **metrics)

        # Apply strategies
        context = {
            "feedback": self.feedback.to_memory(),
            "prompt": self._state.get("prompt", ""),
            "params": self._state.get("params", {}),
            "tool_scores": self._state.get("tool_scores", {}),
            "metrics": metrics,
        }
        for strategy in self.strategies:
            try:
                context = strategy.apply(context)
            except Exception as exc:
                logger.warning("Strategy %s failed: %s", type(strategy).__name__, exc)

        self._state["prompt"] = context.get("prompt", "")
        self._state["params"] = context.get("params", {})
        self._state["tool_scores"] = context.get("tool_scores", {})

        summary = self.feedback.summarize(n=10)
        logger.info(
            "Self-improving summary: %d runs, %.0f%% success",
            summary["total"],
            summary["success_rate"] * 100,
        )

    def get_state(self) -> dict[str, Any]:
        """Return current learned state (prompts, params, tool scores)."""
        return dict(self._state)
