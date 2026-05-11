from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from memory.embeddings import get_engine


@dataclass
class Episode:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    context: str = ""
    action: str = ""
    outcome: str = ""
    emotion: str = "neutral"
    tags: list[str] = field(default_factory=list)
    embedding: list[float] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "context": self.context,
            "action": self.action,
            "outcome": self.outcome,
            "emotion": self.emotion,
            "tags": self.tags,
            "embedding": self.embedding,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Episode":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class EpisodicMemory:
    def __init__(self, base_path: Path, max_episodes: int = 1000) -> None:
        self.base_path = base_path.resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.base_path / "episodes.db"
        self.max_episodes = max_episodes
        self.engine = get_engine()
        self._ensure_table()
        self._enable_wal()

    def _ensure_table(self) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS episodes (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    context TEXT NOT NULL,
                    action TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    emotion TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    embedding_json TEXT,
                    importance INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_episodes_timestamp ON episodes(timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_episodes_importance ON episodes(importance)"
            )

    def _enable_wal(self) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("PRAGMA journal_mode=WAL")

    def record(self, context: str, action: str, outcome: str = "", emotion: str = "neutral", tags: list[str] | None = None) -> Episode:
        text = f"{context} {action} {outcome}"
        importance = self._compute_importance(emotion, outcome)
        ep = Episode(
            context=context,
            action=action,
            outcome=outcome,
            emotion=emotion,
            tags=tags or [],
            embedding=self.engine.encode(text).tolist(),
        )
        self._insert(ep, importance)
        self._enforce_cap()
        return ep

    def _compute_importance(self, emotion: str, outcome: str) -> int:
        score = 0
        if emotion != "neutral":
            score += 1
        lowered = outcome.lower()
        if "error" in lowered or "fail" in lowered or "broke" in lowered:
            score += 1
        return score

    def _insert(self, ep: Episode, importance: int = 0) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO episodes (id, timestamp, context, action, outcome, emotion, tags_json, embedding_json, importance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ep.id,
                    ep.timestamp,
                    ep.context,
                    ep.action,
                    ep.outcome,
                    ep.emotion,
                    json.dumps(ep.tags),
                    json.dumps(ep.embedding) if ep.embedding else None,
                    importance,
                ),
            )

    def _enforce_cap(self) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            count = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
            if count > self.max_episodes:
                to_delete = count - self.max_episodes
                conn.execute(
                    """
                    DELETE FROM episodes WHERE id IN (
                        SELECT id FROM episodes ORDER BY importance ASC, timestamp ASC LIMIT ?
                    )
                    """,
                    (to_delete,),
                )

    def _row_to_episode(self, row: tuple[Any, ...]) -> Episode:
        return Episode(
            id=row[0],
            timestamp=row[1],
            context=row[2],
            action=row[3],
            outcome=row[4],
            emotion=row[5],
            tags=json.loads(row[6]) if row[6] else [],
            embedding=json.loads(row[7]) if row[7] else None,
        )

    def recall(self, query: str, top_k: int = 5) -> list[Episode]:
        qvec = self.engine.encode(query)
        np = __import__("numpy")
        scored: list[tuple[float, Episode]] = []
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute("SELECT * FROM episodes").fetchall()
        for row in rows:
            ep = self._row_to_episode(row)
            if ep.embedding:
                vec = np.array(ep.embedding, dtype=np.float32)
                sim = self.engine.similarity(qvec, vec)
                scored.append((sim, ep))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [ep for _, ep in scored[:top_k]]

    def recent(self, n: int = 5) -> list[Episode]:
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute(
                "SELECT * FROM episodes ORDER BY timestamp DESC LIMIT ?",
                (n,),
            ).fetchall()
        return [self._row_to_episode(row) for row in rows]

    def count(self) -> int:
        with sqlite3.connect(str(self.db_path)) as conn:
            return conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
