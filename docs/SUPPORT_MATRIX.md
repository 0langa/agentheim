# Support Matrix

Maintainer-only document. This matrix is a repository classification aid, not a user-facing feature promise by itself.

This matrix is grounded in the current repository tree. It records what surfaces exist in code and what kinds of local test evidence are present. It does not make external live-provider claims unless that evidence is part of the repository and explicitly referenced.

## States

| State | Meaning |
| --- | --- |
| Stable | Default path with strong code and test backing in the current repository |
| Stable candidate | Code-declared support state used by workflows/presets that are intended to harden further |
| Beta | Implemented and tested, but with known limits or thinner guarantees |
| Experimental | Present in code, but not a hardened baseline path |
| Internal | Implementation detail |

## Providers

### Adapter-backed provider types

Implemented in `core/model_registry.py` and `providers/`:

- `openai_compatible`
- `openai_v1`
- `azure_foundry`
- `oci_genai`
- `aws_bedrock`
- `anthropic`
- `gemini`
- `vertex_ai`
- `cohere`
- `perplexity`
- `ollama_cloud`

### Template-backed compatible endpoints

Configured in `config/config.py` and routed through the compatible adapter path where applicable:

- `xai_grok`
- `kimi_moonshot`
- `mistral`
- `groq`
- `deepseek`
- `openrouter`
- `together`
- `ollama`
- `lm_studio`
- `vllm`
- `tgi`
- `llama_cpp`

### Provider Status

| Surface | State | Evidence |
| --- | --- | --- |
| Provider templates | Beta | `config/config.py`, provider template tests, CLI/API/Web listing routes |
| Adapter loading | Beta | `tests/core/test_model_registry.py`, provider adapter tests |
| Secret-backed profiles | Beta | config/profile tests and provider CLI/API paths |
| Hosted compatible vendors | Experimental | template presence and shared compatible adapter path |
| Self-hosted compatible vendors | Beta | template presence, generic compatible adapter path, CLI/API surfaces |

## Workflows And Presets

| Preset | Workflow | Code Support State | Entry Points | Evidence |
| --- | --- | --- | --- | --- |
| `codebase-assistant` | `coding` | `stable_candidate` | CLI, API, Web | coding runtime/workflow tests, patching tests, run-path tests |
| `command-assistant` | `command_assistant` | `stable_candidate` | CLI, API, Web | workflow registration tests, smoke tests, route tests |
| `local-document-chat` | `documents` | `stable_candidate` | CLI, API, Web | documents workflow tests, registration tests, route tests |
| `context-maintainer` | `context_maintainer` | `stable_candidate` | CLI, API ctx routes, Web ctx routes | ctx command tests, ctx API tests, workflow/runtime import tests |
| `file-organizer` | `file_organization` | `beta` | CLI, API, Web | workflow and agent tests |
| `docs-maintainer` | `docs_maintenance` | `beta` | CLI, API, Web | workflow and agent tests |
| `research-report` | `research` | `beta` | CLI, API, Web | workflow and agent tests |
| `github-maintainer` | `github_maintenance` | `beta` | CLI, API, Web | workflow and agent tests |

## Interfaces

| Interface | State | Evidence | Notes |
| --- | --- | --- | --- |
| CLI | Beta | command registration, help output, smoke tests | primary user-facing surface |
| API server | Beta | route tests, run-status tests, tool approval tests | FastAPI app in `interfaces/api_server/app.py` |
| Web UI | Beta | route tests, WebSocket tests, tool approval tests | separate FastAPI app with similar but not identical route shapes |
| Guided TUI | Beta | unit tests | registered under `guided` |
| Desktop UI | Beta | unit/server-start tests | wraps Web UI via `pywebview`, with `tkinter` and browser fallback |

## Tools

| Tool Surface | State | Evidence | Notes |
| --- | --- | --- | --- |
| Filesystem | Beta | tool tests, API/Web approval-path tests | operation-level behavior matters more than top-level tool id |
| Shell | Beta | shell tool tests, policy tests | exposed as `shell.execute` |
| Git | Beta | git tool tests | mutating operations are implemented in the same tool |
| Browser | Experimental | unit tests | async and sync surfaces exist |
| HTTP | Beta | HTTP tests | gated by policy |
| Local DB | Experimental | local DB tests | meaningful use depends on target DB |
| Memory | Beta | memory tests, API/Web coverage | shared through `MemoryBus` |
| MCP | Experimental | MCP tests and config/adapter code | route and CLI support present |

## Advanced Subsystems

| Subsystem | State | Evidence |
| --- | --- | --- |
| AICtx / ContextOps integration | Beta | ctx routes, ctx CLI, ContextOps code/tests, ADR + module map |
| Federation | Experimental | federation tests and transport code |
| Distributed workflows | Experimental | distributed scheduler/server code and tests |
| Marketplace | Experimental | marketplace code and tests |
| Monitoring | Beta | monitoring code and tests |
| Multimodal | Beta | multimodal code and tests |
| Self-improving agents | Internal | agent feedback loop code and tests |

## Current Code-Based Validation Snapshot

- `pytest --collect-only -q` currently collects 1256 total tests, with 1220 selected and 36 deselected by default markers.
- CLI help and command grouping are exercised by CLI/smoke tests.
- API route coverage exists for tools, providers, runs, memory, and ctx surfaces.
- Web UI route coverage includes tool approval flows and run WebSocket streaming.
- Workflow registration/import coverage exists for all built-in workflows.
