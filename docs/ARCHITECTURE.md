# Architecture

> System design, module layout, runtime phases, and boundary rules for Agentheim.

---

## Table of Contents

- [System Overview](#system-overview)
- [Directory Layout](#directory-layout)
- [Core Runtime](#core-runtime)
- [Subsystems](#subsystems)
- [Runtime Phases](#runtime-phases)
- [Architectural Laws](#architectural-laws)
- [Boundary Rules](#boundary-rules)
- [Ownership Model](#ownership-model)

---

## System Overview

Agentheim is a **preset-driven, local-first AI automation platform** with a generic orchestration runtime at its core. The system is organized around three user layers — beginner, power-user, and developer — all served by the same extensible engine.

```
                    +------------------+
                    |   Beginner Layer  |
                    |  (Preset-driven)  |
                    +--------+---------+
                             | exposes
                    +--------v---------+
                    |  Power-User Layer |
                    | (Configurable)    |
                    +--------+---------+
                             | exposes
                    +--------v---------+
                    |   Developer Layer |
                    |  (Extensible)     |
                    +------------------+
                             |
                    +--------v---------+
                    |   Core Runtime    |
                    | (Generic Engine)  |
                    +------------------+
```

### Design Principles

- **Core ignorance** — `core/` knows no provider, model, workflow, or tool names (one exception: `core/model_registry.py` contains `DEFAULT_PROVIDER_MAP` as a bootstrapping default; the `ModelRegistry` class itself remains fully generic)
- **Local-first** — zero external services required; privacy modes enforced in code
- **Safety by default** — destructive ops require approval; policies are code, not prompts
- **Fully auditable** — every run produces an append-only event ledger
- **Provider-agnostic** — swap providers without code changes

---

## Directory Layout

```
agentheim/
│
├── core/                      # Generic runtime engine
│   ├── workflow_runner.py     # DAG execution, retries, resumption
│   ├── agent_protocol.py      # Agent message schemas
│   ├── model_registry.py      # Capability-based model resolution
│   ├── tool_protocol.py       # Mediated tool invocation interface
│   ├── policy_engine.py       # Allow/deny/ask enforcement
│   ├── ledger.py              # Append-only event log with hash chain
│   ├── artifact_store.py      # Per-run artifact management
│   ├── capability_registry.py # Provider/tool capability declarations
│   ├── context_packer.py      # Legacy context packer (deprecated in favor of ContextOps/AICtx)
│   ├── events.py              # Structured event schema
│   ├── error_classification.py # Failure taxonomy
│   ├── retry_engine.py        # Bounded retry with backoff
│   ├── step_budget.py         # Token/time/iteration budgets
│   ├── cascading_router.py    # Model failover chains
│   ├── privacy_enforcer.py    # Privacy mode enforcement
│   ├── approval_workflow.py   # Approval gate management
│   ├── public_api.py          # Stable public interface
│   ├── resume.py              # Run replay and resumption
│   ├── run_executor.py        # Top-level run execution
│   ├── logging.py             # Logging setup
│   ├── errors.py              # Exception hierarchy
│   ├── schemas.py / schemas_runtime.py
│   └── state_machine.py       # Runtime phase machine
│
├── providers/                 # Lazy-loaded provider adapters
│   ├── base.py                # Abstract provider protocol
│   ├── openai_v1.py           # OpenAI-compatible adapter
│   ├── azure_foundry.py       # Azure AI Foundry adapter
│   ├── aws_bedrock.py         # AWS Bedrock adapter
│   ├── anthropic.py           # Anthropic Messages API adapter
│   ├── gemini.py              # Gemini API and Vertex AI adapters
│   ├── cohere.py              # Cohere adapter
│   ├── perplexity.py          # Perplexity adapter
│   ├── ollama_cloud.py        # Ollama cloud adapter
│   └── oci_genai.py           # OCI GenAI adapter
│
├── tools/                     # Mediated, policy-gated tool implementations
│   ├── browser/               # Web automation (Playwright)
│   ├── mcp/                   # MCP server bridge
│   └── ...                    # Additional tool categories
│
├── workflows/                 # Workflow packs (use-case-specific)
│   ├── base.py                # Abstract workflow base
│   ├── coding/                # Planner/executor/verifier
│   ├── research/              # Gatherer/summarizer/reporter
│   ├── documents/             # Indexer/retriever/answerer
│   ├── file_organization/     # Analyzer/proposer/applier
│   ├── docs_maintenance/      # Detector/updater/aligner
│   ├── github_maintenance/    # Summarizer/drafter
│   └── command_assistant/     # Parser/generator
│
├── memory/                    # Three-tier memory system
│   ├── brain.py               # Unified orchestrator
│   ├── episodic.py            # Timeline-based memory
│   ├── semantic.py            # Concept graph memory
│   ├── embeddings.py          # Vector embedding engine
│   ├── bus.py                 # Cross-process memory bus
│   ├── registry.py            # Memory backend registry
│   └── tiers/                 # Working, global memory
│
├── interfaces/                # User-facing interfaces
│   ├── cli/                   # Command-line interface
│   ├── api_server/            # FastAPI REST server
│   ├── web_ui/                # Web dashboard
│   ├── desktop_ui/            # pywebview desktop wrapper with tkinter/browser fallback
│   └── guided_tui/            # Interactive terminal UI
│
├── presets/                   # Beginner-friendly preset definitions
│   ├── base.py
│   ├── codebase_assistant.py
│   ├── research_report.py
│   ├── local_document_chat.py
│   ├── file_organizer.py
│   ├── docs_maintainer.py
│   ├── github_maintainer.py
│   └── command_assistant.py
│
├── federation/                # Distributed agent coordination
├── marketplace/               # Plugin marketplace
├── multimodal/                # Vision model support
├── monitoring/                # Metrics and health reporting
├── config/                    # Configuration loading
├── tests/                     # Full test suite
├── docs/                      # Documentation (you are here)
├── scripts/                   # Tooling (directive checks, validation helpers, legacy checks)
└── skills/                    # Optional local helpers; not part of the repo baseline
```

---

## Core Runtime

The core runtime (`core/`) is the heart of the system. It is intentionally **generic** — it knows nothing about specific providers, workflows, tools, or models.

### Key Components

| Component | File | Responsibility |
|-----------|------|---------------|
| **WorkflowRunner** | `workflow_runner.py` | Executes DAGs in topological order, parallel groups, retry logic |
| **RunLedger** | `ledger.py` | Append-only event log with SHA-256 hash chain verification |
| **PolicyEngine** | `policy_engine.py` | Evaluates allow/deny/ask decisions for every tool call |
| **ToolRegistry** | `tool_protocol.py` | Mediates all tool invocations through the policy engine |
| **ModelRegistry** | `model_registry.py` | Resolves capability-based model bindings |
| **CapabilityRegistry** | `capability_registry.py` | Discovers and registers workflows, presets, and memory backends |

### Provider Profiles

AI provider setup is owned by `config/` and consumed by the generic model registry. Provider profiles store non-secret provider metadata, role/model bindings, capability tags, and secret refs. Raw provider secrets live in the OS keychain or encrypted vault; `.env` provider loading is not part of runtime config.

`core/model_registry.py` stays generic. It receives resolved `AgentModelConfig` objects and lazy-loads provider adapters by descriptor.
| **Event** | `events.py` | Structured event schema (20+ types) with UUID, sequence, hash |
| **ArtifactStore** | `artifact_store.py` | Produces and validates 15+ run artifacts |
| **ContextPacker** | `context_packer.py` | Legacy context packer kept for compatibility; ContextOps/AICtx is the active path |
| **RetryEngine** | `retry_engine.py` | Bounded retry with exponential backoff per error category |
| **StepBudgetEnforcer** | `step_budget.py` | Enforces token, time, and iteration budgets |
| **CascadingRouter** | `cascading_router.py` | Model failover with health tracking |
| **PrivacyEnforcer** | `privacy_enforcer.py` | Enforces privacy modes at the policy level |
| **ApprovalWorkflow** | `approval_workflow.py` | Manages approval gates with ledger events |

### Runtime Phases

The generic runtime defines phases in `core/state_machine.py`, but not every production path uses that abstract phase list directly. In particular:

- `workflows/coding/workflows/coding.py` delegates real execution to `workflows/coding/runtime.py`
- `workflows/context_maintainer/workflow.py` delegates to `workflows/context_maintainer/runtime.py`

Treat the state machine as the generic runtime model and the dedicated runtimes as the concrete execution paths for those workflows.

---

## Subsystems

### Provider Layer (`providers/`)

Provider adapters are lazy-loaded and interchangeable. They implement the abstract `ModelProvider` protocol and are never imported eagerly — the registry loads them via `importlib` only when a configured model needs one.

**Current adapter implementations in code:**
- `openai_v1` — OpenAI and all OpenAI-compatible APIs (Grok, Ollama, LM Studio, etc.)
- `azure_foundry` — Azure AI Foundry / Azure OpenAI
- `aws_bedrock` — AWS Bedrock
- `anthropic` — Anthropic Messages API
- `gemini` / `vertex_ai` — Google Gemini API and Vertex AI
- `cohere` — Cohere
- `perplexity` — Perplexity
- `ollama_cloud` — Ollama Cloud
- `oci_genai` — Oracle Cloud Infrastructure GenAI

### Tool Layer (`tools/`)

All tools are mediated through `ToolRegistry.invoke()`, which routes through the `PolicyEngine` for allow/deny/ask decisions. Tools declare their risk level (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), and the policy engine enforces approval thresholds.

**Notable tools:**
- **Browser tool** — Web automation via Playwright with session reuse
- **MCP bridge** — Connects to MCP servers at runtime
- **Filesystem, Shell, Git** — Standard developer tools (path-bounded)

### Workflow Layer (`workflows/`)

Workflow packs define agent roles, step DAGs, prompts, policies, and verification logic. Most workflow-facing code stays behind `core.public_api`, but that boundary is not perfectly enforced across the whole repository. Some interface and runtime modules still import selected lower-level modules directly.

### Memory Layer (`memory/`)

Three-tier memory with multiple backends:
- **Working memory** — ephemeral, run-scoped
- **Episodic memory** — timeline-based, bounded growth, importance scoring
- **Semantic memory** — concept graph with deduplication

Backends: JSONL, SQLite, Vector (embeddings).

### Interface Layer (`interfaces/`)

Multiple interfaces all backed by the same core runtime:
- **CLI** (`interfaces/cli/`) — Primary user surface via `agentheim` command
- **API Server** (`interfaces/api_server/`) — FastAPI REST + WebSocket
- **Web UI** (`interfaces/web_ui/`) — Browser dashboard
- **Desktop UI** (`interfaces/desktop_ui/`) — pywebview wrapper over the Web UI with tkinter and browser fallback
- **Guided TUI** (`interfaces/guided_tui/`) — Interactive prompt-based wizard

---

## Architectural Laws

The active repository baseline is intentionally smaller than earlier doctrine stacks. The core architectural rule is still the same: keep `core/` generic and keep concrete provider, workflow, and tool behavior in their own layers.

One intentional exception remains: `core/model_registry.py` contains a `DEFAULT_PROVIDER_MAP` convenience default. The `ModelRegistry` class itself still accepts any `provider_map` and remains generic.

---

## Boundary Rules

### Import Rules

| Module | May Import From | May NOT Import From |
|--------|----------------|-------------------|
| `core/` | `core.*`, `providers.base`, `workflows.base` | Concrete provider adapters, workflow packs, tool implementations, AICtx implementation logic |
| `workflows/` | `core.public_api`, `workflows.base` | Concrete provider adapters |
| `providers/` | `providers.base` | Unnecessary coupling to sibling provider adapters |
| `tools/` | `core.tool_protocol`, `core.public_api` | Unreviewed cross-tool coupling |
| `interfaces/` | Prefer `core.public_api`; current code still has targeted direct imports in maintained paths | New direct dependencies on unstable `core.*` internals without justification |

### Forbidden Patterns

- Provider-specific logic in `core/`
- Workflow-specific logic in `core/`
- Direct tool execution bypassing `tool_protocol`
- Mutable global state
- Importing concrete implementations into `core/`
- Skipping policy engine for tool calls
- Modifying ledger events after append

---

## Ownership Model

Every directory has an implied subsystem owner. Cross-boundary changes must explain the impact and preserve the rules in `.github/instructions/`.

| Directory | Owner |
|-----------|-------|
| `core/` | Runtime Team |
| `providers/` | Provider Team |
| `tools/` | Tool Team |
| `workflows/` | Workflow Team |
| `memory/` | Memory Team |
| `interfaces/` | Interface Team |
| `presets/` | Product Team |
| `config/` | Platform Team |
| `tests/` | Quality Team |
| `docs/` | Documentation Team |
| `.github/instructions/` | Project governance |
| `.github/agents/` | Agent definitions |

---

## Support States and Promotion Criteria

Every exposed subsystem carries one support state. States are not cosmetic labels; they are architectural commitments about what the project promises and what evidence backs the promise.

| State | Meaning | Promotion Gate |
| --- | --- | --- |
| Stable | Reliable default path; safe for first-run docs | Unit tests, smoke tests, docs, current validation evidence, troubleshooting coverage |
| Beta | Intended for real use, known limits documented | Unit tests, smoke tests, docs, at least one live path, documented limits |
| Experimental | Useful but not baseline-critical | Import/unit coverage, explicit limits, hidden from first-run path |
| Internal | Implementation detail; not a user promise | Owner subsystem tests only |

### Promotion Criteria Per Subsystem

To advance a subsystem from one state to the next, the following must be present and current:

1. **Owner** — which team or subsystem owns the surface (see Ownership Model above).
2. **Entrypoints** — exact CLI commands, API routes, Web UI paths, or programmatic APIs a user touches.
3. **Security model** — how auth, policy, approval, privacy, and redaction apply to this surface.
4. **Docs** — user-facing docs in `docs/USER_GUIDE.md`, `docs/API_REFERENCE.md`, or `docs/TROUBLESHOOTING.md` that describe the surface and its limits.
5. **Tests** — unit tests for logic, smoke tests for integration, and where applicable live tests against real providers.
6. **Live evidence** — current, non-contradictory evidence that the surface works end-to-end with a real provider or endpoint.
7. **Known limits** — documented gaps, failure modes, and unsupported paths.

The canonical matrix lives in [`docs/SUPPORT_MATRIX.md`](SUPPORT_MATRIX.md). This section exists to make the promotion path explicit in architecture terms, not to duplicate the matrix.

### First-Run Path Protection

Experimental surfaces must not appear in:
- CLI `Getting Started` help panel
- Web UI dashboard default views
- API first-run documentation
- `doctor` first-class lane checks

They may remain available under `Advanced` panels, `--all` flags, or explicit opt-in routes.

---

## See Also

- [Repository Baseline](../.github/instructions/01-doctrine.md) — binding architectural boundaries
- [Working Rules](../.github/instructions/02-forbidden-behaviors.md) — editing and verification expectations
