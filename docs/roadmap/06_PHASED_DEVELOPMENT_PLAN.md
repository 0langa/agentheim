# 06 — PHASED DEVELOPMENT PLAN
## Strict Phase Gates, Dependency Ordering, Implementation Prerequisites

**Status:** DERIVED FROM 00_PROJECT_DOCTRINE  
**Enforcement:** No agent may implement systems from a phase not yet unlocked.  
**Violation Classification:** ARCHITECTURAL BREACH (Level 3)  
**Last Updated:** 2026-05-10 — Post-Phase 6 audit rewrite

---

## 1. Phase Overview

The project proceeds through eight strictly ordered phases. Phases 0-6 are **functionally complete** (features exist and pass tests). Phase 7 addresses **production-hardening gaps** discovered during the Phase 6 audit. Phase 8 tracks **future expansion** beyond the current roadmap.

```
PHASE 0: FOUNDATION (Cleanup & Invariants) ✅
    |
    v
PHASE 1: CORE RUNTIME (Generic Engine) ✅ (with gaps)
    |
    v
PHASE 2: FIRST WORKFLOW PACK (Coding Workflow) ✅
    |
    v
PHASE 3: TOOL & SAFETY SYSTEM (Mediated Tools + Policy) ✅ (with gaps)
    |
    v
PHASE 4: PRESET SYSTEM & CLI (User Surface) ✅
    |
    v
PHASE 5: EXPANSION (Additional Workflows, Providers, Memory) ✅
    |
    v
PHASE 6: ADVANCED SYSTEMS (MCP, UI, Distributed) ✅
    |
    v
PHASE 7: PRODUCTION HARDENING (Audit gaps, foundational debt)
    |
    v
PHASE 8: FUTURE EXPANSION (IDE, CI/CD, Formal Verification)
```

**Legend:**  
- `✅` = Phase complete (features built, tests pass)  
- `✅ (with gaps)` = Phase complete in terms of shipped features, but foundational subsystems specified in the roadmap are missing or incomplete  
- `🔒` = Locked until previous phase gates pass

---

## 2. Honest Audit Summary

A full codebase audit against roadmap docs 00-18 was conducted on 2026-05-10. Key findings:

### What IS Done (418 tests passing)
- Core runtime is genuinely generic (no hardcoded providers/workflows/tools in `core/`)
- 7 workflow packs with end-to-end execution tests
- Tool protocol + policy engine + registry + risk levels
- Preset system (7 presets) + CLI + guided TUI
- Memory system (JSONL, SQLite, vector backends, 103 tests)
- MCP integration with persistent connection pool
- Browser tool with session reuse + async variant
- API server (execution, SSE/WebSocket streaming, metrics, OpenAPI)
- Web UI + Desktop UI scaffold
- Distributed workers (HTTP transport) + federation
- Vision models (OpenAI GPT-4o, Claude 3)
- Self-improving hooks + monitoring (Prometheus)
- Secret redaction, path confinement, command classification

### What Is MISSING (foundational gaps)
- **Ledger integrity:** No SHA-256 hash chain, no `ledger.hash`, no replay, no resume
- **Event sourcing:** No `core/events.py`; events are ad-hoc dicts, not structured schema
- **Approval workflow:** MEDIUM/HIGH tools auto-allowed in non-interactive mode; no 6-field disclosure prompt
- **Core runtime files:** `workflow_runner.py`, `error_classification.py`, `retry_engine.py`, `step_budget.py`, `artifact_store.py`, `context_packer.py`, `agent_protocol.py`, `events.py` — all missing
- **Public API:** No `core/public_api.py`; interfaces import directly from internals
- **Provider lazy loading:** `providers/__init__.py` eagerly imports all concrete providers
- **Parallel execution:** Flags exist but no engine; `Workflow.run()` is purely sequential
- **Privacy enforcer:** No `PrivacyMode` enum or `PrivacyEnforcer` class
- **Model registry:** No cascading router, fallback chains, or auto-failover

These gaps are catalogued in detail in the per-phase "As-Built" sections below and will be addressed in **Phase 7**.

---

## 3. Phase 0: FOUNDATION ✅

