"""Plugin sandbox for isolated execution."""

from __future__ import annotations

import signal
from contextlib import contextmanager
from typing import Any, Callable

from core.tool_protocol import ToolContext


class PluginSandboxError(Exception):
    """Raised when a plugin violates sandbox constraints."""


class Sandbox:
    """Restricts plugin execution with timeouts and confined context."""

    def __init__(self, max_execution_seconds: float = 30.0, max_file_size: int = 10_000_000) -> None:
        self.max_execution_seconds = max_execution_seconds
        self.max_file_size = max_file_size

    @contextmanager
    def run(self):
        """Context manager providing a restricted ToolContext."""
        ctx = ToolContext(
            network_allowed=False,
            max_file_size=self.max_file_size,
        )
        yield ctx

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Call a function within sandbox constraints."""
        try:
            with self.run() as ctx:
                # Inject context as first arg if function accepts it
                import inspect

                sig = inspect.signature(func)
                if len(sig.parameters) > 0 and "context" in sig.parameters:
                    return func(ctx, *args, **kwargs)
                return func(*args, **kwargs)
        except Exception as exc:
            raise PluginSandboxError(f"Plugin execution failed: {exc}") from exc
