"""HTTP tool implementing ToolProtocol.

Outbound HTTP requests with network policy enforcement.
"""

from __future__ import annotations

from typing import Any

from core.errors import ToolSafetyError
from core.tool_protocol import BaseTool, ParamSchema, ReturnSchema, RiskLevel, ToolContext, ToolResult, ToolSchema


class HttpTool(BaseTool):
    """Outbound HTTP requests with network policy enforcement."""

    def __init__(self) -> None:
        schema = ToolSchema(
            description="Make outbound HTTP requests.",
            parameters={
                "method": ParamSchema(type="string", description="HTTP method", enum=["GET", "POST", "PUT", "DELETE", "PATCH"], required=True),
                "url": ParamSchema(type="string", description="Request URL", required=True),
                "headers": ParamSchema(type="object", description="Request headers", required=False),
                "body": ParamSchema(type="string", description="Request body", required=False),
                "timeout": ParamSchema(type="integer", description="Timeout in seconds", default=30, required=False),
            },
            returns=ReturnSchema(type="object", description="{status, headers, body}"),
        )
        super().__init__("http.request", schema, RiskLevel.HIGH)

    def invoke(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        valid, err = self.validate_params(params)
        if not valid:
            return ToolResult(success=False, error=err)

        url = params.get("url", "")
        method = params.get("method", "GET")
        headers = params.get("headers", {})
        body = params.get("body")
        timeout = params.get("timeout", 30)

        # Network policy check
        if not context.network_allowed:
            return ToolResult(success=False, error="Network access is not allowed by policy.")

        try:
            import urllib.request
            import json

            req = urllib.request.Request(url, method=method, headers=headers)
            if body is not None:
                req.data = body.encode("utf-8") if isinstance(body, str) else body

            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_body = response.read().decode("utf-8", errors="ignore")
                return ToolResult(
                    success=True,
                    data={
                        "status": response.status,
                        "headers": dict(response.headers),
                        "body": response_body,
                    },
                )
        except Exception as exc:
            return ToolResult(success=False, error=f"HTTP request failed: {exc}")