### 3.1 Objective
Clean the existing codebase, enforce architectural invariants, and establish the core directory structure.

### 3.2 As-Built
| Deliverable | Status | Notes |
|-------------|--------|-------|
| Directory structure matches canonical spec | ✅ | `core/`, `providers/`, `tools/`, `workflows/`, `memory/`, `interfaces/`, `presets/`, `config/`, `tests/`, `docs/`, `scripts/` all exist |
| `core/` contains only generic code | ✅ | Grep audit confirms no concrete provider/workflow/tool imports in `core/` |
| `providers/` contains all provider adapters | ✅ | 4 provider adapters exist |
| `workflows/coding/` exists as first workflow pack | ✅ | Coding workflow extracted from core |
| `tools/` has base protocol and registry | ✅ | `ToolProtocol`, `BaseTool`, `ToolRegistry` in `core/tool_protocol.py` |
| Import rules enforced | ⚠️ | Custom script (`scripts/roadmap-check.py`) provides some coverage, but crashes on Windows encoding errors; no dedicated import linter |
| CI pipeline enforces architecture | ⚠️ | CI runs architecture check but does not enforce import boundaries strictly |

### 3.3 Exit Gate
**GATE 0.1:** ✅ All provider-specific logic removed from `core/`  
**GATE 0.2:** ✅ All workflow-specific logic removed from `core/`  
**GATE 0.3:** ✅ Directory structure matches canonical specification  
**GATE 0.4:** ⚠️ CI enforces architectural boundaries (partial — script is brittle)  
**GATE 0.5:** ⚠️ Import linting passes on all modules (partial — no dedicated linter)  
**GATE 0.6:** ✅ ModelRegistry is fully generic

---

## 4. Phase 1: CORE RUNTIME ✅ (with gaps)

### 4.1 Objective
Build the generic execution engine that powers all workflow packs.

### 4.2 As-Built
| Deliverable | Status | Notes |
|-------------|--------|-------|
| Workflow runner with DAG execution | ⚠️ | `workflows/base.py` has `Workflow.run()` but it is a **sequential for-loop** with no retries, no resumption, no parallel execution. No `core/workflow_runner.py` exists. |
| Agent protocol with message schemas | ⚠️ | `AgentMessage` exists in `core/schemas.py`. `AgentRequest`, `AgentResponse`, `AgentContext` are **missing**. No `core/agent_protocol.py`. |
| Model registry with capability resolution | ⚠️ | `core/model_registry.py` filters by capability but has no cascading router, fallback chains, or auto-failover. |
| Provider registry with lazy loading | ❌ | No `core/provider_registry.py`. `providers/__init__.py` eagerly imports all concrete providers at startup. |
| Tool protocol with mediated invocation | ✅ | `core/tool_protocol.py` — `ToolProtocol`, `BaseTool`, `ToolRegistry`, `ToolContext`, `ToolResult` all implemented |
| Policy engine with decision types | ✅ | `core/policy_engine.py` — `allow`/`deny`/`ask`/`boundary`/`budget` decisions implemented |
| Run ledger with append-only events | ⚠️ | `core/ledger.py` writes JSONL files but has **no hash chain, no index, no checkpoints, no replay**. Events are ad-hoc dicts, not structured schema. |
| Artifact store with structured output | ❌ | No `core/artifact_store.py`. `RunLedger` writes files directly without schema management. |
| Capability registry | ✅ | `core/capability_registry.py` — registration and discovery of workflows, presets, providers |
| Context packer | ❌ | No `core/context_packer.py`. `core/repo/context_pack.py` exists but does not produce `context_bundle.md` + `context_manifest.json`. |
| Config loader with validation | ✅ | `config/config.py` — YAML/JSON config loading with validation |
| Error classification | ❌ | No `core/error_classification.py`. `core/errors.py` only defines exception classes. No TRANSIENT/RECOVERABLE/VERIFICATION/CONFIGURATION/PERMISSION/FATAL taxonomy. |
| Retry engine | ❌ | No `core/retry_engine.py`. No bounded retry or backoff anywhere. |
| Step budget enforcement | ⚠️ | `StepBudget` model exists on `Step` but is **not enforced** during workflow execution. `ToolBudget` is checked by `PolicyEngine` but no unified step-budget enforcement. |
| Phase machine | ⚠️ | `core/state_machine.py` implements all 14 phases correctly, but file is named `state_machine.py` instead of `phase_machine.py`. No resume logic wired to `RESUME_AVAILABLE`. |
| Event system | ❌ | No `core/events.py`. No structured event types. Events are informal dicts. |

