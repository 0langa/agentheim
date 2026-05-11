"""Federated agent network protocol definitions."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DiscoveryRequest:
    peer_id: str
    nonce: str = ""

    def to_json(self) -> dict[str, Any]:
        return {"type": "DiscoveryRequest", "peer_id": self.peer_id, "nonce": self.nonce}

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "DiscoveryRequest":
        return cls(peer_id=data["peer_id"], nonce=data.get("nonce", ""))


@dataclass
class CapabilityAdvertisement:
    peer_id: str
    capabilities: list[str] = field(default_factory=list)
    public_key_fingerprint: str = ""

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "CapabilityAdvertisement",
            "peer_id": self.peer_id,
            "capabilities": self.capabilities,
            "public_key_fingerprint": self.public_key_fingerprint,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "CapabilityAdvertisement":
        return cls(
            peer_id=data["peer_id"],
            capabilities=data.get("capabilities", []),
            public_key_fingerprint=data.get("public_key_fingerprint", ""),
        )


@dataclass
class TaskDelegation:
    task_id: str
    from_peer: str
    to_peer: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "TaskDelegation",
            "task_id": self.task_id,
            "from_peer": self.from_peer,
            "to_peer": self.to_peer,
            "payload": self.payload,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "TaskDelegation":
        return cls(
            task_id=data["task_id"],
            from_peer=data["from_peer"],
            to_peer=data["to_peer"],
            payload=data.get("payload", {}),
        )


@dataclass
class ResultRelay:
    task_id: str
    from_peer: str
    to_peer: str
    success: bool
    data: Any = None
    error: str | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "ResultRelay",
            "task_id": self.task_id,
            "from_peer": self.from_peer,
            "to_peer": self.to_peer,
            "success": self.success,
            "data": self.data,
            "error": self.error,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "ResultRelay":
        return cls(
            task_id=data["task_id"],
            from_peer=data["from_peer"],
            to_peer=data["to_peer"],
            success=data["success"],
            data=data.get("data"),
            error=data.get("error"),
        )


class FederationProtocol:
    """Federation protocol with whitelist-based trust."""

    def __init__(self, peer_id: str, trusted_peers: list[str] | None = None) -> None:
        self.peer_id = peer_id
        self._trusted = set(trusted_peers or [])

    def is_trusted(self, peer_id: str) -> bool:
        return peer_id in self._trusted

    def trust(self, peer_id: str) -> None:
        self._trusted.add(peer_id)

    def untrust(self, peer_id: str) -> None:
        self._trusted.discard(peer_id)

    @staticmethod
    def fingerprint_public_key(public_key_pem: str) -> str:
        return hashlib.sha256(public_key_pem.encode()).hexdigest()[:16]
