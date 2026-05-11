from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.errors import ToolSafetyError
from core.tool_protocol import RiskLevel, ToolContext, ToolResult
from tools.browser import BrowserTool


class TestBrowserToolSchema:
    def test_tool_id(self) -> None:
        tool = BrowserTool()
        assert tool.tool_id == "browser"

    def test_risk_level(self) -> None:
        tool = BrowserTool()
        assert tool.risk_level == RiskLevel.HIGH

    def test_schema_has_required_params(self) -> None:
        tool = BrowserTool()
        assert "operation" in tool.schema.parameters
        assert tool.schema.parameters["operation"].required is True
        assert "url" in tool.schema.parameters
        assert "selector" in tool.schema.parameters


class TestBrowserToolPolicy:
    def test_network_blocked(self) -> None:
        tool = BrowserTool()
        ctx = ToolContext(network_allowed=False)
        result = tool.invoke({"operation": "navigate", "url": "https://example.com"}, ctx)
        assert result.success is False
        assert "not allowed by policy" in result.error

    def test_missing_url_for_navigate(self) -> None:
        tool = BrowserTool()
        ctx = ToolContext(network_allowed=True)
        result = tool.invoke({"operation": "navigate"}, ctx)
        assert result.success is False
        assert "'url' is required" in result.error

    def test_missing_operation(self) -> None:
        tool = BrowserTool()
        ctx = ToolContext(network_allowed=True)
        result = tool.invoke({"url": "https://example.com"}, ctx)
        assert result.success is False
        assert "Missing required parameter" in result.error


class TestBrowserToolFallbackChain:
    def test_playwright_available_flag(self) -> None:
        # Playwright should be available in this test environment
        assert BrowserTool._playwright_available() is True

    def test_screenshot_requires_playwright(self) -> None:
        tool = BrowserTool()
        ctx = ToolContext(network_allowed=True)
        with patch.object(BrowserTool, "_playwright_available", return_value=False):
            result = tool.invoke({"operation": "screenshot", "url": "https://example.com"}, ctx)
        assert result.success is False
        assert "Screenshot requires Playwright" in result.error

    def test_click_requires_playwright(self) -> None:
        tool = BrowserTool()
        ctx = ToolContext(network_allowed=True)
        with patch.object(BrowserTool, "_playwright_available", return_value=False):
            result = tool.invoke({"operation": "click", "url": "https://example.com", "selector": "#btn"}, ctx)
        assert result.success is False
        assert "Click requires Playwright" in result.error

    def test_fill_requires_playwright(self) -> None:
        tool = BrowserTool()
        ctx = ToolContext(network_allowed=True)
        with patch.object(BrowserTool, "_playwright_available", return_value=False):
            result = tool.invoke({"operation": "fill", "url": "https://example.com", "selector": "#input", "value": "x"}, ctx)
        assert result.success is False
        assert "Fill requires Playwright" in result.error

    def test_evaluate_requires_playwright(self) -> None:
        tool = BrowserTool()
        ctx = ToolContext(network_allowed=True)
        with patch.object(BrowserTool, "_playwright_available", return_value=False):
            result = tool.invoke({"operation": "evaluate", "url": "https://example.com", "script": "1+1"}, ctx)
        assert result.success is False
        assert "Evaluate requires Playwright" in result.error


class TestBrowserToolHttpFallback:
    """Test HTTP fallback methods directly."""

    def test_navigate_http_fallback(self) -> None:
        tool = BrowserTool()
        html = "<html><head><title>Test Page</title></head><body>Hello</body></html>"
        with patch.object(tool, "_fetch", return_value=(200, html)):
            result = tool._navigate_http_fallback("https://example.com", 10)
        assert result.success is True
        assert result.data["title"] == "Test Page"
        assert result.data["status"] == 200
        assert result.metadata["backend"] == "http_fallback"

    def test_navigate_http_fallback_fetch_failure(self) -> None:
        tool = BrowserTool()
        with patch.object(tool, "_fetch", return_value=(None, "Connection timeout")):
            result = tool._navigate_http_fallback("https://example.com", 10)
        assert result.success is False
        assert "Failed to fetch URL" in result.error

    def test_get_text_http_fallback(self) -> None:
        tool = BrowserTool()
        html = "<html><body><p>Hello world</p></body></html>"
        with patch.object(tool, "_fetch", return_value=(200, html)):
            result = tool._get_text_http_fallback("https://example.com", None, 10)
        assert result.success is True
        assert "Hello world" in result.data
        assert result.metadata["backend"] == "http_fallback"

    def test_get_text_http_fallback_with_selector(self) -> None:
        tool = BrowserTool()
        html = "<html><body><div id='main'>Target text</div><div>Other</div></body></html>"
        with patch.object(tool, "_fetch", return_value=(200, html)):
            result = tool._get_text_http_fallback("https://example.com", "#main", 10)
        assert result.success is True
        assert result.data == "Target text"

    def test_get_text_http_fallback_selector_not_found(self) -> None:
        tool = BrowserTool()
        html = "<html><body><p>Hello</p></body></html>"
        with patch.object(tool, "_fetch", return_value=(200, html)):
            result = tool._get_text_http_fallback("https://example.com", "#missing", 10)
        assert result.success is False
        assert "Selector not found" in result.error

    def test_get_links_http_fallback(self) -> None:
        tool = BrowserTool()
        html = '<html><body><a href="/a">Link A</a><a href="/b">Link B</a></body></html>'
        with patch.object(tool, "_fetch", return_value=(200, html)):
            result = tool._get_links_http_fallback("https://example.com", 10)
        assert result.success is True
        assert len(result.data) == 2
        assert result.data[0]["text"] == "Link A"
        assert result.data[0]["href"] == "/a"


class TestBrowserToolPlaywrightMocked:
    """Test Playwright-backed operations with mocked playwright."""

    def _make_mocked_tool(self):
        tool = BrowserTool()
        return tool

    def test_navigate_playwright(self) -> None:
        tool = self._make_mocked_tool()
        mock_response = MagicMock()
        mock_response.status = 200
        mock_page = MagicMock()
        mock_page.goto.return_value = mock_response
        mock_page.title.return_value = "Mock Title"
        mock_page.url = "https://example.com/"
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright = MagicMock()
        mock_playwright.chromium.launch.return_value = mock_browser

        with patch("playwright.sync_api.sync_playwright") as mock_sp:
            mock_sp.return_value.__enter__ = MagicMock(return_value=mock_playwright)
            mock_sp.return_value.__exit__ = MagicMock(return_value=False)
            result = tool._navigate_playwright("https://example.com", 10)

        assert result.success is True
        assert result.data["title"] == "Mock Title"
        assert result.data["status"] == 200
        assert result.metadata["backend"] == "playwright"

    def test_get_text_playwright(self) -> None:
        tool = self._make_mocked_tool()
        mock_page = MagicMock()
        mock_page.goto.return_value = MagicMock()
        body_locator = MagicMock()
        body_locator.inner_text.return_value = "Page text content"
        mock_page.locator.return_value = body_locator
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright = MagicMock()
        mock_playwright.chromium.launch.return_value = mock_browser

        with patch("playwright.sync_api.sync_playwright") as mock_sp:
            mock_sp.return_value.__enter__ = MagicMock(return_value=mock_playwright)
            mock_sp.return_value.__exit__ = MagicMock(return_value=False)
            result = tool._get_text_playwright("https://example.com", None, 10)

        assert result.success is True
        assert result.data == "Page text content"

    def test_get_text_playwright_with_selector(self) -> None:
        tool = self._make_mocked_tool()
        mock_page = MagicMock()
        mock_page.goto.return_value = MagicMock()
        elem_locator = MagicMock()
        elem_locator.inner_text.return_value = "Selected text"
        mock_page.locator.return_value.first = elem_locator
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright = MagicMock()
        mock_playwright.chromium.launch.return_value = mock_browser

        with patch("playwright.sync_api.sync_playwright") as mock_sp:
            mock_sp.return_value.__enter__ = MagicMock(return_value=mock_playwright)
            mock_sp.return_value.__exit__ = MagicMock(return_value=False)
            result = tool._get_text_playwright("https://example.com", "#main", 10)

        assert result.success is True
        assert result.data == "Selected text"
        mock_page.locator.assert_called_once_with("#main")

    def test_get_links_playwright(self) -> None:
        tool = self._make_mocked_tool()
        mock_page = MagicMock()
        mock_page.goto.return_value = MagicMock()
        link1 = MagicMock()
        link1.get_attribute.return_value = "/a"
        link1.inner_text.return_value = "Link A"
        link2 = MagicMock()
        link2.get_attribute.return_value = "/b"
        link2.inner_text.return_value = "Link B"
        mock_page.locator.return_value.all.return_value = [link1, link2]
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright = MagicMock()
        mock_playwright.chromium.launch.return_value = mock_browser

        with patch("playwright.sync_api.sync_playwright") as mock_sp:
            mock_sp.return_value.__enter__ = MagicMock(return_value=mock_playwright)
            mock_sp.return_value.__exit__ = MagicMock(return_value=False)
            result = tool._get_links_playwright("https://example.com", 10)

        assert result.success is True
        assert len(result.data) == 2
        assert result.data[0] == {"text": "Link A", "href": "/a"}

    def test_screenshot_playwright_base64(self) -> None:
        tool = self._make_mocked_tool()
        mock_page = MagicMock()
        mock_page.goto.return_value = MagicMock()
        mock_page.screenshot.return_value = b"PNGDATA"
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright = MagicMock()
        mock_playwright.chromium.launch.return_value = mock_browser

        with patch("playwright.sync_api.sync_playwright") as mock_sp:
            mock_sp.return_value.__enter__ = MagicMock(return_value=mock_playwright)
            mock_sp.return_value.__exit__ = MagicMock(return_value=False)
            result = tool._screenshot_playwright("https://example.com", None, 10)

        assert result.success is True
        assert result.data == "UE5HREFUQQ=="  # base64 of b"PNGDATA"
        assert result.metadata["encoding"] == "base64"
        assert result.metadata["saved"] is False

    def test_screenshot_playwright_save_to_file(self, tmp_path: Path) -> None:
        tool = BrowserTool(repo_root=tmp_path)
        mock_page = MagicMock()
        mock_page.goto.return_value = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright = MagicMock()
        mock_playwright.chromium.launch.return_value = mock_browser

        with patch("playwright.sync_api.sync_playwright") as mock_sp:
            mock_sp.return_value.__enter__ = MagicMock(return_value=mock_playwright)
            mock_sp.return_value.__exit__ = MagicMock(return_value=False)
            result = tool._screenshot_playwright("https://example.com", tmp_path / "shot.png", 10)

        assert result.success is True
        assert result.data == "shot.png"
        assert result.metadata["saved"] is True
        mock_page.screenshot.assert_called_once_with(path=str(tmp_path / "shot.png"), full_page=True)

    def test_click_playwright(self) -> None:
        tool = self._make_mocked_tool()
        mock_page = MagicMock()
        mock_page.goto.return_value = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright = MagicMock()
        mock_playwright.chromium.launch.return_value = mock_browser

        with patch("playwright.sync_api.sync_playwright") as mock_sp:
            mock_sp.return_value.__enter__ = MagicMock(return_value=mock_playwright)
            mock_sp.return_value.__exit__ = MagicMock(return_value=False)
            result = tool._click_playwright("https://example.com", "#btn", 10)

        assert result.success is True
        assert result.data["clicked"] == "#btn"

    def test_fill_playwright(self) -> None:
        tool = self._make_mocked_tool()
        mock_page = MagicMock()
        mock_page.goto.return_value = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright = MagicMock()
        mock_playwright.chromium.launch.return_value = mock_browser

        with patch("playwright.sync_api.sync_playwright") as mock_sp:
            mock_sp.return_value.__enter__ = MagicMock(return_value=mock_playwright)
            mock_sp.return_value.__exit__ = MagicMock(return_value=False)
            result = tool._fill_playwright("https://example.com", "#input", "hello", 10)

        assert result.success is True
        assert result.data["filled"] == "#input"

    def test_evaluate_playwright(self) -> None:
        tool = self._make_mocked_tool()
        mock_page = MagicMock()
        mock_page.goto.return_value = MagicMock()
        mock_page.evaluate.return_value = 42
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright = MagicMock()
        mock_playwright.chromium.launch.return_value = mock_browser

        with patch("playwright.sync_api.sync_playwright") as mock_sp:
            mock_sp.return_value.__enter__ = MagicMock(return_value=mock_playwright)
            mock_sp.return_value.__exit__ = MagicMock(return_value=False)
            result = tool._evaluate_playwright("https://example.com", "1 + 1", 10)

        assert result.success is True
        assert result.data == 42


