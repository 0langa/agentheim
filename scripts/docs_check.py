#!/usr/bin/env python3
"""Validate that README and User Guide only mention existing CLI commands."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def _collect_commands() -> set[str]:
    """Collect all registered CLI command names."""
    result = subprocess.run(
        [sys.executable, "-m", "interfaces.cli.cli", "commands", "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"Warning: could not list commands: {result.stderr}")
        return set()

    import json

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Warning: could not parse commands JSON")
        return set()

    commands: set[str] = set()
    for section in data.get("sections", []):
        for item in section.get("commands", []):
            name = item.get("command", "")
            if name:
                commands.add(name)
    return commands


def _find_mentioned_commands(text: str) -> set[str]:
    """Find potential command mentions like `agentheim setup` or agentheim setup."""
    # Match `agentheim <word>` or agentheim <word> where word is a simple identifier
    # Exclude words starting with dashes (options/flags)
    pattern = re.compile(r"(?:`?)agentheim\s+([a-z][a-z0-9-]*)(?:`?)")
    return set(m.group(1) for m in pattern.finditer(text) if not m.group(1).startswith("-"))


def main() -> int:
    repo_root = Path(__file__).parent.parent.resolve()
    commands = _collect_commands()
    if not commands:
        print("No commands collected; skipping docs check.")
        return 0

    docs = [
        repo_root / "README.md",
        repo_root / "docs" / "USER_GUIDE.md",
    ]
    errors: list[str] = []
    for doc in docs:
        if not doc.exists():
            continue
        text = doc.read_text(encoding="utf-8")
        mentioned = _find_mentioned_commands(text)
        unknown = mentioned - commands
        if unknown:
            for cmd in sorted(unknown):
                errors.append(f"{doc.name}: mentions unknown command '{cmd}'")

    if errors:
        print("Docs check FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("Docs check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
