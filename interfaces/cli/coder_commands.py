from __future__ import annotations

import json
import threading
import time
import webbrowser
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from workflows.coder.runtime import approve_request, create_session, get_session, list_sessions, post_message


coder_app = typer.Typer(help="Persistent local coding sessions.", invoke_without_command=True)
console = Console()


def _start_web_server(repo_root: Path, port: int) -> threading.Thread:
    from interfaces.desktop_ui.app import _run_server

    thread = threading.Thread(target=_run_server, args=(repo_root, port), daemon=True)
    thread.start()
    return thread


def _wait_for_web_server(port: int) -> bool:
    from interfaces.desktop_ui.app import _wait_for_server

    return _wait_for_server(port, timeout=15.0)


def _render_session(session) -> None:
    console.print(f"session id: {session.session_id}")
    console.print(f"workspace: {session.workspace_root}")
    console.print(f"trust mode: {session.trust_mode}")
    console.print(f"status: {session.status}")
    if session.current_assistant_message:
        console.print(f"assistant: {session.current_assistant_message}")
    if session.pending_approval:
        console.print(f"approval pending: {session.pending_approval.request_id} ({session.pending_approval.tool_id})")


def _interactive_loop(workspace: Path, session) -> None:
    console.print("Interactive coder session. Type `exit` to leave.")
    current = session
    while True:
        entered = typer.prompt("coder", prompt_suffix="> ", default="", show_default=False).strip()
        if entered.lower() in {"exit", "quit"}:
            break
        if not entered:
            continue
        current = post_message(workspace.resolve(), current.session_id, entered)
        _render_session(current)
        if current.pending_approval:
            decision = typer.confirm("Grant the pending approval?", default=False)
            if decision:
                current = approve_request(workspace.resolve(), current.session_id, current.pending_approval.request_id, grant=True)
            else:
                current = approve_request(workspace.resolve(), current.session_id, current.pending_approval.request_id, grant=False)
            _render_session(current)


@coder_app.callback()
def coder_root(
    ctx: typer.Context,
    workspace: Path = typer.Option(Path.cwd(), "--workspace", help="Workspace directory for the coder session."),
    prompt: str | None = typer.Option(None, "--prompt", help="Optional first prompt for a new coder session."),
    trust_mode: str = typer.Option("ask", "--trust-mode", help="Trust mode: read_only, ask, workspace."),
    as_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON output."),
) -> None:
    if ctx.invoked_subcommand is not None:
        return
    session = create_session(workspace.resolve(), trust_mode=trust_mode)
    if prompt:
        session = post_message(workspace.resolve(), session.session_id, prompt)
    if as_json:
        console.print_json(json.dumps(session.model_dump(mode="json")))
        return
    _render_session(session)
    if not prompt:
        _interactive_loop(workspace.resolve(), session)


@coder_app.command("ui")
def coder_ui(
    workspace: Path = typer.Option(Path.cwd(), "--workspace", help="Workspace directory to serve in the coder UI."),
    port: int = typer.Option(8765, "--port", help="Port for the local coder UI."),
    no_browser: bool = typer.Option(False, "--no-browser", help="Start the coder UI without opening a browser."),
    as_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON output."),
) -> None:
    url = f"http://127.0.0.1:{port}/coder"
    if as_json:
        console.print_json(json.dumps({"url": url, "workspace": str(workspace.resolve())}))
        return
    _start_web_server(workspace.resolve(), port)
    if not _wait_for_web_server(port):
        raise typer.BadParameter(f"Coder UI failed to start on {url}")
    if not no_browser:
        webbrowser.open(url)
    console.print(f"Agentheim Coder UI: {url}")


@coder_app.command("list")
def coder_list(
    workspace: Path = typer.Option(Path.cwd(), "--workspace", help="Workspace directory to inspect."),
    as_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON output."),
) -> None:
    sessions = list_sessions(workspace.resolve())
    if as_json:
        console.print_json(json.dumps([session.model_dump(mode="json") for session in sessions]))
        return
    table = Table(title="Coder Sessions")
    table.add_column("Session")
    table.add_column("Status")
    table.add_column("Trust")
    for session in sessions:
        table.add_row(session.session_id, str(session.status), str(session.trust_mode))
    console.print(table)


@coder_app.command("resume")
def coder_resume(
    session_id: str,
    workspace: Path = typer.Option(Path.cwd(), "--workspace", help="Workspace directory for the session."),
    prompt: str | None = typer.Option(None, "--prompt", help="Optional follow-up prompt."),
    grant: str | None = typer.Option(None, "--grant", help="Grant a pending approval request by id."),
    deny: str | None = typer.Option(None, "--deny", help="Deny a pending approval request by id."),
    as_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON output."),
) -> None:
    if grant and deny:
        raise typer.BadParameter("Use only one of --grant or --deny.")
    if grant:
        session = approve_request(workspace.resolve(), session_id, grant, grant=True)
    elif deny:
        session = approve_request(workspace.resolve(), session_id, deny, grant=False)
    elif prompt:
        session = post_message(workspace.resolve(), session_id, prompt)
    else:
        session = get_session(workspace.resolve(), session_id)
    if as_json:
        console.print_json(json.dumps(session.model_dump(mode="json")))
        return
    _render_session(session)
    if not any([grant, deny, prompt]):
        _interactive_loop(workspace.resolve(), session)
