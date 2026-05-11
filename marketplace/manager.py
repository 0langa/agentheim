"""Plugin manager for discovery, loading, and registration."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from marketplace.manifest import PluginManifest
from marketplace.sandbox import Sandbox


class PluginManager:
    """Discover, validate, and load plugins."""

    DEFAULT_SCAN_PATHS = [
        Path.home() / ".agentheim" / "plugins",
        Path(".").resolve() / "plugins",
    ]

    def __init__(self, scan_paths: list[Path] | None = None) -> None:
        self.scan_paths = scan_paths or [p for p in self.DEFAULT_SCAN_PATHS]
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
        """Load a plugin from its directory with sandboxing and signature verification."""
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

        # Signature verification
        if manifest.signature:
            computed = manifest.compute_signature(plugin_dir)
            if computed != manifest.signature:
                return False, "Signature verification failed"

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
