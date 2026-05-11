from __future__ import annotations

import json
import logging
import subprocess
import threading
import time
from typing import Any

logger = logging.getLogger(__name__)


class MCPError(Exception):
    """Raised when MCP protocol communication fails."""


class MCPClient:
    """Lightweight MCP client using stdio JSON-RPC transport.

    Does not require the official `mcp` package. Implements the subset
    of the protocol needed for tool discovery and invocation.
    """

    def __init__(
        self,
        command: list[str],
        env: dict[str, str] | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.command = command
        self.env = env
        self.timeout = timeout
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()
        self._msg_id = 0

    def _next_id(self) -> int:
        with self._lock:
            self._msg_id += 1
            return self._msg_id

    def connect(self) -> None:
        """Spawn the MCP server process and perform initialize handshake."""
        if self._proc is not None:
            return

        try:
            self._proc = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self.env,
            )
        except FileNotFoundError as exc:
            raise MCPError(f"MCP server command not found: {self.command[0]}") from exc

        # Send initialize request
        init_req = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "agentheim", "version": "1.0.0"},
            },
        }
        self._send(init_req)
        init_resp = self._read_response(init_req["id"])
        if init_resp is None:
            raise MCPError("MCP initialize timed out")
        if "error" in init_resp:
            raise MCPError(f"MCP initialize error: {init_resp['error']}")

        # Send initialized notification
        self._send({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        })

    def disconnect(self) -> None:
        """Terminate the MCP server process."""
        if self._proc is None:
            return
        try:
            self._proc.terminate()
            self._proc.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            self._proc.kill()
            self._proc.wait()
        except Exception as exc:
            logger.warning("MCP disconnect error: %s", exc)
        finally:
            self._proc = None

    def __enter__(self) -> "MCPClient":
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.disconnect()

    def list_tools(self) -> list[dict[str, Any]]:
        """Discover tools exposed by the MCP server."""
        self._ensure_connected()
        req = {"jsonrpc": "2.0", "id": self._next_id(), "method": "tools/list"}
        self._send(req)
        resp = self._read_response(req["id"])
        if resp is None:
            raise MCPError("tools/list timed out")
        if "error" in resp:
            raise MCPError(f"tools/list error: {resp['error']}")
        result = resp.get("result", {})
        return list(result.get("tools", []))

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Invoke an MCP tool by name with arguments."""
        self._ensure_connected()
        req = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
        self._send(req)
        resp = self._read_response(req["id"])
        if resp is None:
            raise MCPError(f"tools/call({name}) timed out")
        if "error" in resp:
            raise MCPError(f"tools/call({name}) error: {resp['error']}")
        return dict(resp.get("result", {}))

    def _ensure_connected(self) -> None:
        if self._proc is None or self._proc.poll() is not None:
            raise MCPError("MCP client not connected")

    def _send(self, msg: dict[str, Any]) -> None:
        if self._proc is None or self._proc.stdin is None:
            raise MCPError("MCP stdin not available")
        line = json.dumps(msg, ensure_ascii=False)
        self._proc.stdin.write(line + "\n")
        self._proc.stdin.flush()

    def _read_response(self, expected_id: int) -> dict[str, Any] | None:
        if self._proc is None or self._proc.stdout is None:
            return None
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            try:
                line = self._proc.stdout.readline()
            except Exception:
                return None
            if not line:
                time.sleep(0.05)
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if data.get("id") == expected_id:
                return data
            # Ignore notifications / unsolicited messages
        return None
