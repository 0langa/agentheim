"""Web UI prototype for agent orchestration.

FastAPI-based dashboard and API for tools, workflows, presets, and memory.
"""

from __future__ import annotations

from interfaces.web_ui.app import create_app

__all__ = ["create_app"]
