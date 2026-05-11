"""API key authentication for the API server."""

from __future__ import annotations

import os
import secrets
from typing import Annotated

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# In-memory allowlist; in production this would be backed by a database
_API_KEYS: set[str] = set()
_initialized = False


def _dev_mode_enabled() -> bool:
    return os.environ.get("AI_TEAM_DEV_MODE", "").strip().lower() in {"1", "true", "yes", "on"}


def _load_keys() -> None:
    global _initialized
    if _initialized:
        return
    env_keys = os.environ.get("AI_TEAM_API_KEYS", "")
    for key in env_keys.split(","):
        key = key.strip()
        if key:
            _API_KEYS.add(key)
    _initialized = True


def verify_api_key(api_key: Annotated[str | None, Security(api_key_header)]) -> str:
    """Verify the API key from the X-API-Key header."""
    _load_keys()
    if not _API_KEYS and not _dev_mode_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication is not configured. Set AI_TEAM_API_KEYS.",
        )
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key header: X-API-Key",
        )
    if not _API_KEYS and _dev_mode_enabled():
        return api_key
    if api_key not in _API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return api_key


def generate_api_key() -> str:
    """Generate a new random API key."""
    return secrets.token_urlsafe(32)
