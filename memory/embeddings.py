from __future__ import annotations

import hashlib
import math
import re
from typing import Any

import numpy as np


class EmbeddingEngine:
    def __init__(self, dim: int = 256) -> None:
        self.dim = dim
        self._rng = np.random.RandomState(42)
        self._projections: dict[int, np.ndarray] = {}

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())

    def _get_projection(self, token: str) -> np.ndarray:
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        if h not in self._projections:
            self._projections[h] = self._rng.randn(self.dim)
        return self._projections[h]

    def encode(self, text: str) -> np.ndarray:
        tokens = self._tokenize(text)
        if not tokens:
            return np.zeros(self.dim, dtype=np.float32)
        vec = np.zeros(self.dim, dtype=np.float32)
        for token in tokens:
            vec += self._get_projection(token)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        dot = float(np.dot(a, b))
        return max(0.0, min(1.0, dot))


_default_engine: EmbeddingEngine | None = None


def get_engine(dim: int = 256) -> EmbeddingEngine:
    global _default_engine
    if _default_engine is None:
        _default_engine = EmbeddingEngine(dim=dim)
    return _default_engine
