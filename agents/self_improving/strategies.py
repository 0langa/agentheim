"""Self-improvement strategy definitions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ImprovementStrategy(ABC):
    """Base class for self-improvement strategies."""

    @abstractmethod
    def apply(self, context: dict[str, Any]) -> dict[str, Any]:
        """Apply the strategy and return updated context."""
        raise NotImplementedError


class PromptEvolutionStrategy(ImprovementStrategy):
    """Evolves prompts based on feedback patterns."""

    def apply(self, context: dict[str, Any]) -> dict[str, Any]:
        feedback = context.get("feedback", [])
        prompt = context.get("prompt", "")
        if not feedback or not prompt:
            return context

        # Simple heuristic: if failures cluster around a topic, append guidance
        failures = [f for f in feedback if not f.get("success", True)]
        if len(failures) > len(feedback) * 0.3:
            prompt += "\n\n[Learned guidance: Pay extra attention to edge cases.]"

        return {**context, "prompt": prompt}


class ParameterTuningStrategy(ImprovementStrategy):
    """Adjusts parameters based on performance metrics."""

    def apply(self, context: dict[str, Any]) -> dict[str, Any]:
        params = dict(context.get("params", {}))
        metrics = context.get("metrics", {})

        # Simple heuristic: increase timeout if tasks time out
        if metrics.get("timeout_rate", 0) > 0.1:
            params["timeout"] = params.get("timeout", 30) * 1.5

        return {**context, "params": params}


class ToolSelectionStrategy(ImprovementStrategy):
    """Adjusts tool selection based on success rates."""

    def apply(self, context: dict[str, Any]) -> dict[str, Any]:
        tool_scores = dict(context.get("tool_scores", {}))
        feedback = context.get("feedback", [])

        for record in feedback:
            tool = record.get("tool")
            if tool:
                score = tool_scores.get(tool, 0.5)
                delta = 0.1 if record.get("success") else -0.1
                tool_scores[tool] = max(0.0, min(1.0, score + delta))

        return {**context, "tool_scores": tool_scores}
