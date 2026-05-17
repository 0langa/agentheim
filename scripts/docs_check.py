#!/usr/bin/env python3
"""Validate documentation against the live CLI and internal links."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def _collect_commands() -> dict[str, str]:
    """Collect all registered CLI command names mapped to their kind ('command' or 'group')."""
    result = subprocess.run(
        [sys.executable, "-m", "interfaces.cli.cli", "commands", "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"Warning: could not list commands: {result.stderr}")
        return {}

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Warning: could not parse commands JSON")
        return {}

    commands: dict[str, str] = {}
    for section in data.get("sections", []):
        for item in section.get("commands", []):
            name = item.get("command", "")
            kind = item.get("kind", "command")
            if name:
                commands[name] = kind
    return commands


def _find_mentioned_commands(text: str) -> set[str]:
    """Find potential command mentions like `agentheim setup` or agentheim setup."""
    pattern = re.compile(r"(?:`?)agentheim\s+([a-z][a-z0-9-]*)(?:`?)")
    return set(m.group(1) for m in pattern.finditer(text) if not m.group(1).startswith("-"))


def _find_markdown_links(text: str, doc_path: Path) -> list[tuple[str, str]]:
    """Find all local markdown links in the text. Returns list of (link_target, line)."""
    links: list[tuple[str, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", line):
            target = match.group(2)
            # Skip external links, anchors-only, and mailto
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            # Strip anchor
            target = target.split("#")[0]
            if target:
                links.append((target, f"{doc_path}:{lineno}"))
    return links


def _check_local_links(repo_root: Path) -> list[str]:
    """Check that all local markdown links point to existing files."""
    docs_dir = repo_root / "docs"
    readme = repo_root / "README.md"
    all_docs = [readme] + list(docs_dir.glob("*.md"))

    errors: list[str] = []
    for doc in all_docs:
        text = doc.read_text(encoding="utf-8")
        for target, line_ref in _find_markdown_links(text, doc):
            # Resolve relative to the doc's directory
            if doc.parent == repo_root:
                resolved = repo_root / target
            else:
                resolved = doc.parent / target
            if not resolved.exists():
                errors.append(f"{line_ref} -> broken link '{target}'")
    return errors


def _check_cli_commands_doc(repo_root: Path, live_commands: dict[str, str]) -> list[str]:
    """Validate that docs/CLI-COMMANDS.md mentions all live user-callable commands."""
    cli_doc = repo_root / "docs" / "CLI-COMMANDS.md"
    if not cli_doc.exists():
        return ["docs/CLI-COMMANDS.md not found"]

    text = cli_doc.read_text(encoding="utf-8")
    # Extract backtick-wrapped command names from tables (supports spaces for subcommands)
    found: set[str] = set()
    for match in re.finditer(r"`([a-z][a-z0-9-]+(?: [a-z][a-z0-9-]+)*)`", text):
        found.add(match.group(1))

    # Only require kind="command" entries; skip structural group names
    root_live = {c for c, k in live_commands.items() if k == "command" and "." not in c}
    missing = root_live - found

    errors: list[str] = []
    if missing:
        for cmd in sorted(missing):
            errors.append(f"docs/CLI-COMMANDS.md: missing root command '{cmd}'")
    return errors


def main() -> int:
    repo_root = Path(__file__).parent.parent.resolve()
    commands = _collect_commands()

    all_errors: list[str] = []

    # 1. Check that docs only mention existing CLI commands
    if commands:
        docs = [
            repo_root / "README.md",
            repo_root / "docs" / "USER_GUIDE.md",
            repo_root / "docs" / "CLI-COMMANDS.md",
        ]
        live_names = set(commands.keys())
        for doc in docs:
            if not doc.exists():
                continue
            text = doc.read_text(encoding="utf-8")
            mentioned = _find_mentioned_commands(text)
            unknown = mentioned - live_names
            if unknown:
                for cmd in sorted(unknown):
                    all_errors.append(f"{doc.name}: mentions unknown command '{cmd}'")

        # 2. Check CLI-COMMANDS.md coverage
        all_errors.extend(_check_cli_commands_doc(repo_root, commands))
    else:
        print("Warning: could not collect live commands; skipping command checks.")

    # 3. Check local markdown links
    all_errors.extend(_check_local_links(repo_root))

    if all_errors:
        print("Docs check FAILED:")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print("Docs check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
