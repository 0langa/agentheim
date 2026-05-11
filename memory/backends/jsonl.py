from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from memory.backends.base import MemoryBackend


class JsonlBackend(MemoryBackend):
    def read(self, key: str, scope: str = "global", run_id: str | None = None) -> dict[str, Any] | None:
        safe = self._sanitize_key(key)
        path = self._scope_dir(scope, run_id) / f"{safe}.jsonl"
        if not path.exists():
            return None

        latest: dict[str, Any] | None = None
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("key") == safe:
                    latest = record.get("value")
        return latest

    def write(self, key: str, value: dict[str, Any], scope: str = "global", run_id: str | None = None) -> None:
        safe = self._sanitize_key(key)
        scope_dir = self._scope_dir(scope, run_id)
        path = scope_dir / f"{safe}.jsonl"
        tmp_path = scope_dir / f".{safe}.jsonl.tmp"
        with tmp_path.open("w", encoding="utf-8") as f:
            if path.exists():
                existing = path.read_text(encoding="utf-8")
                f.write(existing)
            f.write(json.dumps({"key": safe, "value": value}, ensure_ascii=False) + "\n")
        tmp_path.replace(path)

    def list_keys(self, scope: str = "global", run_id: str | None = None) -> list[str]:
        scope_dir = self._scope_dir(scope, run_id)
        return [p.stem for p in scope_dir.glob("*.jsonl")]

    def search(self, query: str, scope: str = "global", run_id: str | None = None) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        q = query.lower()
        for key in self.list_keys(scope, run_id):
            val = self.read(key, scope, run_id)
            if val is None:
                continue
            text = json.dumps(val, ensure_ascii=False).lower()
            if q in text or q in key.lower():
                results.append({"key": key, "value": val})
        return results
