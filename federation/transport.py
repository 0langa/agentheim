"""HTTP transport for federated agent networks.

Provides a FastAPI server and HTTP client for peer discovery, capability
advertisement, task delegation, and result relay.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from federation.protocol import (
    CapabilityAdvertisement,
    DiscoveryRequest,
    ResultRelay,
    TaskDelegation,
)

logger = logging.getLogger(__name__)


class PeerInfo(BaseModel):
    peer_id: str
    endpoint: str
    capabilities: list[str] = Field(default_factory=list)
    public_key_fingerprint: str = ""


class DiscoverRequest(BaseModel):
    peer_id: str
    capabilities: list[str] = Field(default_factory=list)


class DelegateRequest(BaseModel):
    task_id: str
    task_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    origin_peer: str


class RelayRequest(BaseModel):
    task_id: str
    success: bool
    data: Any = None
    error: str | None = None
    origin_peer: str


def create_federation_app(local_peer_id: str, local_capabilities: list[str] | None = None) -> FastAPI:
    app = FastAPI(
        title="Agentheim Federation",
        description="Peer-to-peer federation for distributed agents",
        version="0.1.0",
    )
    _peers: dict[str, PeerInfo] = {}
    _local_peer_id = local_peer_id
    _local_capabilities = local_capabilities or []

    @app.post("/api/federation/discover")
    def discover(req: DiscoverRequest) -> dict[str, Any]:
        """Handle a discovery request from a peer."""
        # Simple trust model: accept any peer (production would verify signatures)
        _peers[req.peer_id] = PeerInfo(
            peer_id=req.peer_id,
            endpoint="",  # Would be extracted from request
            capabilities=req.capabilities,
        )
        return {
            "peer_id": _local_peer_id,
            "capabilities": _local_capabilities,
            "known_peers": list(_peers.keys()),
        }

    @app.get("/api/federation/peers")
    def list_peers() -> list[PeerInfo]:
        """List known peers."""
        return list(_peers.values())

    @app.post("/api/federation/delegate")
    def delegate_task(req: DelegateRequest) -> dict[str, str]:
        """Receive a delegated task from a peer."""
        logger.info("Received delegated task %s from %s", req.task_id, req.origin_peer)
        # In production, this would enqueue the task for local execution
        return {"status": "accepted", "task_id": req.task_id}

    @app.post("/api/federation/relay")
    def relay_result(req: RelayRequest) -> dict[str, str]:
        """Receive a relayed result from a peer."""
        logger.info("Received relayed result for task %s from %s", req.task_id, req.origin_peer)
        return {"status": "received", "task_id": req.task_id}

    return app


class FederationClient:
    """HTTP client for communicating with federation peers."""

    def __init__(self, peer_endpoint: str, timeout: float = 30.0) -> None:
        self.peer_endpoint = peer_endpoint.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        import requests

        url = f"{self.peer_endpoint}{path}"
        try:
            resp = requests.request(method, url, json=json, timeout=self.timeout, allow_redirects=False)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.warning("Federation request failed: %s", exc)
            raise

    def discover(self, local_peer_id: str, capabilities: list[str]) -> dict[str, Any]:
        return self._request(
            "POST",
            "/api/federation/discover",
            {"peer_id": local_peer_id, "capabilities": capabilities},
        )

    def delegate(self, task: TaskDelegation) -> dict[str, str]:
        return self._request(
            "POST",
            "/api/federation/delegate",
            {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "payload": task.payload,
                "origin_peer": task.origin_peer,
            },
        )

    def relay(self, result: ResultRelay) -> dict[str, str]:
        return self._request(
            "POST",
            "/api/federation/relay",
            {
                "task_id": result.task_id,
                "success": result.success,
                "data": result.data,
                "error": result.error,
                "origin_peer": result.origin_peer,
            },
        )
