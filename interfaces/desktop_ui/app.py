"""Desktop UI scaffold with PyQt6 primary and tkinter fallback."""

from __future__ import annotations

import sys
import threading
import webbrowser
from pathlib import Path
from typing import Any

from interfaces.web_ui import create_app as create_web_app


def _run_server(repo_root: Path, port: int) -> None:
    """Run the FastAPI server in a background thread."""
    import uvicorn

    app = create_web_app(repo_root=repo_root)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


def _run_pyqt6(repo_root: Path, port: int) -> None:
    """Run the desktop app using PyQt6."""
    from PyQt6.QtCore import QUrl
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
    except ImportError:
        # WebEngine not available, fallback to browser launch
        webbrowser.open(f"http://127.0.0.1:{port}")
        print(f"PyQt6 WebEngine not available. Opened browser at http://127.0.0.1:{port}")
        print("Press Ctrl+C to stop the server.")
        try:
            while True:
                pass
        except KeyboardInterrupt:
            return

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Local Agent Orchestra")
    window.setGeometry(100, 100, 1280, 800)

    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)

    webview = QWebEngineView()
    webview.setUrl(QUrl(f"http://127.0.0.1:{port}"))
    layout.addWidget(webview)

    window.setCentralWidget(central)
    window.show()
    sys.exit(app.exec())


def _run_tkinter(repo_root: Path, port: int) -> None:
    """Run a minimal tkinter desktop wrapper."""
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.title("Local Agent Orchestra")
    root.geometry("800x600")

    tk.Label(root, text="Local Agent Orchestra", font=("Helvetica", 20)).pack(pady=20)
    tk.Label(root, text=f"Server running at http://127.0.0.1:{port}", font=("Helvetica", 12)).pack(pady=10)

    def open_browser() -> None:
        webbrowser.open(f"http://127.0.0.1:{port}")

    tk.Button(root, text="Open in Browser", command=open_browser, font=("Helvetica", 14)).pack(pady=20)
    tk.Button(root, text="Exit", command=root.destroy, font=("Helvetica", 14)).pack(pady=10)

    root.mainloop()


def run_desktop_app(repo_root: str | Path = ".", port: int = 8765) -> None:
    """Launch the desktop UI, choosing the best available framework."""
    repo_root = Path(repo_root).resolve()

    # Start server in background thread
    server_thread = threading.Thread(target=_run_server, args=(repo_root, port), daemon=True)
    server_thread.start()

    # Try PyQt6 first
    try:
        import PyQt6  # noqa: F401
        _run_pyqt6(repo_root, port)
        return
    except ImportError:
        pass

    # Fallback to tkinter (usually available)
    try:
        import tkinter  # noqa: F401
        _run_tkinter(repo_root, port)
        return
    except ImportError:
        pass

    # Last resort: just open browser
    print(f"No GUI framework available. Opening browser at http://127.0.0.1:{port}")
    webbrowser.open(f"http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop the server.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass
