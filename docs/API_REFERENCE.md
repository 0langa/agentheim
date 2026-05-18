# API Reference

Agentheim exposes a FastAPI API server in `interfaces/api_server/app.py`. The repository also contains a separate Web UI FastAPI app in `interfaces/web_ui/app.py` with a similar but not identical route surface.

## Starting The API Server

```python
from interfaces.api_server import create_api_app
import uvicorn

app = create_api_app(".")
uvicorn.run(app, host="127.0.0.1", port=8000)
```

Repo-local command:

```bash
python -c "from interfaces.api_server import create_api_app; import uvicorn; uvicorn.run(create_api_app('.'), host='127.0.0.1', port=8000)"
```

## Authentication

Write and execution routes depend on the `X-API-Key` header through `verify_api_key`.

```http
X-API-Key: <your-api-key>
```

Configured API keys are loaded from `AI_TEAM_API_KEYS`.

Provider secrets are separate from API-server auth. Provider secrets are stored through Agentheim profiles and secret refs, not loaded from `.env` at runtime.

## Read Routes Without API Key

The current code exposes these read-oriented routes without `X-API-Key`:

- `GET /api/health`
- `GET /api/health/oci`
- `GET /api/tools`
- `GET /api/workflows`
- `GET /api/workflows/{workflow_id}`
- `GET /api/presets`
- `GET /api/memory/{scope}/{key}`
- `GET /api/models`
- `GET /api/providers`
- `GET /api/providers/templates`
- `GET /api/coder/sessions`
- `GET /api/coder/sessions/{session_id}`
- `GET /api/runs/{run_id}`
- `GET /api/runs/{run_id}/stream`
- `GET /api/metrics`

## Rate Limiting

Mutating API routes are wrapped with the repository `RateLimiter`. See `interfaces/api_server/rate_limit.py` for the exact behavior.

## Routes

### Health

- `GET /api/health`
- `GET /api/health/oci`

### Tools

- `GET /api/tools`
- `POST /api/tools/{tool_id}/invoke`
- `POST /api/tools/approvals/{request_id}/grant`
- `POST /api/tools/approvals/{request_id}/deny`

Tool invocation body:

```json
{
  "params": {
    "...": "tool-specific values"
  }
}
```

Current behavior:

- medium-risk operations can return `409` with an approval payload
- denied policy decisions return `403`
- successful execution returns the tool result plus policy metadata

### Workflows

- `GET /api/workflows`
- `GET /api/workflows/{workflow_id}`
- `POST /api/workflows/{workflow_id}/execute`

Workflow execute body:

```json
{
  "params": {
    "...": "workflow-specific values"
  }
}
```

### Presets

- `GET /api/presets`
- `POST /api/presets/{preset_id}/run`

Preset run body:

```json
{
  "inputs": {
    "...": "preset-specific values"
  }
}
```

Both workflow execution and preset execution are asynchronous and return an executor `run_id`.

### Memory

- `GET /api/memory/{scope}/{key}`
- `POST /api/memory/{scope}/{key}`

The route passes the path `scope` through to `MemoryBus`. The common public usage in current examples is `global`.

Write body:

```json
{
  "value": {
    "...": "json-serializable data"
  }
}
```

### Models And Providers

- `GET /api/models`
- `GET /api/providers`
- `GET /api/providers/templates`
- `POST /api/providers`
- `POST /api/providers/assign`

`POST /api/providers` body:

```json
{
  "provider_id": "openai",
  "template": "openai_v1",
  "model": "gpt-4o-mini",
  "role": "planner",
  "profile": "default",
  "endpoint": null,
  "api_key": "secret",
  "capabilities": ["text", "json"]
}
```

`POST /api/providers/assign` body:

```json
{
  "profile": "default",
  "role": "executor",
  "provider_id": "openai",
  "model": "gpt-4o-mini",
  "capabilities": ["text", "json"]
}
```

### Runs

- `GET /api/runs/{run_id}`
- `GET /api/runs/{run_id}/stream`
- `WS /api/runs/{run_id}/ws`

The canonical run summary is built from in-memory executor state when available, then from persisted run artifacts.

### Coder Sessions

- `GET /api/coder/sessions`
- `POST /api/coder/sessions`
- `GET /api/coder/sessions/{session_id}`
- `POST /api/coder/sessions/{session_id}/messages`
- `POST /api/coder/sessions/{session_id}/approvals/{request_id}/grant`
- `POST /api/coder/sessions/{session_id}/approvals/{request_id}/deny`
- `WS /api/coder/sessions/{session_id}/ws`

Session create body:

```json
{
  "workspace_root": ".",
  "trust_mode": "ask"
}
```

Message post body:

```json
{
  "workspace_root": ".",
  "prompt": "Build a FastAPI app in this folder"
}
```

Current behavior:

- coder sessions persist under `.ai-team/runs/<session-id>/`
- the workspace only needs to be an existing directory; git is optional
- trust mode accepts `read_only`, `ask`, or `workspace`
- approval grant and deny routes update pending coder requests without creating a separate tool-specific endpoint
- the coder WebSocket currently emits a session snapshot payload for browser clients

### Context Operations

- `POST /api/ctx/init`
- `POST /api/ctx/scan`
- `POST /api/ctx/run`
- `POST /api/ctx/verify`
- `POST /api/ctx/status`
- `POST /api/ctx/clean`
- `POST /api/ctx/public-docs/impact`
- `POST /api/ctx/public-docs/update`

Current API-server request bodies use the `project` field name, not `project_path`.

Examples:

```json
{ "project": "." }
```

```json
{ "project": ".", "scope": "changed", "write_mode": "patch", "allow_dirty": false }
```

## Web UI Differences

The Web UI app exposes a similar browser-facing surface, but there are important route differences in the current code:

- tool invocation is `POST /api/tools/invoke`
- context request bodies use `project_path`
- the Web UI also exposes `GET /coder` for the dedicated browser-based coder experience
- Web UI routes return Web-specific models such as support-state-decorated workflow and preset listings

## Desktop UI

The desktop UI in `interfaces/desktop_ui/app.py` starts the Web UI server locally, then prefers `pywebview`, falls back to `tkinter`, and finally falls back to the system browser.

## Error Handling

The API server uses structured FastAPI/HTTP exceptions plus route-specific handling for:

- configuration errors
- policy denials
- approval-required responses
- ContextOps safety and verification failures

For exact response payload shapes, use the FastAPI schema generated by the current app instance.