### 4.3 Exit Gate
**GATE 1.1:** ⚠️ Core unit tests exist but coverage is ~76% (not >80%)  
**GATE 1.2:** ⚠️ Integration tests pass for core interactions that exist; missing subsystems untested  
**GATE 1.3:** ✅ Phase machine executes full lifecycle without errors  
**GATE 1.4:** ❌ Ledger replay produces identical state — **no replay function exists**  
**GATE 1.5:** ✅ Policy engine correctly evaluates all decision types  
**GATE 1.6:** ❌ Provider registry lazy-loads — **eager imports in `providers/__init__.py`**  
**GATE 1.7:** ⚠️ Model registry resolves capabilities correctly (basic filtering only)  
**GATE 1.8:** ❌ Budget enforcement halts runs cleanly — **budgets declared but not enforced during execution**

---

## 5. Phase 2: FIRST WORKFLOW PACK ✅

### 5.1 Objective
Implement the coding workflow as the first workflow pack. Validate that the core runtime is genuinely generic.

### 5.2 As-Built
| Deliverable | Status | Notes |
|-------------|--------|-------|
| Coding workflow definition | ✅ | `workflows/coding/` — full workflow with agents, steps, policies |
| Orchestrator agent | ✅ | Planning agent with structured output |
| Executor agent | ✅ | Code generation agent |
| Verifier agent | ✅ | Verification agent with test execution |
| Patching logic | ✅ | File modification with diff generation |
| Test execution | ✅ | Run tests, capture results |
| Report generation | ✅ | Final report artifact (`final_report.md` + `final_report.json`) |
| Workflow-level policies | ✅ | Coding-specific policy rules |
| Verification logic | ✅ | Pass/fail criteria for code changes |

### 5.3 Exit Gate
**GATE 2.1:** ✅ Coding workflow executes end-to-end  
**GATE 2.2:** ❌ Workflow uses only public core APIs — **workflows import `core.model_registry`, `core.ledger`, `core.policy_engine` directly**  
**GATE 2.3:** ✅ All workflow artifacts generated correctly  
**GATE 2.4:** ✅ Policy engine enforces workflow-specific policies  
**GATE 2.5:** ✅ Verifier correctly evaluates code changes  
**GATE 2.6:** ❌ Run is fully replayable from ledger — **no replay function**  
**GATE 2.7:** ❌ Core has zero code changes due to workflow integration — **workflows mutate `core.capability_registry` on import**

---

## 6. Phase 3: TOOL & SAFETY SYSTEM ✅ (with gaps)

### 6.1 Objective
Implement the complete tool system with mediated invocation, safety policies, and approval workflows.

### 6.2 As-Built
| Deliverable | Status | Notes |
|-------------|--------|-------|
| Filesystem tool | ✅ | Read, write, list, stat with path boundaries |
| Shell tool | ✅ | Execute with allowlist/denylist + command classification (SAFE/INSTALL/DESTRUCTIVE/DEPLOY) |
| Git tool | ✅ | Clone, diff, commit, status |
| HTTP tool | ✅ | Request with network policy enforcement |
| Memory tool | ✅ | Read/write structured memory |
| Tool registry | ✅ | Registration and discovery |
| Approval workflow | ❌ | **No actual approval UI flow.** MEDIUM risk auto-allowed in non-interactive mode. No 6-field disclosure prompt. |
| Risk classification | ✅ | None/Low/Medium/High/Critical levels |
| Path confinement | ✅ | Filesystem scoped to declared boundaries; path traversal blocked |
| Network confinement | ✅ | No network by default, policy-gated |
| Secret redaction | ✅ | Secrets removed from all logs/artifacts BEFORE model context packing |

