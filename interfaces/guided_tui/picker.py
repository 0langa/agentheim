"""Preset picker logic for the guided TUI."""

from __future__ import annotations

from rich.console import Console

from typing import Any

from interfaces.guided_tui.render import build_preset_table, print_error, print_info


def pick_preset(console: Console, presets: list[Any]) -> Any | None:
    """Display presets and let the user pick one by number.

    Returns the selected RegistryEntry or None if the user cancels.
    """
    if not presets:
        print_error(console, "No presets are available. Please register a preset first.")
        return None

    console.print(build_preset_table(presets))
    console.print()
    print_info(console, "Enter the number of the preset you want to use, or 'q' to quit.")

    while True:
        try:
            choice = console.input("[bold]Preset #[/bold] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            console.print()
            return None

        if choice in ("q", "quit", "exit", ""):
            return None

        if not choice.isdigit():
            print_error(console, "Please enter a number or 'q' to quit.")
            continue

        idx = int(choice)
        if idx < 1 or idx > len(presets):
            print_error(console, f"Please enter a number between 1 and {len(presets)}.")
            continue

        return presets[idx - 1]
