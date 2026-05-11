from __future__ import annotations

import json
from pathlib import Path

import pytest

from marketplace import PluginManager, PluginManifest
from marketplace.sandbox import PluginSandboxError, Sandbox


class TestPluginManifest:
    def test_valid_manifest(self) -> None:
        m = PluginManifest(
            name="test-plugin",
            version="1.0.0",
            entry_point="plugin.py",
            author="test",
        )
        ok, err = m.validate()
        assert ok is True
        assert err == ""

    def test_invalid_name(self) -> None:
        m = PluginManifest(name="", version="1.0.0", entry_point="plugin.py", author="test")
        ok, err = m.validate()
        assert ok is False
        assert "name" in err.lower()

    def test_missing_version(self) -> None:
        m = PluginManifest(name="plugin", version="", entry_point="plugin.py", author="test")
        ok, err = m.validate()
        assert ok is False
        assert "version" in err.lower()

    def test_roundtrip_json(self) -> None:
        m = PluginManifest(
            name="test-plugin",
            version="1.0.0",
            entry_point="plugin.py",
            author="test",
            description="A test plugin",
        )
        data = m.to_json()
        restored = PluginManifest.from_json(data)
        assert restored.name == "test-plugin"
        assert restored.description == "A test plugin"

    def test_from_file(self, tmp_path: Path) -> None:
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(
            json.dumps({
                "name": "file-plugin",
                "version": "1.0.0",
                "entry_point": "plugin.py",
                "author": "test",
            }),
            encoding="utf-8",
        )
        m = PluginManifest.from_file(manifest_path)
        assert m.name == "file-plugin"

    def test_compute_signature(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("hello")
        m = PluginManifest(name="x", version="1", entry_point="a.py", author="y")
        sig = m.compute_signature(tmp_path)
        assert len(sig) == 64  # SHA-256 hex


class TestPluginManager:
    def test_discover_finds_manifests(self, tmp_path: Path) -> None:
        plugin_dir = tmp_path / "plugins" / "my-plugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "manifest.json").write_text(
            json.dumps({
                "name": "my-plugin",
                "version": "1.0.0",
                "entry_point": "plugin.py",
                "author": "test",
            }),
            encoding="utf-8",
        )
        mgr = PluginManager(scan_paths=[tmp_path / "plugins"])
        found = mgr.discover()
        assert len(found) == 1
        assert found[0].name == "my-plugin"

    def test_load_success(self, tmp_path: Path) -> None:
        plugin_dir = tmp_path / "plugins" / "my-plugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "manifest.json").write_text(
            json.dumps({
                "name": "my-plugin",
                "version": "1.0.0",
                "entry_point": "plugin.py",
                "author": "test",
            }),
            encoding="utf-8",
        )
        (plugin_dir / "plugin.py").write_text("x = 42\n", encoding="utf-8")
        mgr = PluginManager(scan_paths=[tmp_path / "plugins"])
        ok, err = mgr.load(plugin_dir)
        assert ok is True
        assert err == ""
        assert "my-plugin" in mgr.list_loaded()

    def test_load_missing_manifest(self, tmp_path: Path) -> None:
        mgr = PluginManager(scan_paths=[])
        ok, err = mgr.load(tmp_path)
        assert ok is False
        assert "manifest" in err.lower()

    def test_load_missing_entry_point(self, tmp_path: Path) -> None:
        plugin_dir = tmp_path / "bad-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "manifest.json").write_text(
            json.dumps({
                "name": "bad-plugin",
                "version": "1.0.0",
                "entry_point": "missing.py",
                "author": "test",
            }),
            encoding="utf-8",
        )
        mgr = PluginManager()
        ok, err = mgr.load(plugin_dir)
        assert ok is False
        assert "entry point" in err.lower()

    def test_unload(self, tmp_path: Path) -> None:
        plugin_dir = tmp_path / "plugins" / "my-plugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "manifest.json").write_text(
            json.dumps({
                "name": "my-plugin",
                "version": "1.0.0",
                "entry_point": "plugin.py",
                "author": "test",
            }),
            encoding="utf-8",
        )
        (plugin_dir / "plugin.py").write_text("x = 42\n", encoding="utf-8")
        mgr = PluginManager(scan_paths=[tmp_path / "plugins"])
        mgr.load(plugin_dir)
        assert "my-plugin" in mgr.list_loaded()
        mgr.unload("my-plugin")
        assert "my-plugin" not in mgr.list_loaded()


class TestSandbox:
    def test_sandbox_context(self) -> None:
        sandbox = Sandbox()
        with sandbox.run() as ctx:
            assert ctx.network_allowed is False

    def test_sandbox_call_success(self) -> None:
        sandbox = Sandbox()
        result = sandbox.call(lambda: 42)
        assert result == 42

    def test_sandbox_call_failure(self) -> None:
        sandbox = Sandbox()
        with pytest.raises(PluginSandboxError):
            sandbox.call(lambda: 1 / 0)