### 6.3 Exit Gate
**GATE 3.1:** ✅ All tools pass through policy engine  
**GATE 3.2:** ✅ Path confinement prevents directory escape  
**GATE 3.3:** ✅ Shell command classification works correctly  
**GATE 3.4:** ❌ Approval workflow functions for all risk levels — **MEDIUM auto-allowed, no human-in-the-loop**  
**GATE 3.5:** ✅ Secret redaction removes sensitive data from artifacts  
**GATE 3.6:** ✅ Network policy blocks unauthorized outbound requests  
**GATE 3.7:** ✅ Tool registry discovers and registers all tools

---

## 7. Phase 4: PRESET SYSTEM & CLI ✅

### 7.1 Objective
Build the user-facing surface: presets that hide complexity and a CLI that serves all three user layers.

### 7.2 As-Built
| Deliverable | Status | Notes |
|-------------|--------|-------|
| Preset base class | ✅ | Schema, validation, defaults |
| Codebase Assistant preset | ✅ | Inspect → plan → patch → test → report |
| Local Document Chat preset | ✅ | Index → answer → cite |
| Research Report preset | ✅ | Gather → summarize → compare → report |
| File Organizer preset | ✅ | Analyze → propose → preview → apply |
| CLI with preset picker | ✅ | Guided preset selection via `agentheim` CLI |
| CLI with power-user flags | ✅ | Model, privacy, approval overrides |
| Doctor command | ✅ | System diagnostics and verification |
| Default configuration | ✅ | Sensible defaults for all settings |
| Beginner-friendly output | ✅ | Plain language, progress indicators |

### 7.3 Exit Gate
**GATE 4.1:** ✅ Beginner can launch a preset with 3 inputs or fewer  
**GATE 4.2:** ✅ Power-user can override all relevant settings via CLI  
**GATE 4.3:** ✅ Doctor script diagnoses common issues  
**GATE 4.4:** ✅ All presets produce complete artifact sets  
**GATE 4.5:** ✅ Preset selection requires no technical knowledge  
**GATE 4.6:** ⚠️ Configuration is portable (export/import) — partial, no formal export/import CLI command

---

## 8. Phase 5: EXPANSION ✅

### 8.1 Objective
Expand the platform with additional workflow packs, providers, memory backends, and the guided TUI.

### 8.2 As-Built
| Deliverable | Status | Notes |
|-------------|--------|-------|
| Documents workflow | ✅ | Index, retrieve, answer, cite |
| Research workflow | ✅ | Gather, summarize, compare, report |
| File organization workflow | ✅ | Analyze, propose, preview, apply |
| Docs maintenance workflow | ✅ | Detect stale, update, align |
| GitHub maintenance workflow | ✅ | Summarize issues, draft PRs |
| Command assistant workflow | ✅ | Parse intent, generate safe commands |
| Guided TUI | ✅ | Terminal-native preset picker with rich components |
| Additional memory backends | ✅ | JSONL, SQLite, Vector backends; 103 memory tests |
| Vector retrieval | ✅ | Chroma integration |

### 8.3 Exit Gate
**GATE 5.1:** ✅ 6 workflow packs implemented and tested beyond coding  
**GATE 5.2:** ✅ Guided TUI provides beginner-friendly experience  
**GATE 5.3:** ✅ Memory system functional with 3 backends (JSONL, SQLite, Vector)  
**GATE 5.4:** ✅ All workflow packs produce complete artifacts  
**GATE 5.5:** ✅ Platform is usable by non-technical users

---

## 9. Phase 6: ADVANCED SYSTEMS ✅

### 9.1 Objective
Implement advanced subsystems: MCP, browser, UIs, distributed workers, multimodal, self-improving, federation.

