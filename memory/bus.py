from __future__ import annotations

import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from filelock import FileLock

from memory.backends.base import MemoryBackend
from memory.backends.jsonl import JsonlBackend
from memory.backends.sqlite import SqliteBackend
from memory.backends.vector import VectorBackend


class MemoryBus:
    """Cross-process safe memory bus with intra-process thread locking.

    Write operations acquire both a thread lock (same process) and
    a file lock (cross process). Read operations acquire only the thread
    lock; backends are assumed read-safe without external coordination.

    The exclusive lock is reentrant for the same thread to prevent
    deadlocks when nested operations occur (e.g. Brain.perceive ->
    _extract_concepts -> semantic.learn).
    """

    _instances: dict[Path, "MemoryBus"] = {}
    _inst_lock = threading.Lock()

    def __new__(cls, repo_root: Path) -> "MemoryBus":
        resolved = repo_root.resolve()
        with cls._inst_lock:
            if resolved not in cls._instances:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instances[resolved] = instance
            return cls._instances[resolved]

    def __init__(self, repo_root: Path) -> None:
        if getattr(self, "_initialized", False):
            return
        self.repo_root = repo_root.resolve()
        self.base_path = self.repo_root / ".ai-team" / "memory"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._thread_lock = threading.RLock()
        self._file_lock = FileLock(str(self.base_path / ".memory.bus.lock"))
        self._file_lock_holder: int | None = None
        self._backends: dict[str, MemoryBackend] = {}
        self._initialized = True

    def _get_backend(self, name: str) -> MemoryBackend:
        if name not in self._backends:
            mapping = {
                "jsonl": JsonlBackend,
                "sqlite": SqliteBackend,
                "vector": VectorBackend,
            }
            cls = mapping[name]
            self._backends[name] = cls(self.base_path / name)
        return self._backends[name]

    @contextmanager
    def exclusive(self) -> Generator[None, None, None]:
        """Acquire write lock (thread + file). Reentrant for same thread."""
        thread_id = threading.current_thread().ident
        already_holds = self._file_lock_holder == thread_id
        self._thread_lock.acquire()
        if not already_holds:
            self._file_lock.acquire()
            self._file_lock_holder = thread_id
        try:
            yield
        finally:
            if not already_holds:
                self._file_lock_holder = None
                self._file_lock.release()
            self._thread_lock.release()

    @contextmanager
    def shared(self) -> Generator[None, None, None]:
        """Acquire read lock (thread only)."""
        self._thread_lock.acquire()
        try:
            yield
        finally:
            self._thread_lock.release()

    def read(self, backend: str, key: str, scope: str = "global", run_id: str | None = None) -> Any:
        with self.shared():
            return self._get_backend(backend).read(key, scope, run_id)

    def write(self, backend: str, key: str, value: dict[str, Any], scope: str = "global", run_id: str | None = None) -> None:
        with self.exclusive():
            self._get_backend(backend).write(key, value, scope, run_id)

    def list_keys(self, backend: str, scope: str = "global", run_id: str | None = None) -> list[str]:
        with self.shared():
            return self._get_backend(backend).list_keys(scope, run_id)

    def search(self, backend: str, query: str, scope: str = "global", run_id: str | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        with self.shared():
            return self._get_backend(backend).search(query, scope, run_id, **kwargs)
