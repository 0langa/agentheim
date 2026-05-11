from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from memory.backends.base import MemoryBackend


class SqliteBackend(MemoryBackend):
    def __init__(self, base_path: Path) -> None:
        super().__init__(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.db_path = base_path / "memory.db"
        self._ensure_table()

    def _ensure_table(self) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_entries (
                    scope TEXT NOT NULL,
                    run_id TEXT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (scope, run_id, key)
                )
                """
            )

    def read(self, key: str, scope: str = "global", run_id: str | None = None) -> dict[str, Any] | None:
        safe = self._sanitize_key(key)
        with sqlite3.connect(str(self.db_path)) as conn:
            row = conn.execute(
                "SELECT value FROM memory_entries WHERE scope = ? AND run_id = ? AND key = ?",
                (scope, run_id or "", safe),
            ).fetchone()
        if row is None:
            return None
        return json.loads(row[0])

    def write(self, key: str, value: dict[str, Any], scope: str = "global", run_id: str | None = None) -> None:
        safe = self._sanitize_key(key)
        payload = json.dumps(value, ensure_ascii=False)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO memory_entries (scope, run_id, key, value)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(scope, run_id, key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
                """,
                (scope, run_id or "", safe, payload),
            )

    def list_keys(self, scope: str = "global", run_id: str | None = None) -> list[str]:
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute(
                "SELECT key FROM memory_entries WHERE scope = ? AND run_id = ?",
                (scope, run_id or ""),
            ).fetchall()
        return [r[0] for r in rows]

    def search(self, query: str, scope: str = "global", run_id: str | None = None) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        q = f"%{query}%"
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute(
                "SELECT key, value FROM memory_entries WHERE scope = ? AND run_id = ? AND (key LIKE ? OR value LIKE ?)",
                (scope, run_id or "", q, q),
            ).fetchall()
        for key, val_json in rows:
            results.append({"key": key, "value": json.loads(val_json)})
        return results
