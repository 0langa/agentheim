"""Browser automation tool implementing ToolProtocol.

Web page interaction with Playwright primary backend and HTTP fallback chain.
"""

from __future__ import annotations

import base64
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from core.errors import ToolSafetyError
from core.tool_protocol import BaseTool, ParamSchema, ReturnSchema, RiskLevel, ToolContext, ToolResult, ToolSchema


class BrowserTool(BaseTool):
    """Browser automation with Playwright primary and HTTP fallback."""

    PLAYWRIGHT_OPS = {"screenshot", "click", "fill", "evaluate"}

    def __init__(self, repo_root: str | Path = ".") -> None:
        self.repo_root = Path(repo_root).resolve()
        schema = ToolSchema(
            description="Browser automation for web page interaction.",
            parameters={
                "operation": ParamSchema(
                    type="string",
                    description="Operation to perform",
                    enum=["navigate", "get_text", "get_links", "screenshot", "click", "fill", "evaluate"],
                    required=True,
                ),
                "url": ParamSchema(type="string", description="URL to navigate to", required=False),
                "selector": ParamSchema(type="string", description="CSS selector for click/fill/get_text", required=False),
                "value": ParamSchema(type="string", description="Value to fill into input", required=False),
                "script": ParamSchema(type="string", description="JavaScript to evaluate", required=False),
                "save_path": ParamSchema(type="string", description="Relative path to save screenshot (omit for base64)", required=False),
                "timeout": ParamSchema(type="integer", description="Timeout in seconds", default=30, required=False),
            },
            returns=ReturnSchema(type="object", description="Operation result"),
        )
        super().__init__("browser", schema, RiskLevel.HIGH)

    def invoke(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        valid, err = self.validate_params(params)
        if not valid:
            return ToolResult(success=False, error=err)

        operation = params.get("operation")
        url = params.get("url", "")

        # Network policy check
        if not context.network_allowed:
            return ToolResult(success=False, error="Network access is not allowed by policy.")

        # URL required for all ops except evaluate (which may run on current page context)
        if operation != "evaluate" and not url:
            return ToolResult(success=False, error="Parameter 'url' is required for this operation.")

        try:
            if operation == "navigate":
                return self._navigate(url, params.get("timeout", 30))
            if operation == "get_text":
                return self._get_text(url, params.get("selector"), params.get("timeout", 30))
            if operation == "get_links":
                return self._get_links(url, params.get("timeout", 30))
            if operation == "screenshot":
                return self._screenshot(url, params.get("save_path"), params.get("timeout", 30))
            if operation == "click":
                return self._click(url, params.get("selector", ""), params.get("timeout", 30))
            if operation == "fill":
                return self._fill(url, params.get("selector", ""), params.get("value", ""), params.get("timeout", 30))
            if operation == "evaluate":
                return self._evaluate(url, params.get("script", ""), params.get("timeout", 30))
        except ToolSafetyError as exc:
            return ToolResult(success=False, error=str(exc))

        return ToolResult(success=False, error=f"Unknown operation: {operation}")

    # ------------------------------------------------------------------
    # Backend helpers
    # ------------------------------------------------------------------

    def _resolve_save_path(self, raw_path: str | None) -> Path | None:
        """Resolve and validate a screenshot save path."""
        if not raw_path:
            return None
        target = (self.repo_root / raw_path).resolve()
        try:
            target.relative_to(self.repo_root)
        except ValueError:
            raise ToolSafetyError(f"Save path escapes workspace: {raw_path}")
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    @staticmethod
    def _playwright_available() -> bool:
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------

    def _navigate(self, url: str, timeout: int) -> ToolResult:
        """Navigate to URL and return page metadata."""
        if self._playwright_available():
            return self._navigate_playwright(url, timeout)
        return self._navigate_http_fallback(url, timeout)

    def _get_text(self, url: str, selector: str | None, timeout: int) -> ToolResult:
        if self._playwright_available():
            return self._get_text_playwright(url, selector, timeout)
        return self._get_text_http_fallback(url, selector, timeout)

    def _get_links(self, url: str, timeout: int) -> ToolResult:
        if self._playwright_available():
            return self._get_links_playwright(url, timeout)
        return self._get_links_http_fallback(url, timeout)

    def _screenshot(self, url: str, save_path: str | None, timeout: int) -> ToolResult:
        if not self._playwright_available():
            return ToolResult(success=False, error="Screenshot requires Playwright which is not available.")
        target = self._resolve_save_path(save_path)
        return self._screenshot_playwright(url, target, timeout)

    def _click(self, url: str, selector: str, timeout: int) -> ToolResult:
        if not selector:
            return ToolResult(success=False, error="Parameter 'selector' is required for click.")
        if not self._playwright_available():
            return ToolResult(success=False, error="Click requires Playwright which is not available.")
        return self._click_playwright(url, selector, timeout)

    def _fill(self, url: str, selector: str, value: str, timeout: int) -> ToolResult:
        if not selector:
            return ToolResult(success=False, error="Parameter 'selector' is required for fill.")
        if not self._playwright_available():
            return ToolResult(success=False, error="Fill requires Playwright which is not available.")
        return self._fill_playwright(url, selector, value, timeout)

    def _evaluate(self, url: str, script: str, timeout: int) -> ToolResult:
        if not script:
            return ToolResult(success=False, error="Parameter 'script' is required for evaluate.")
        if not self._playwright_available():
            return ToolResult(success=False, error="Evaluate requires Playwright which is not available.")
        return self._evaluate_playwright(url, script, timeout)

    # ------------------------------------------------------------------
    # Playwright backends
    # ------------------------------------------------------------------

    def _navigate_playwright(self, url: str, timeout: int) -> ToolResult:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                response = page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
                status = response.status if response else None
                title = page.title()
                return ToolResult(
                    success=True,
                    data={"title": title, "status": status, "url": page.url},
                    metadata={"backend": "playwright"},
                )
            finally:
                browser.close()

    def _get_text_playwright(self, url: str, selector: str | None, timeout: int) -> ToolResult:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
                if selector:
                    element = page.locator(selector).first
                    text = element.inner_text(timeout=timeout * 1000)
                else:
                    text = page.locator("body").inner_text(timeout=timeout * 1000)
                return ToolResult(success=True, data=text, metadata={"backend": "playwright"})
            finally:
                browser.close()

    def _get_links_playwright(self, url: str, timeout: int) -> ToolResult:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
                links = page.locator("a").all()
                results = []
                for link in links:
                    href = link.get_attribute("href") or ""
                    text = link.inner_text().strip()
                    if href:
                        results.append({"text": text, "href": href})
                return ToolResult(success=True, data=results, metadata={"backend": "playwright", "count": len(results)})
            finally:
                browser.close()

    def _screenshot_playwright(self, url: str, save_path: Path | None, timeout: int) -> ToolResult:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
                if save_path:
                    page.screenshot(path=str(save_path), full_page=True)
                    return ToolResult(
                        success=True,
                        data=str(save_path.relative_to(self.repo_root)),
                        metadata={"backend": "playwright", "format": "png", "saved": True},
                    )
                else:
                    png_bytes = page.screenshot(full_page=True)
                    b64 = base64.b64encode(png_bytes).decode("ascii")
                    return ToolResult(
                        success=True,
                        data=b64,
                        metadata={"backend": "playwright", "format": "png", "saved": False, "encoding": "base64"},
                    )
            finally:
                browser.close()

    def _click_playwright(self, url: str, selector: str, timeout: int) -> ToolResult:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
                page.locator(selector).first.click(timeout=timeout * 1000)
                return ToolResult(success=True, data={"clicked": selector}, metadata={"backend": "playwright"})
            finally:
                browser.close()

    def _fill_playwright(self, url: str, selector: str, value: str, timeout: int) -> ToolResult:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
                page.locator(selector).first.fill(value, timeout=timeout * 1000)
                return ToolResult(success=True, data={"filled": selector}, metadata={"backend": "playwright"})
            finally:
                browser.close()

    def _evaluate_playwright(self, url: str, script: str, timeout: int) -> ToolResult:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
                result = page.evaluate(script)
                return ToolResult(success=True, data=result, metadata={"backend": "playwright"})
            finally:
                browser.close()

    # ------------------------------------------------------------------
    # HTTP fallback backends (requests → urllib)
    # ------------------------------------------------------------------

    def _fetch_with_requests(self, url: str, timeout: int) -> tuple[int, str]:
        import requests

        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "AI-Team-BrowserTool/1.0"})
        return resp.status_code, resp.text

    def _fetch_with_urllib(self, url: str, timeout: int) -> tuple[int | None, str]:
        req = urllib.request.Request(url, headers={"User-Agent": "AI-Team-BrowserTool/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="ignore")

    def _fetch(self, url: str, timeout: int) -> tuple[int | None, str]:
        try:
            return self._fetch_with_requests(url, timeout)
        except Exception:
            try:
                return self._fetch_with_urllib(url, timeout)
            except urllib.error.HTTPError as exc:
                return exc.code, exc.read().decode("utf-8", errors="ignore")
            except Exception as exc:
                return None, str(exc)

    def _navigate_http_fallback(self, url: str, timeout: int) -> ToolResult:
        status, html = self._fetch(url, timeout)
        if status is None:
            return ToolResult(success=False, error=f"Failed to fetch URL: {html}")
        # Extract title from HTML
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""
        return ToolResult(
            success=True,
            data={"title": title, "status": status, "url": url},
            metadata={"backend": "http_fallback"},
        )

    def _get_text_http_fallback(self, url: str, selector: str | None, timeout: int) -> ToolResult:
        status, html = self._fetch(url, timeout)
        if status is None:
            return ToolResult(success=False, error=f"Failed to fetch URL: {html}")
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            if selector:
                element = soup.select_one(selector)
                if element is None:
                    return ToolResult(success=False, error=f"Selector not found: {selector}")
                text = element.get_text(separator="\n", strip=True)
            else:
                # Remove script/style tags
                for tag in soup(["script", "style"]):
                    tag.decompose()
                text = soup.get_text(separator="\n", strip=True)
            return ToolResult(success=True, data=text, metadata={"backend": "http_fallback"})
        except ImportError:
            # Pure regex fallback
            text = re.sub(r"<[^>]+>", " ", html)
            text = re.sub(r"\s+", " ", text).strip()
            return ToolResult(success=True, data=text, metadata={"backend": "urllib_fallback"})

    def _get_links_http_fallback(self, url: str, timeout: int) -> ToolResult:
        status, html = self._fetch(url, timeout)
        if status is None:
            return ToolResult(success=False, error=f"Failed to fetch URL: {html}")
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            links = []
            for a in soup.find_all("a", href=True):
                links.append({"text": a.get_text(strip=True), "href": a["href"]})
            return ToolResult(success=True, data=links, metadata={"backend": "http_fallback", "count": len(links)})
        except ImportError:
            # Regex fallback
            links = []
            for match in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL):
                href = match.group(1)
                text = re.sub(r"<[^>]+>", "", match.group(2)).strip()
                links.append({"text": text, "href": href})
            return ToolResult(success=True, data=links, metadata={"backend": "urllib_fallback", "count": len(links)})