class TestBrowserToolSavePathValidation:
    def test_save_path_escapes_workspace(self, tmp_path: Path) -> None:
        tool = BrowserTool(repo_root=tmp_path)
        with pytest.raises(ToolSafetyError, match="escapes workspace"):
            tool._resolve_save_path("../outside.png")

    def test_save_path_inside_workspace(self, tmp_path: Path) -> None:
        tool = BrowserTool(repo_root=tmp_path)
        path = tool._resolve_save_path("screenshots/shot.png")
        assert path == tmp_path / "screenshots" / "shot.png"
        assert path.parent.exists()

    def test_none_save_path(self, tmp_path: Path) -> None:
        tool = BrowserTool(repo_root=tmp_path)
        assert tool._resolve_save_path(None) is None


class TestBrowserToolIntegration:
    """Lightweight integration tests hitting real (but simple) endpoints."""

    def test_navigate_httpbin(self) -> None:
        """Navigate to httpbin.org/html (reliable static endpoint)."""
        tool = BrowserTool()
        ctx = ToolContext(network_allowed=True)
        result = tool.invoke({"operation": "navigate", "url": "https://httpbin.org/html", "timeout": 15}, ctx)
        # May fail in air-gapped environments; skip if so
        if not result.success:
            pytest.skip(f"Network unavailable or blocked: {result.error}")
        assert result.success is True
        assert "Herman Melville" in result.data["title"] or result.data["status"] == 200

    def test_get_text_httpbin(self) -> None:
        tool = BrowserTool()
        ctx = ToolContext(network_allowed=True)
        result = tool.invoke({"operation": "get_text", "url": "https://httpbin.org/html", "timeout": 15}, ctx)
        if not result.success:
            pytest.skip(f"Network unavailable or blocked: {result.error}")
        assert result.success is True
        assert "Moby Dick" in result.data or "Herman Melville" in result.data

    def test_get_links_httpbin(self) -> None:
        tool = BrowserTool()
        ctx = ToolContext(network_allowed=True)
        result = tool.invoke({"operation": "get_links", "url": "https://httpbin.org/html", "timeout": 15}, ctx)
        if not result.success:
            pytest.skip(f"Network unavailable or blocked: {result.error}")
        assert result.success is True
        assert isinstance(result.data, list)
