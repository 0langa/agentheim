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
        self._vectors: dict[tuple[str, str], dict[str, np.ndarray]] = {}
        self._metas: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
        self._load()

    @staticmethod
    def _bucket(scope: str, run_id: str | None) -> tuple[str, str]:
        return (scope, run_id or "")

    def _index_path(self, scope: str, run_id: str | None) -> Path:
        return self._scope_dir(scope, run_id) / "vector_index.json"

    def _load(self) -> None:
        for path in self.base_path.rglob("vector_index.json"):
            try:
                rel = path.relative_to(self.base_path)
            except ValueError:
                continue
            parts = rel.parts
            if len(parts) == 2 and parts[0] in ("global", "repository") and parts[1] == "vector_index.json":
                scope = parts[0]
                run_id = ""
            elif len(parts) == 3 and parts[0] == "run" and parts[2] == "vector_index.json":
                scope = "run"
                run_id = parts[1]
            else:
                continue

            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            bucket = self._bucket(scope, run_id)
            self._vectors.setdefault(bucket, {})
            self._metas.setdefault(bucket, {})
            for entry in data.get("entries", []):
                key = entry["key"]
                self._vectors[bucket][key] = np.array(entry["vector"], dtype=np.float32)
                self._metas[bucket][key] = entry.get("meta", {})

    def _save(self, scope: str, run_id: str | None) -> None:
        path = self._index_path(scope, run_id)
        bucket = self._bucket(scope, run_id)
        entries = []
        for key, vec in self._vectors.get(bucket, {}).items():
            entries.append({
                "key": key,
                "vector": vec.tolist(),
                "meta": self._metas.get(bucket, {}).get(key, {}),
            })
        with path.open("w", encoding="utf-8") as f:
            json.dump({"entries": entries}, f)

    def write(self, key: str, value: dict[str, Any], scope: str = "global", run_id: str | None = None) -> None:
        safe = self._sanitize_key(key)
        text = json.dumps(value, ensure_ascii=False)
        bucket = self._bucket(scope, run_id)
        self._vectors.setdefault(bucket, {})
        self._metas.setdefault(bucket, {})
        self._vectors[bucket][safe] = self.engine.encode(text)
        self._metas[bucket][safe] = value
        self._save(scope, run_id)

    def read(self, key: str, scope: str = "global", run_id: str | None = None) -> dict[str, Any] | None:
        safe = self._sanitize_key(key)
        bucket = self._bucket(scope, run_id)
        return self._metas.get(bucket, {}).get(safe)

    def list_keys(self, scope: str = "global", run_id: str | None = None) -> list[str]:
        bucket = self._bucket(scope, run_id)
        return list(self._metas.get(bucket, {}).keys())

    def search(self, query: str, scope: str = "global", run_id: str | None = None, top_k: int = 5) -> list[dict[str, Any]]:
        qvec = self.engine.encode(query)
        bucket = self._bucket(scope, run_id)
        vectors = self._vectors.get(bucket, {})
        metas = self._metas.get(bucket, {})
        scored: list[tuple[float, str]] = []
        for key, vec in vectors.items():
            sim = self.engine.similarity(qvec, vec)
            scored.append((sim, key))
        scored.sort(reverse=True)
        results: list[dict[str, Any]] = []
        for sim, key in scored[:top_k]:
            meta = metas.get(key, {})
            results.append({"key": key, "value": meta, "score": round(sim, 4)})
        return results
