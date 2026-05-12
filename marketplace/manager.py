"""Plugin manager for discovery, loading, and registration."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from marketplace.manifest import PluginManifest
from marketplace.sandbox import Sandbox
from marketplace.signing import PluginSigner, PluginSigningError


class PluginManager:
    """Discover, validate, and load plugins.

    Plugins are verified using Ed25519 cryptographic signatures before
    loading.  A trusted public key directory maps key IDs to PEM-encoded
    Ed25519 public keys.  If verification fails, the plugin is rejected.
    """

    DEFAULT_SCAN_PATHS = [
        Path.home() / ".agentheim" / "plugins",
        Path(".").resolve() / "plugins",
    ]

    # Default directories to look up trusted public keys.
    # Can be overridden via ``trusted_key_dirs``.
    DEFAULT_TRUSTED_KEY_DIRS = [
        Path.home() / ".agentheim" / "trusted-keys",
        Path(".").resolve() / ".agentheim" / "trusted-keys",
    ]

    def __init__(
        self,
        scan_paths: list[Path] | None = None,
        trusted_key_dirs: list[Path] | None = None,
    ) -> None:
        self.scan_paths = scan_paths or [p for p in self.DEFAULT_SCAN_PATHS]
        self.trusted_key_dirs = trusted_key_dirs or [
            p for p in self.DEFAULT_TRUSTED_KEY_DIRS
        ]
        self._loaded: dict[str, Any] = {}
        self._sandbox = Sandbox()

    def discover(self) -> list[Path]:
        """Find plugin directories containing manifest.json."""
        found: list[Path] = []
        for scan_path in self.scan_paths:
            if not scan_path.exists():
                continue
            for item in scan_path.iterdir():
                if item.is_dir() and (item / "manifest.json").exists():
                    found.append(item)
        return found

    def load(self, plugin_dir: Path) -> tuple[bool, str]:
        """Load a plugin from its directory with sandboxing and Ed25519 signature verification.

        Verification flow:
        1. Parse the manifest
        2. Validate schema fields
        3. Locate the trusted public key using ``trusted_key_id`` from the manifest
        4. Verify the Ed25519 signature over all package files
        5. Load the entry point module
        6. Execute activation hooks through the sandbox
        """
        manifest_path = plugin_dir / "manifest.json"
        if not manifest_path.exists():
            return False, "manifest.json not found"

        try:
            manifest = PluginManifest.from_file(manifest_path)
        except Exception as exc:
            return False, f"Failed to parse manifest: {exc}"

        valid, err = manifest.validate()
        if not valid:
            return False, err

        # Ed25519 cryptographic signature verification
        if manifest.signature:
            if not manifest.trusted_key_id:
                return False, "Plugin has a signature but no trusted_key_id; cannot verify"
            try:
                public_key_path = self._resolve_public_key(manifest.trusted_key_id)
                PluginSigner.verify_package(plugin_dir, public_key_path)
            except PluginSigningError as exc:
                return False, f"Ed25519 signature verification failed: {exc}"
        else:
            # In production mode, reject unsigned plugins
            return False, (
                "Plugin is not signed.  All plugins must have an Ed25519 signature "
                "and a trusted_key_id.  Run the PluginSigner to sign this package."
            )

        entry_file = plugin_dir / manifest.entry_point
        if not entry_file.exists():
            return False, f"Entry point not found: {manifest.entry_point}"

        try:
            spec = importlib.util.spec_from_file_location(
                f"plugin_{manifest.name}", str(entry_file)
            )
            if spec is None or spec.loader is None:
                return False, "Failed to create module spec"
            module = importlib.util.module_from_spec(spec)
            sys.modules[module.__name__] = module
            spec.loader.exec_module(module)

            # Sandbox activation: if the module exposes an activate() or register()
            # function, invoke it through the sandbox with restricted context.
            for hook_name in ("activate", "register"):
                hook = getattr(module, hook_name, None)
                if callable(hook):
                    try:
                        self._sandbox.call(hook)
                    except Exception as exc:
                        return False, f"Plugin {hook_name}() failed sandbox execution: {exc}"
                    break

            self._loaded[manifest.name] = module
            return True, ""
        except Exception as exc:
            return False, f"Failed to load plugin module: {exc}"

    def unload(self, name: str) -> None:
        """Unload a plugin by name."""
        if name in self._loaded:
            del self._loaded[name]

    def list_loaded(self) -> list[str]:
        return list(self._loaded.keys())

    def get(self, name: str) -> Any:
        return self._loaded.get(name)

    def _resolve_public_key(self, key_id: str) -> Path:
        """Resolve *key_id* to a public key PEM file path.

        Searches ``trusted_key_dirs`` for a file named ``key_id.pub``.
        """
        for key_dir in self.trusted_key_dirs:
            candidate = key_dir / f"{key_id}.pub"
            if candidate.exists():
                return candidate
        raise PluginSigningError(
            f"No trusted public key found for key_id='{key_id}'. "
            f"Searched directories: {[str(d) for d in self.trusted_key_dirs]}"
        )