### 9.2 As-Built
| Priority | Subsystem | Path | Status | Notes |
|----------|-----------|------|--------|-------|
| P1 | MCP integration | `tools/mcp/` | ✅ | Persistent connection pool, tool discovery, stdio JSON-RPC transport |
| P1 | Browser tool | `tools/browser/` | ✅ | Session reuse, multi-step workflows, async variant |
| P2 | Local DB tool | `tools/local_db/` | ✅ | SQLite operations |
| P2 | Web UI | `interfaces/web_ui/` | ✅ | Execution, SSE/WebSocket streaming, dashboard |
| P3 | Desktop UI | `interfaces/desktop_ui/` | ✅ | Minimal scaffold around Web UI |
| P3 | API server | `interfaces/api_server/` | ✅ | Execution, streaming, metrics, real health checks, OpenAPI spec |
| P4 | Distributed workers | `workflows/distributed/` | ✅ | HTTP transport (coordinator + client), task scheduler |
| P4 | Plugin marketplace | `marketplace/` | ✅ | Sandbox wired, signature verification |
| P5 | Monitoring | `monitoring/` | ✅ | MetricsCollector wired into RunExecutor, Prometheus endpoint |
| P5 | Self-improving agents | `agents/self_improving/` | ✅ | Feedback capture, prompt evolution, parameter tuning, tool selection strategies |
| P5 | Cross-modal capabilities | `multimodal/` | ✅ | OpenAIVisionProcessor, ClaudeVisionProcessor |
| P5 | Federated agent networks | `federation/` | ✅ | HTTP transport, peer discovery, task delegation |

### 9.3 Exit Gate
**GATE 6.1:** ✅ MCP integration functional  
**GATE 6.2:** ✅ Browser tool operational  
**GATE 6.3:** ✅ Web UI prototype  
**GATE 6.4:** ✅ API server with OpenAPI spec  
**GATE 6.5:** ✅ Desktop UI scaffold  
**GATE 6.6:** ✅ Distributed worker protocol defined

---

## 10. Phase 7: PRODUCTION HARDENING 🔒

### 10.1 Objective
Close foundational gaps discovered in the Phase 6 audit. This phase does **not** add new user-facing features; it makes existing features robust, secure, and compliant with the original architectural specification.

### 10.2 Unlock Criteria
- ALL Phase 6 exit gates passed ✅
- Audit report completed and accepted ✅

### 10.3 Unlocked Subsystems

| Priority | Subsystem | Path | Gap From |
|----------|-----------|------|----------|
| P1 | Event-sourced ledger | `core/ledger.py` | Doc 11 — hash chain, replay, resume |
| P1 | Core runtime files | `core/` | Doc 03 — missing modules |
| P1 | Public API facade | `core/public_api.py` | Doc 02 — interface boundary |
| P2 | Approval workflow | `interfaces/cli/` + `core/policy_engine.py` | Doc 10 — human-in-the-loop |
| P2 | Provider lazy loading | `providers/` | Doc 08 — eager import breach |
| P2 | Workflow isolation | `workflows/` | Doc 05 — direct core imports |
| P3 | Parallel execution | `core/workflow_runner.py` | Doc 15 — sequential-only runner |
| P3 | Privacy enforcer | `core/policy_engine.py` | Doc 18 — no PrivacyMode/PrivacyEnforcer |
| P3 | Model fallback chains | `core/model_registry.py` | Doc 08 — no cascading router |
| P4 | Agent protocol | `core/agent_protocol.py` | Doc 14 — missing schemas |
| P4 | Context packer | `core/context_packer.py` | Doc 12 — missing artifact generation |
| P4 | Eight standard roles | `config/config.py` | Doc 14 — 4 of 8 roles defined |

### 10.4 Deliverables

