from __future__ import annotations

from pathlib import Path

import pytest


class TestDesktopUI:
    def test_import(self) -> None:
        from interfaces.desktop_ui import run_desktop_app

        assert callable(run_desktop_app)

    def test_pyqt6_import_or_skip(self) -> None:
        try:
            import PyQt6  # noqa: F401
            assert True
        except ImportError:
            pytest.skip("PyQt6 not available")

    def test_tkinter_import(self) -> None:
        import tkinter

        assert tkinter is not None

    def test_server_thread_logic(self, tmp_path: Path) -> None:
        from interfaces.desktop_ui.app import _run_server

        # We can't actually start the server in tests (would bind port),
        # but we verify the function signature is callable
        assert callable(_run_server)
