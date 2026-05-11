from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import platformdirs

from core.redaction import redact_dict


class GlobalMemory:
    """Cross-project persistent memory (Tier 3).

    Stores user preferences, coding style, model performance profiles,
    and approval history. Never contains repository-specific data.
    """

    def __init__(self, base_path: Path | None = None) -> None:
        if base_path is None:
            base_path = Path(
                platformdirs.user_data_path("agent-arena", appauthor="agentheim")
            )
        self.base_path = base_path.resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.base_path / "global_memory.db"
        self._ensure_table()
        self._enable_wal()

    def _ensure_table(self) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value_json TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS approval_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    decision TEXT NOT NULL,
                    tool_name TEXT,
                    context_json TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS model_profiles (
                    model_id TEXT PRIMARY KEY,
                    task_type TEXT,
                    success_count INTEGER DEFAULT 0,
                    fail_count INTEGER DEFAULT 0,
                    avg_latency_ms REAL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def _enable_wal(self) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("PRAGMA journal_mode=WAL")

    def get_preference(self, key: str, default: Any = None) -> Any:
        with sqlite3.connect(str(self.db_path)) as conn:
            row = conn.execute(
                "SELECT value_json FROM preferences WHERE key = ?", (key,)
            ).fetchone()
        if row is None:
            return default
        return json.loads(row[0])

    def set_preference(self, key: str, value: Any) -> None:
        safe = redact_dict({"v": value})
        payload = json.dumps(safe["v"], ensure_ascii=False)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO preferences (key, value_json)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json, updated_at=CURRENT_TIMESTAMP
                """,
                (key, payload),
            )

    def record_approval(self, decision: str, tool_name: str | None = None, context: dict[str, Any] | None = None) -> None:
        safe_context = redact_dict(context or {})
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "INSERT INTO approval_history (decision, tool_name, context_json) VALUES (?, ?, ?)",
                (decision, tool_name or "", json.dumps(safe_context, ensure_ascii=False)),
            )

    def get_approval_history(self, limit: int = 50) -> list[dict[str, Any]]:
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute(
                "SELECT decision, tool_name, context_json, timestamp FROM approval_history ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "decision": r[0],
                "tool_name": r[1],
                "context": json.loads(r[2]) if r[2] else {},
                "timestamp": r[3],
            }
            for r in rows
        ]

    def record_model_result(self, model_id: str, task_type: str, success: bool, latency_ms: float) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            existing = conn.execute(
                "SELECT success_count, fail_count, avg_latency_ms FROM model_profiles WHERE model_id = ?",
                (model_id,),
            ).fetchone()
            if existing:
                s, f, avg = existing
                s = s + (1 if success else 0)
                f = f + (0 if success else 1)
                total = s + f
                new_avg = ((avg * (total - 1)) + latency_ms) / total if total > 0 else latency_ms
                conn.execute(
                    "UPDATE model_profiles SET success_count=?, fail_count=?, avg_latency_ms=?, updated_at=CURRENT_TIMESTAMP WHERE model_id=?",
                    (s, f, new_avg, model_id),
                )
            else:
                conn.execute(
                    "INSERT INTO model_profiles (model_id, task_type, success_count, fail_count, avg_latency_ms) VALUES (?, ?, ?, ?, ?)",
                    (model_id, task_type, 1 if success else 0, 0 if success else 1, latency_ms),
                )

    def get_model_profile(self, model_id: str) -> dict[str, Any] | None:
        with sqlite3.connect(str(self.db_path)) as conn:
            row = conn.execute(
                "SELECT task_type, success_count, fail_count, avg_latency_ms FROM model_profiles WHERE model_id = ?",
                (model_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "model_id": model_id,
            "task_type": row[0],
            "success_count": row[1],
            "fail_count": row[2],
            "avg_latency_ms": row[3],
        }
