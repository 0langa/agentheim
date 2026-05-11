"""Rich rendering helpers for the guided TUI."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def print_header(console: Console, title: str) -> None:
    """Print a bold header."""
    console.print()
    console.rule(f"[bold blue]{title}[/bold blue]")
    console.print()


def print_subheader(console: Console, title: str) -> None:
    """Print a sub-header."""
    console.print(f"[bold cyan]{title}[/bold cyan]")
    console.print()


def print_info(console: Console, message: str) -> None:
    """Print an informational message."""
    console.print(f"[dim]{message}[/dim]")


def print_success(console: Console, message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]✓ {message}[/bold green]")


def print_error(console: Console, message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]✗ {message}[/bold red]")


def print_warning(console: Console, message: str) -> None:
    """Print a warning message."""
    console.print(f"[bold yellow]⚠ {message}[/bold yellow]")


def print_panel(console: Console, title: str, content: str, border_style: str = "blue") -> None:
    """Print content inside a panel."""
    panel = Panel(content, title=title, border_style=border_style)
    console.print(panel)


def build_preset_table(presets: list) -> Table:
    """Build a rich table of available presets."""
    table = Table(title="Available Presets", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Name", min_width=20)
    table.add_column("Description", min_width=30)

    for idx, preset in enumerate(presets, start=1):
        name = _get_preset_name(preset)
        description = _get_preset_description(preset)
        table.add_row(str(idx), name, description)

    return table


def build_summary_table(answers: dict[str, str]) -> Table:
    """Build a rich table of collected answers."""
    table = Table(title="Your Answers", show_header=True, header_style="bold magenta")
    table.add_column("Question", min_width=20)
    table.add_column("Answer", min_width=30)

    for question_id, answer in answers.items():
        table.add_row(question_id, str(answer))

    return table


def _get_preset_name(preset) -> str:
    """Extract human-readable name from a preset registry entry."""
    name = preset.metadata.get("name") if hasattr(preset, "metadata") else None
    if name:
        return name
    if hasattr(preset, "name"):
        return preset.name
    if hasattr(preset, "preset_id"):
        return preset.preset_id
    return preset.id


def _get_preset_description(preset) -> str:
    """Extract description from a preset registry entry."""
    description = preset.metadata.get("description") if hasattr(preset, "metadata") else None
    if description:
        return description
    if hasattr(preset, "description"):
        return preset.description
    return "No description provided."
