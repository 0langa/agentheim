"""Questionnaire runner for the guided TUI."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from rich.console import Console

from interfaces.guided_tui.render import print_error, print_info, print_panel, print_success, print_warning


def run_questionnaire(console: Console, questions: list[dict[str, Any]]) -> dict[str, Any]:
    """Run a guided questionnaire and return collected answers.

    Each question dict should have:
        - id: str
        - text: str
        - type: "text" | "choice" | "path" | "boolean"
        - choices: list[str] (for "choice" type)
        - default: Any (optional)
        - help: str (optional)
        - required: bool (default True)
    """
    answers: dict[str, Any] = {}

    if not questions:
        print_warning(console, "This preset has no questions to answer.")
        return answers

    console.print()
    print_panel(console, "Guided Setup", "Answer a few quick questions so I know what you'd like to do.")
    console.print()

    for question in questions:
        answer = _ask_question(console, question)
        answers[question["id"]] = answer

    console.print()
    print_success(console, "All questions answered!")
    console.print()
    return answers


def _ask_question(console: Console, question: dict[str, Any]) -> Any:
    """Ask a single question and return the validated answer."""
    qid = question["id"]
    text = question.get("text", qid)
    qtype = question.get("type", "text")
    default = question.get("default")
    help_text = question.get("help", "")
    required = question.get("required", True)

    # Build prompt label
    prompt_lines = [f"[bold]{text}[/bold]"]
    if help_text:
        prompt_lines.append(f"[dim]{help_text}[/dim]")
    if default is not None:
        prompt_lines.append(f"[dim](default: {default})[/dim]")

    prompt = "\n".join(prompt_lines)

    while True:
        console.print()
        console.print(prompt)

        if qtype == "choice":
            choices = question.get("choices", [])
            for idx, option in enumerate(choices, start=1):
                marker = "*" if option == default else " "
                console.print(f"  {marker}[{idx}] {option}")
            raw = console.input("Choice #: ").strip()
            result = _parse_choice(raw, choices, default, required)
        elif qtype == "boolean":
            raw = console.input("[y/n]: ").strip().lower()
            result = _parse_boolean(raw, default, required)
        elif qtype == "path":
            raw = console.input("Path: ").strip()
            result = _parse_path(console, raw, default, required)
        else:
            # text (default)
            raw = console.input("Answer: ").strip()
            result = _parse_text(raw, default, required)

        if result is not None or (not required and raw == ""):
            return result if result is not None else ""

        print_error(console, "A valid answer is required. Please try again.")


def _parse_text(raw: str, default: Any, required: bool) -> str | None:
    if not raw:
        if default is not None:
            return str(default)
        if not required:
            return ""
        return None
    return raw


def _parse_choice(raw: str, choices: list[str], default: Any, required: bool) -> str | None:
    if not raw:
        if default is not None:
            return str(default)
        if not required:
            return ""
        return None

    # Allow selection by number
    if raw.isdigit():
        idx = int(raw)
        if 1 <= idx <= len(choices):
            return choices[idx - 1]

    # Allow selection by exact text
    if raw in choices:
        return raw

    return None


def _parse_boolean(raw: str, default: Any, required: bool) -> bool | None:
    if not raw:
        if default is not None:
            return bool(default)
        if not required:
            return None
        return None

    if raw in ("y", "yes", "true", "1", "on"):
        return True
    if raw in ("n", "no", "false", "0", "off"):
        return False
    return None


def _parse_path(console: Console, raw: str, default: Any, required: bool) -> str | None:
    if not raw:
        if default is not None:
            return str(default)
        if not required:
            return ""
        return None

    # Expand user home and environment variables
    expanded = os.path.expandvars(os.path.expanduser(raw))
    path = Path(expanded)

    if not path.exists():
        print_error(console, f"Path does not exist: {path}")
        return None

    return str(path.resolve())
