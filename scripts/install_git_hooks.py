#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIR = ROOT / ".githooks"


def main() -> int:
    subprocess.run(
        ["git", "config", "core.hooksPath", str(HOOKS_DIR)],
        cwd=ROOT,
        check=True,
    )
    print(f"Configured git hooks path: {HOOKS_DIR}")
    print("post-commit will now refresh .kimi/memory.jsonl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
