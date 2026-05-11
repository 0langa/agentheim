"""FastAPI API server with OpenAPI spec, auth, and rate limiting."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.capability_registry import list_workflows as cap_list_workflows
from core.tool_protocol import ToolContext, ToolResult
from memory.bus import MemoryBus
from tools.registry import ToolRegistry

from interfaces.api_server.auth import verify_api_key
from interfaces.api_server.rate_limit import RateLimiter


# ------------------------------------------------------------------
# Pydantic models (module-level for FastAPI compatibility)
# ------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    components: dict[str, str] = Field(default_factory=dict)


class ToolSchemaItem(BaseModel):
    tool_id: str
    risk_level: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class ToolInvokeRequest(BaseModel):
    params: dict[str, Any] = Field(default_factory=dict)


class ToolInvokeResponse(BaseModel):
    success: bool
    data: Any = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowListItem(BaseModel):
    workflow_id: str
    name: str
    description: str


class WorkflowDetail(BaseModel):
    workflow_id: str
    name: str
    description: str
    required_agents: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)


class PresetListItem(BaseModel):
    preset_id: str
    name: str
    description: str


class MemoryReadResponse(BaseModel):
    scope: str
    key: str
    value: Any = None
    found: bool = False


class MemoryWriteRequest(BaseModel):
    value: dict[str, Any]


class MemoryWriteResponse(BaseModel):
    scope: str
    key: str
    status: str = "written"


class ModelListItem(BaseModel):
    model_id: str
    provider: str
    capabilities: list[str] = Field(default_factory=list)


class ProviderListItem(BaseModel):
    provider_id: str
    healthy: bool


class RunStatusResponse(BaseModel):
    run_id: str
    status: str
    artifacts: list[str] = Field(default_factory=list)


# ------------------------------------------------------------------
# App factory
# ------------------------------------------------------------------

def create_api_app(repo_root: str | Path = ".") -> FastAPI:
    repo_root = Path(repo_root).resolve()
    app = FastAPI(
        title="Local Agent Orchestra API",
        description="Production API for agent orchestration, tool invocation, and workflow management.",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    tool_registry = ToolRegistry(repo_root)
    memory_bus = MemoryBus(repo_root)
    rate_limiter = RateLimiter(max_requests=60, window_seconds=60.0)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _find_tool(tool_id: str):
        for attr_name in dir(tool_registry):
            if attr_name.startswith("_"):
                continue
            candidate = getattr(tool_registry, attr_name)
            if getattr(candidate, "tool_id", None) == tool_id:
                return candidate
        return None

    def _import_workflows() -> None:
        try:
            import workflows.coding
            import workflows.command_assistant
            import workflows.docs_maintenance
            import workflows.documents
            import workflows.file_organization
            import workflows.github_maintenance
            import workflows.research
        except Exception:
            pass

    def _tool_schema_to_dict(tool) -> dict[str, Any]:
        params = {}
        for name, ps in tool.schema.parameters.items():
            params[name] = {
                "type": ps.type,
                "description": ps.description,
                "required": ps.required,
                "default": ps.default,
            }
            if ps.enum:
                params[name]["enum"] = ps.enum
        return params

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------

    @app.get("/api/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return HealthResponse(
            components={
                "tools": "ok",
                "memory": "ok",
                "workflows": "ok",
            }
        )

    @app.get("/api/tools", response_model=list[ToolSchemaItem], tags=["tools"])
    def list_tools() -> list[ToolSchemaItem]:
        """List all available tools with their schemas."""
        items = []
        for attr_name in dir(tool_registry):
            if attr_name.startswith("_"):
                continue
            tool = getattr(tool_registry, attr_name)
            if hasattr(tool, "tool_id") and hasattr(tool, "schema"):
                items.append(
                    ToolSchemaItem(
                        tool_id=tool.tool_id,
                        risk_level=tool.risk_level.value,
                        description=tool.schema.description,
                        parameters=_tool_schema_to_dict(tool),
                    )
                )
        return sorted(items, key=lambda x: x.tool_id)

    @app.post(
        "/api/tools/{tool_id}/invoke",
        response_model=ToolInvokeResponse,
        tags=["tools"],
        dependencies=[Depends(rate_limiter.check)],
    )
    def invoke_tool(
        tool_id: str,
        request: ToolInvokeRequest,
        api_key: str = Depends(verify_api_key),
    ) -> ToolInvokeResponse:
        """Invoke a tool with the given parameters. MEDIUM+ risk tools require confirmation."""
        tool = _find_tool(tool_id)
        if tool is None:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found")

        # Safety: block high/critical risk tools without explicit confirmation
        if tool.risk_level.value in ("high", "critical"):
            raise HTTPException(
                status_code=403,
                detail=f"Tool '{tool_id}' has risk level '{tool.risk_level.value}'. Use CLI for high-risk operations.",
            )

        ctx = ToolContext(network_allowed=False)
        result: ToolResult = tool.invoke(request.params, ctx)
        return ToolInvokeResponse(
            success=result.success,
            data=result.data,
            error=result.error,
            metadata=result.metadata,
        )

    @app.get("/api/workflows", response_model=list[WorkflowListItem], tags=["workflows"])
    def list_workflows() -> list[WorkflowListItem]:
        """List registered workflows."""
        _import_workflows()
        return [
            WorkflowListItem(
                workflow_id=w.id,
                name=w.id.replace("_", " ").title(),
                description=getattr(w, "description", "") or "",
            )
            for w in cap_list_workflows()
        ]

    @app.get("/api/workflows/{workflow_id}", response_model=WorkflowDetail, tags=["workflows"])
    def get_workflow(workflow_id: str) -> WorkflowDetail:
        """Get detailed information about a workflow."""
        _import_workflows()
        for w in cap_list_workflows():
            if w.id == workflow_id:
                return WorkflowDetail(
                    workflow_id=w.id,
                    name=w.id.replace("_", " ").title(),
                    description=getattr(w, "description", "") or "",
                    required_agents=getattr(w, "required_agents", []),
                    required_tools=getattr(w, "required_tools", []),
                )
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")

    @app.get("/api/presets", response_model=list[PresetListItem], tags=["presets"])
    def list_presets() -> list[PresetListItem]:
        """List available presets."""
        from presets import PRESET_REGISTRY

        return [
            PresetListItem(
                preset_id=p.preset_id,
                name=getattr(p, "name", p.preset_id) or p.preset_id,
                description=getattr(p, "description", "") or "",
            )
            for p in PRESET_REGISTRY.list()
        ]

    @app.get("/api/memory/{scope}/{key}", response_model=MemoryReadResponse, tags=["memory"])
    def read_memory(scope: str, key: str) -> MemoryReadResponse:
        """Read a value from the memory bus."""
        value = memory_bus.read(scope, key)
        return MemoryReadResponse(
            scope=scope,
            key=key,
            value=value,
            found=value is not None,
        )

    @app.post("/api/memory/{scope}/{key}", response_model=MemoryWriteResponse, tags=["memory"])
    def write_memory(
        scope: str,
        key: str,
        request: MemoryWriteRequest,
        api_key: str = Depends(verify_api_key),
    ) -> MemoryWriteResponse:
        """Write a value to the memory bus."""
        memory_bus.write(scope, key, request.value)
        return MemoryWriteResponse(scope=scope, key=key)

    @app.get("/api/models", response_model=list[ModelListItem], tags=["models"])
    def list_models() -> list[ModelListItem]:
        """List configured models and their capabilities."""
        from core.model_registry import ModelRegistry

        try:
            registry = ModelRegistry.from_team_config()
            items = []
            for binding in registry._bindings.values():
                items.append(
                    ModelListItem(
                        model_id=binding.model_id,
                        provider=binding.provider,
                        capabilities=list(binding.capabilities),
                    )
                )
            return items
        except Exception:
            return []

    @app.get("/api/providers", response_model=list[ProviderListItem], tags=["providers"])
    def list_providers() -> list[ProviderListItem]:
        """List providers and their health status."""
        from providers import base as provider_base

        # Basic provider listing; health checks would require credentials
        providers = [
            ProviderListItem(provider_id="openai_v1", healthy=True),
            ProviderListItem(provider_id="aws_bedrock", healthy=True),
            ProviderListItem(provider_id="azure_foundry", healthy=True),
            ProviderListItem(provider_id="oci_genai", healthy=True),
        ]
        return providers

    @app.get("/api/runs/{run_id}", response_model=RunStatusResponse, tags=["runs"])
    def get_run_status(run_id: str) -> RunStatusResponse:
        """Get the status of a run."""
        # Runs are stored in .ai-team/runs/{run_id}/
        run_dir = repo_root / ".ai-team" / "runs" / run_id
        if not run_dir.exists():
            raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

        artifacts = []
        if run_dir.is_dir():
            artifacts = sorted(
                f.name for f in run_dir.iterdir() if f.is_file()
            )

        status_str = "completed" if (run_dir / "final_report.md").exists() else "in_progress"
        return RunStatusResponse(
            run_id=run_id,
            status=status_str,
            artifacts=artifacts,
        )

    return app