| Deliverable | Owner | Prerequisites | Exit Criteria |
|-------------|-------|--------------|---------------|
| Ledger hash chain + indexing | Runtime Team | Phase 6 | SHA-256 chain, `ledger.hash`, `ledger.index`, checkpointing |
| Deterministic replay + resume | Runtime Team | Phase 6 | `reconstruct_state()`, `apply_event()`, CLI `resume` replays and continues |
| Structured event schema | Runtime Team | Phase 6 | `core/events.py` with 20+ event types, sequence numbers, parent references |
| `core/workflow_runner.py` | Runtime Team | Phase 6 | Generic DAG runner with retries, resumption, parallel group execution |
| `core/error_classification.py` | Runtime Team | Phase 6 | TRANSIENT/RECOVERABLE/VERIFICATION/CONFIGURATION/PERMISSION/FATAL taxonomy |
| `core/retry_engine.py` | Runtime Team | Phase 6 | Bounded retry with exponential backoff, integrated into workflow runner |
| `core/step_budget.py` | Runtime Team | Phase 6 | Budget enforcement before every agent invocation and tool call |
| `core/artifact_store.py` | Runtime Team | Phase 6 | Schema-managed artifact directory producing all 11 required files |
| `core/context_packer.py` | Runtime Team | Phase 6 | Produces `context_bundle.md` + `context_manifest.json` per run |
| `core/agent_protocol.py` | Runtime Team | Phase 6 | `AgentRequest`, `AgentResponse`, `AgentContext` schemas |
| `core/public_api.py` | Architecture Lead | Phase 6 | Stable facade; all interfaces import ONLY from this module |
| Approval workflow UI | Interface Team | Phase 6 | MEDIUM/HIGH tools pause for human approval with 6 required disclosure fields |
| Provider lazy loading | Provider Team | Phase 6 | `providers/__init__.py` has no eager imports; string-based resolution |
| Workflow pack isolation | Workflow Team | Phase 6 | Workflows use only `core.public_api`; no direct core internals |
| Parallel execution engine | Runtime Team | Phase 6 | `ResourceLock`, workspace isolation, concurrency limits, `parallel_groups()` integrated |
| `PrivacyMode` + `PrivacyEnforcer` | Security Team | Phase 6 | 4-mode enum, enforcer class, integrated into policy engine |
| Cascading model router | Provider Team | Phase 6 | Cost-aware selection, fallback chains, auto-failover |

### 10.5 Explicitly NOT in Phase 7
- New workflow packs
- New tools (beyond hardening existing ones)
- New providers
- New UIs (beyond approval workflow)
- New memory backends
- IDE extensions, CI/CD integration, formal verification

### 10.6 Exit Gate
**GATE 7.1:** Ledger is tamper-evident (SHA-256 hash chain) + replayable — `ledger.hash`, `reconstruct_state()`, replay tests pass  
**GATE 7.2:** Resume from interruption works end-to-end — CLI `resume` loads checkpoint, replays events, continues execution  
**GATE 7.3:** All missing core runtime files exist and tested — `workflow_runner.py`, `error_classification.py`, `retry_engine.py`, `step_budget.py`, `artifact_store.py`, `events.py`, `agent_protocol.py`, `context_packer.py`  
**GATE 7.4:** Interfaces import ONLY from `core.public_api` — `core/public_api.py` exists; grep shows zero direct imports in `interfaces/`  
**GATE 7.5:** Provider lazy loading enforced — `providers/__init__.py` has no eager imports; providers loaded only when configured  
**GATE 7.6:** Approval workflow with 6-field disclosure — MEDIUM/HIGH tools pause for human approval with Action description, Risk explanation, Scope, Reversibility, Alternatives, Policy reference

---

## 11. Phase 8: FUTURE EXPANSION 🔒

### 11.1 Objective
Extend the platform beyond the original six-phase roadmap with new integrations, interfaces, and research areas.

### 11.2 Unlock Criteria
- ALL Phase 7 exit gates passed
- Architecture Lead approval

### 11.3 Unlocked Subsystems

| Priority | Subsystem | Path | Source |
|----------|-----------|------|--------|
| P2 | IDE Extensions | `interfaces/ide/` | Former doc 19 — VS Code, JetBrains, Neovim |
| P2 | CI/CD Integration | `interfaces/ci/` | Former doc 19 — GitHub Actions, GitLab CI, Azure DevOps |
| P3 | AICtx Context Intelligence | `integrations/aictx/` | Former doc 19 — Context compilation, project scanning |
| P4 | Formal Verification | `research/formal/` | Former doc 19 — SMT solvers, property-based testing |
| P5 | Advanced Monitoring | `monitoring/advanced/` | Former doc 19 — eBPF (Linux), ETW (Windows) |

### 11.4 Exit Gate
**GATE 8.1:** IDE extension provides inline agent assistance in at least one editor  
**GATE 8.2:** CI/CD integration triggers Agentheim runs from pipeline configuration  
**GATE 8.3:** Formal verification proves correctness for a non-trivial critical path  

---

*End of 06_PHASED_DEVELOPMENT_PLAN.md*
