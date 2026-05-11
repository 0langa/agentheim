"""Plugin manifest schema and validation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PluginManifest:
    name: str
    version: str
    entry_point: str
    author: str
    description: str = ""
    dependencies: list[str] = field(default_factory=list)
    required_tools: list[str] = field(default_factory=list)
    required_providers: list[str] = field(default_factory=list)
    signature: str = ""

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "entry_point": self.entry_point,
            "author": self.author,
            "description": self.description,
            "dependencies": self.dependencies,
            "required_tools": self.required_tools,
            "required_providers": self.required_providers,
            "signature": self.signature,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "PluginManifest":
        return cls(
            name=data["name"],
            version=data["version"],
            entry_point=data["entry_point"],
            author=data["author"],
            description=data.get("description", ""),
            dependencies=data.get("dependencies", []),
            required_tools=data.get("required_tools", []),
            required_providers=data.get("required_providers", []),
            signature=data.get("signature", ""),
        )

    @classmethod
    def from_file(cls, path: Path) -> "PluginManifest":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_json(data)

    def validate(self) -> tuple[bool, str]:
        if not self.name or not self.name.replace("-", "").replace("_", "").isalnum():
            return False, "Invalid plugin name"
        if not self.version:
            return False, "Version is required"
        if not self.entry_point:
            return False, "Entry point is required"
        if not self.author:
            return False, "Author is required"
        return True, ""

    def compute_signature(self, package_path: Path) -> str:
        """Compute SHA-256 signature of package directory."""
        sha = hashlib.sha256()
        for file in sorted(package_path.rglob("*")):
            if file.is_file():
                sha.update(file.read_bytes())
        return sha.hexdigest()
