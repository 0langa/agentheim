"""API server for agent orchestration.

FastAPI-based production API with OpenAPI spec, authentication, and rate limiting.
"""

from __future__ import annotations

from interfaces.api_server.app import create_api_app

__all__ = ["create_api_app"]
