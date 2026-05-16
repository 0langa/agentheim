# Architecture

Agentheim is a local-first AI automation platform built around a generic orchestration runtime.

## System Overview

The runtime serves three user layers from the same engine:

```text
Beginner (Presets)
  -> guided preset-driven workflows

Power User (CLI / Config)
  -> direct control over providers, roles, and runtime inputs

Developer (Extensible)
  -> add providers, workflows, and tools without changing the core runtime

Core Runtime
  -> DAG execution, policy engine, ledgers, tool mediation, model resolution
```

## Design Principles

- `core/` remains generic and does not hard-code provider, workflow, or tool behavior
- all side effects route through policy-gated tools
- run state is recorded through append-oriented ledgers and artifacts
- providers are resolved through interchangeable adapters
- local-first operation is the default

## Directory Layout

```text
agentheim/
├── core/          # Generic runtime engine
├── providers/     # Provider adapters
├── tools/         # Mediated tool implementations
├── workflows/     # Workflow packs
├── memory/        # Memory subsystem
├── interfaces/    # CLI, API server, Web UI, Desktop UI, guided TUI
├── presets/       # Preset definitions
├── agents/        # Runtime self-improving hooks
├── federation/    # Distributed coordination
├── marketplace/   # Plugin marketplace
├── multimodal/    # Vision-related support
├── monitoring/    # Metrics and health reporting
├── config/        # Configuration loading
└── docs/          # Public documentation
```

## Core Runtime

Important modules under `core/` include:

| Component | Responsibility |
|-----------|----------------|
| `workflow_runner.py` | Executes DAGs with dependencies and retries |
| `run_executor.py` | Top-level run execution |
| `ledger.py` | Append-only event log with hash chaining |
| `policy_engine.py` | Allow/deny/ask enforcement for tool calls |
| `tool_protocol.py` | Mediated tool invocation interface |
| `model_registry.py` | Capability-based provider/model resolution |
| `events.py` | Structured event schema |
| `resume.py` | Run replay and resumption |

`core/model_registry.py` contains a convenience provider map bootstrap, but the registry itself remains generic.

## Providers

Current provider adapters in code include:

- `openai_v1`
- `azure_foundry`
- `aws_bedrock`
- `anthropic`
- `gemini`
- `vertex_ai`
- `cohere`
- `perplexity`
- `ollama_cloud`
- `oci_genai`

## Interfaces

The current user-facing entrypoints are:

- CLI in `interfaces/cli/`
- API server in `interfaces/api_server/`
- Web UI in `interfaces/web_ui/`
- Desktop wrapper in `interfaces/desktop_ui/`
- Guided terminal UI in `interfaces/guided_tui/`

## Notes

- `workflows/coding/` and `workflows/context_maintainer/` use dedicated runtime paths in addition to the generic workflow abstractions.
- `agents/self_improving/` is runtime code used by interface-level run hooks, not repository-only scaffolding.
