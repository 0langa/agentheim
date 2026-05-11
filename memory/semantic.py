from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from memory.embeddings import get_engine


@dataclass
class Concept:
    id: str
    label: str
    description: str = ""
    related: list[str] = field(default_factory=list)
    embedding: list[float] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "related": self.related,
            "embedding": self.embedding,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Concept":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class SemanticMemory:
    def __init__(self, base_path: Path, max_concepts: int = 500) -> None:
        self.base_path = base_path.resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.base_path / "concepts.db"
        self.max_concepts = max_concepts
        self.engine = get_engine()
        self._ensure_table()
        self._enable_wal()

    def _ensure_table(self) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS concepts (
                    id TEXT PRIMARY KEY,
                    label TEXT NOT NULL,
                    description TEXT NOT NULL,
                    related_json TEXT NOT NULL,
                    embedding_json TEXT
                )
                """
            )

    def _enable_wal(self) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("PRAGMA journal_mode=WAL")

    def learn(self, concept_id: str, label: str, description: str = "", related: list[str] | None = None) -> Concept:
        text = f"{label} {description}"
        c = Concept(
            id=concept_id,
            label=label,
            description=description,
            related=related or [],
            embedding=self.engine.encode(text).tolist(),
        )
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO concepts (id, label, description, related_json, embedding_json)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    label=excluded.label,
                    description=excluded.description,
                    related_json=excluded.related_json,
                    embedding_json=excluded.embedding_json
                """,
                (
                    c.id,
                    c.label,
                    c.description,
                    json.dumps(c.related),
                    json.dumps(c.embedding) if c.embedding else None,
                ),
            )
        self._enforce_cap()
        return c

    def _enforce_cap(self) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            count = conn.execute("SELECT COUNT(*) FROM concepts").fetchone()[0]
            if count > self.max_concepts:
                to_delete = count - self.max_concepts
                # Evict concepts with fewest relations first
                conn.execute(
                    """
                    DELETE FROM concepts WHERE id IN (
                        SELECT id FROM concepts
                        ORDER BY (LENGTH(related_json) - LENGTH(REPLACE(related_json, ',', ''))) ASC
                        LIMIT ?
                    )
                    """,
                    (to_delete,),
                )

    def relate(self, concept_id: str, other_id: str) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            row = conn.execute(
                "SELECT related_json FROM concepts WHERE id = ?", (concept_id,)
            ).fetchone()
            if row is None:
                return
            related = json.loads(row[0]) if row[0] else []
            if other_id not in related:
                related.append(other_id)
                conn.execute(
                    "UPDATE concepts SET related_json = ? WHERE id = ?",
                    (json.dumps(related), concept_id),
                )

    def query(self, query: str, top_k: int = 5) -> list[Concept]:
        qvec = self.engine.encode(query)
        np = __import__("numpy")
        scored: list[tuple[float, Concept]] = []
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute("SELECT * FROM concepts").fetchall()
        for row in rows:
            c = self._row_to_concept(row)
            if c.embedding:
                vec = np.array(c.embedding, dtype=np.float32)
                sim = self.engine.similarity(qvec, vec)
                scored.append((sim, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:top_k]]

    def get(self, concept_id: str) -> Concept | None:
        with sqlite3.connect(str(self.db_path)) as conn:
            row = conn.execute("SELECT * FROM concepts WHERE id = ?", (concept_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_concept(row)

    def list_all(self) -> list[Concept]:
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute("SELECT * FROM concepts").fetchall()
        return [self._row_to_concept(row) for row in rows]

    def count(self) -> int:
        with sqlite3.connect(str(self.db_path)) as conn:
            return conn.execute("SELECT COUNT(*) FROM concepts").fetchone()[0]

    def _row_to_concept(self, row: tuple[Any, ...]) -> Concept:
        return Concept(
            id=row[0],
            label=row[1],
            description=row[2],
            related=json.loads(row[3]) if row[3] else [],
            embedding=json.loads(row[4]) if row[4] else None,
        )
