"""Simple in-memory rate limiter for the API server."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict

from fastapi import HTTPException, Request, status


@dataclass
class _RateLimitEntry:
    requests: list[float] = field(default_factory=list)


class RateLimiter:
    """Sliding window rate limiter (in-memory)."""

    def __init__(self, max_requests: int = 60, window_seconds: float = 60.0) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._clients: Dict[str, _RateLimitEntry] = {}

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        entry = self._clients.get(client_id)
        if entry is None:
            entry = _RateLimitEntry()
            self._clients[client_id] = entry

        # Prune old requests outside the window
        cutoff = now - self.window_seconds
        entry.requests = [t for t in entry.requests if t > cutoff]

        if len(entry.requests) >= self.max_requests:
            return False

        entry.requests.append(now)
        return True

    def check(self, request: Request) -> None:
        """FastAPI dependency that raises 429 if rate limit exceeded."""
        # Use X-Forwarded-For if behind proxy, else direct IP
        client_id = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
        if not self.is_allowed(client_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.max_requests} requests per {self.window_seconds}s",
            )
