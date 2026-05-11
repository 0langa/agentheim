from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from memory.backends.base import MemoryBackend
from memory.embeddings import get_engine


class VectorBackend(MemoryBackend):
    def __init__(self, base_path: Path, dim: int = 256) -> None:
        super().__init__(base_path)
        self.engine = get_engine(dim=dim)
        self._vectors: dict[str, np.ndarray] = {}
        self._metas: dict[str, dict[str, Any]] = {}
        self._load()

    def _index_path(self, scope: str, run_id: str | None) -> Path:
        return self._scope_dir(scope, run_id) / "vector_index.json"

    def _load(self) -> None:
        for path in self.base_path.rglob("vector_index.json"):
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            for entry in data.get("entries", []):
                key = entry["key"]
                self._vectors[key] = np.array(entry["vector"], dtype=np.float32)
                self._metas[key] = entry.get("meta", {})

    def _save(self, scope: str, run_id: str | None) -> None:
        path = self._index_path(scope, run_id)
        entries = []
        for key, vec in self._vectors.items():
            entries.append({
                "key": key,
                "vector": vec.tolist(),
                "meta": self._metas.get(key, {}),
            })
        with path.open("w", encoding="utf-8") as f:
            json.dump({"entries": entries}, f)

    def write(self, key: str, value: dict[str, Any], scope: str = "global", run_id: str | None = None) -> None:
        safe = self._sanitize_key(key)
        text = json.dumps(value, ensure_ascii=False)
        self._vectors[safe] = self.engine.encode(text)
        self._metas[safe] = value
        self._save(scope, run_id)

    def read(self, key: str, scope: str = "global", run_id: str | None = None) -> dict[str, Any] | None:
        safe = self._sanitize_key(key)
        return self._metas.get(safe)

    def list_keys(self, scope: str = "global", run_id: str | None = None) -> list[str]:
        return list(self._metas.keys())

    def search(self, query: str, scope: str = "global", run_id: str | None = None, top_k: int = 5) -> list[dict[str, Any]]:
        qvec = self.engine.encode(query)
        scored: list[tuple[float, str]] = []
        for key, vec in self._vectors.items():
            sim = self.engine.similarity(qvec, vec)
            scored.append((sim, key))
        scored.sort(reverse=True)
        results: list[dict[str, Any]] = []
        for sim, key in scored[:top_k]:
            meta = self._metas.get(key, {})
            results.append({"key": key, "value": meta, "score": round(sim, 4)})
        return results
