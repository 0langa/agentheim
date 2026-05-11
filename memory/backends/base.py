from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class MemoryBackend(ABC):
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path.resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def read(self, key: str, scope: str = "global", run_id: str | None = None) -> dict[str, Any] | None:
        ...

    @abstractmethod
    def write(self, key: str, value: dict[str, Any], scope: str = "global", run_id: str | None = None) -> None:
        ...

    @abstractmethod
    def list_keys(self, scope: str = "global", run_id: str | None = None) -> list[str]:
        ...

    @abstractmethod
    def search(self, query: str, scope: str = "global", run_id: str | None = None) -> list[dict[str, Any]]:
        ...

    def _sanitize_key(self, key: str) -> str:
        safe = "".join(c for c in key if c.isalnum() or c in "-_")
        if not safe:
            raise ValueError("Key contains no safe characters")
        return safe

    def _scope_dir(self, scope: str, run_id: str | None = None) -> Path:
        if scope == "run" and run_id:
            path = self.base_path / "run" / run_id
        elif scope == "repository":
            path = self.base_path / "repository"
        else:
            path = self.base_path / "global"
        path.mkdir(parents=True, exist_ok=True)
        return path
