"""Desktop UI scaffold for agent orchestration.

Lightweight native desktop wrapper around the Web UI.
Supports PyQt6 primary and tkinter fallback.
"""

from __future__ import annotations

from interfaces.desktop_ui.app import run_desktop_app

__all__ = ["run_desktop_app"]
