from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.tool_protocol import RiskLevel, ToolContext
from tools.mcp.client import MCPClient, MCPError
from tools.mcp.config import MCPServerConfig, load_mcp_config
from tools.mcp.tool_adapter import MCPTool, _convert_schema, _mcp_type_to_param_type


class TestMCPTypeMapping:
    def test_string_type(self) -> None:
        assert _mcp_type_to_param_type("string") == "str"

    def test_integer_type(self) -> None:
        assert _mcp_type_to_param_type("integer") == "int"

    def test_number_type(self) -> None:
        assert _mcp_type_to_param_type("number") == "float"

    def test_boolean_type(self) -> None:
        assert _mcp_type_to_param_type("boolean") == "bool"

    def test_unknown_type_defaults_to_str(self) -> None:
        assert _mcp_type_to_param_type("custom") == "str"


class TestSchemaConversion:
    def test_convert_simple_schema(self) -> None:
        mcp_schema = {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "count": {"type": "integer", "description": "How many"},
            },
            "required": ["path"],
        }
        params = _convert_schema(mcp_schema)
        assert "path" in params
        assert params["path"].required is True
        assert params["path"].type == "str"
        assert "count" in params
        assert params["count"].required is False
        assert params["count"].type == "int"

    def test_enum_preserved(self) -> None:
        mcp_schema = {
            "type": "object",
            "properties": {
                "mode": {"type": "string", "enum": ["read", "write"]},
            },
        }
        params = _convert_schema(mcp_schema)
        assert params["mode"].enum == ["read", "write"]


class TestMCPTool:
    def test_tool_id_prefixed(self) -> None:
        client = MagicMock()
        info = {"name": "read_file", "description": "Read a file"}
        tool = MCPTool(client, info)
        assert tool.tool_id == "mcp.read_file"

    def test_schema_description(self) -> None:
        client = MagicMock()
        info = {
            "name": "read_file",
            "description": "Read a file",
            "inputSchema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        }
        tool = MCPTool(client, info)
        assert tool.schema.description == "Read a file"
        assert "path" in tool.schema.parameters

    def test_risk_level(self) -> None:
        client = MagicMock()
        info = {"name": "x", "description": "x"}
        tool = MCPTool(client, info)
        assert tool.risk_level == RiskLevel.MEDIUM

    def test_invoke_success(self) -> None:
        client = MagicMock()
        client.call_tool.return_value = {"content": [{"type": "text", "text": "hello"}]}
        info = {"name": "echo", "description": "Echo"}
        tool = MCPTool(client, info)
        result = tool.invoke({"msg": "hi"}, ToolContext())
        assert result.success is True
        assert result.metadata.get("source") == "mcp"
        client.call_tool.assert_called_once_with("echo", {"msg": "hi"})

    def test_invoke_failure(self) -> None:
        client = MagicMock()
        client.call_tool.side_effect = RuntimeError("boom")
        info = {"name": "fail", "description": "Fail"}
        tool = MCPTool(client, info)
        result = tool.invoke({}, ToolContext())
        assert result.success is False
        assert "boom" in result.error


class TestMCPClient:
    def test_connect_command_not_found(self) -> None:
        client = MCPClient(["definitely_not_a_real_command_12345"])
        with pytest.raises(MCPError, match="not found"):
            client.connect()

    def test_disconnect_without_connect_is_noop(self) -> None:
        client = MCPClient(["echo", "hi"])
        client.disconnect()  # should not raise

    def test_list_tools_and_call_tool_mocked(self) -> None:
        client = MCPClient(["dummy"])
        client._proc = MagicMock()
        client._proc.poll.return_value = None
        client._proc.stdin = MagicMock()
        client._proc.stdout = MagicMock()

        # Simulate tools/list response (id will be 1 since connect() is bypassed)
        list_resp = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": [
                    {"name": "read", "description": "Read file"},
                    {"name": "write", "description": "Write file"},
                ]
            },
        }
        # Simulate tools/call response (id will be 2)
        call_resp = {"jsonrpc": "2.0", "id": 2, "result": {"content": [{"type": "text", "text": "ok"}]}}

        client._proc.stdout.readline.side_effect = [
            json.dumps(list_resp) + "\n",
            json.dumps(call_resp) + "\n",
        ]

        # We need to bypass connect() since we're mocking _proc directly
        # Just test list_tools and call_tool directly
        tools = client.list_tools()
        assert len(tools) == 2
        assert tools[0]["name"] == "read"

        result = client.call_tool("read", {"path": "/tmp/x"})
        assert result["content"][0]["text"] == "ok"


class TestMCPConfig:
    def test_load_config_from_file(self, tmp_path: Path) -> None:
        path = tmp_path / "mcp.json"
        path.write_text(
            json.dumps({
                "servers": [
                    {"name": "fs", "command": ["npx", "fs"], "enabled": True},
                    {"name": "db", "command": ["uvx", "db"], "enabled": False},
                ]
            }),
            encoding="utf-8",
        )
        servers = load_mcp_config(path)
        assert len(servers) == 2
        assert servers[0].name == "fs"
        assert servers[0].enabled is True
        assert servers[1].enabled is False

    def test_load_config_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(
            "AI_TEAM_MCP_SERVERS_JSON",
            json.dumps({"servers": [{"name": "env", "command": ["echo"]}]}),
        )
        servers = load_mcp_config(Path("/nonexistent"))
        assert len(servers) == 1
        assert servers[0].name == "env"

    def test_default_enabled(self, tmp_path: Path) -> None:
        path = tmp_path / "mcp.json"
        path.write_text(
            json.dumps({"servers": [{"name": "x", "command": ["echo"]}]}),
            encoding="utf-8",
        )
        servers = load_mcp_config(path)
        assert servers[0].enabled is True
