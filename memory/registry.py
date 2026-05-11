from __future__ import annotations

from pathlib import Path
from typing import Any

from memory.backends.base import MemoryBackend
from memory.backends.jsonl import JsonlBackend
from memory.backends.sqlite import SqliteBackend
from memory.backends.vector import VectorBackend


class MemoryRegistry:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.base_path = self.repo_root / ".ai-team" / "memory"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._backends: dict[str, MemoryBackend] = {
            "jsonl": JsonlBackend(self.base_path / "jsonl"),
            "sqlite": SqliteBackend(self.base_path / "sqlite"),
            "vector": VectorBackend(self.base_path / "vector"),
        }

    def get(self, name: str) -> MemoryBackend:
        if name not in self._backends:
            raise KeyError(f"Memory backend '{name}' not registered")
        return self._backends[name]

    def register(self, name: str, backend: MemoryBackend) -> None:
        self._backends[name] = backend

    def list_backends(self) -> list[str]:
        return list(self._backends.keys())

    def read(self, backend: str, key: str, scope: str = "global", run_id: str | None = None) -> Any:
        return self.get(backend).read(key, scope, run_id)

    def write(self, backend: str, key: str, value: Any, scope: str = "global", run_id: str | None = None) -> None:
        return self.get(backend).write(key, value, scope, run_id)

    def search(self, backend: str, query: str, scope: str = "global", run_id: str | None = None) -> list[dict[str, Any]]:
        return self.get(backend).search(query, scope, run_id)


_default_registries: dict[Path, MemoryRegistry] = {}


def get_default_registry(repo_root: Path) -> MemoryRegistry:
    resolved = repo_root.resolve()
    if resolved not in _default_registries:
        _default_registries[resolved] = MemoryRegistry(resolved)
    return _default_registries[resolved]
