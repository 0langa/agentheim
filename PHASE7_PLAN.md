# Phase 7: Production Hardening — Implementation Plan

**Status:** Unlocked  
**Derived from:** `docs/roadmap/06_PHASED_DEVELOPMENT_PLAN.md`  
**Last updated:** 2026-05-10

---

## 0. Goal

Close all foundational gaps discovered in the 2026-05-10 audit. No new user-facing features. Make existing features robust, secure, and compliant with the original architectural specification.

**Success criteria:** All 6 Phase 7 exit gates pass.

---

## 1. Logical Slices

Phase 7 is split into **6 slices** that build on each other. Each slice has a clear deliverable set, entry criteria, and exit criteria. Slices are ordered by dependency — do not skip.

```
Slice 1: Event Foundation
    |
    v
Slice 2: Runtime Engine
    |
    v
Slice 3: Artifacts & Protocols
    |
    v
Slice 4: Boundaries & Loading
    |
    v
Slice 5: Safety & Privacy
    |
    v
Slice 6: Advanced Routing & Resume
```

---

## 2. Slice 1: Event Foundation

**Goal:** Replace ad-hoc dict events with a structured, typed event schema and make the ledger tamper-evident.

**Entry criteria:** Phase 6 complete ✅

### 2.1 Deliverables

| # | File / Component | What to build |
|---|------------------|---------------|
| 1.1 | `core/events.py` | Structured event schema: `Event` dataclass with `event_id` (UUID), `sequence` (monotonic int), `timestamp`, `event_type` (enum), `run_id`, `step_id`, `agent_id`, `tool_id`, `phase`, `payload` (dict), `metadata` (dict), `parent_event_id` (optional). 20+ event type constants: `RUN_INITIATED`, `CONFIG_LOADED`, `PHASE_TRANSITION`, `AGENT_INVOKED`, `TOOL_CALLED`, `POLICY_EVALUATED`, `BUDGET_CHECKED`, `ARTIFACT_CREATED`, `CONTEXT_PACKED`, `RUN_COMPLETED`, `RUN_FAILED`, `RUN_RESUMED`, etc. |
| 1.2 | `core/ledger.py` — Hash chain | Add `previous_hash: str` field to every event. Compute SHA-256 of serialized event (minus its own hash field). Write `ledger.hash` file with chain verification helper `verify_chain()` → returns `(bool, list[str])` of broken links. |
| 1.3 | `core/ledger.py` — Indexing | Add `ledger.index` file (JSON) mapping: `event_type → [sequence_nums]`, `phase → [sequence_nums]`, `agent_id → [sequence_nums]`, `tool_id → [sequence_nums]`, `step_id → [sequence_nums]`. Helper `query_index(event_type=None, phase=None, agent_id=None, tool_id=None, step_id=None) → list[Event]`. |
| 1.4 | `core/ledger.py` — Checkpoints | Add `checkpoints/` directory under run dir. Save full reconstructed state as JSON every N events (default 100), at phase boundaries, and on user approval. Helper `save_checkpoint(state, sequence_num)` and `load_last_checkpoint() → (state, sequence_num)`. |
| 1.5 | `core/ledger.py` — Unified ledger | Merge scattered `tool_calls.jsonl`, `state_transitions.jsonl`, `patch_attempts.jsonl` into single `ledger.jsonl` using the new `Event` schema. Backward-compat shim for existing code that reads old files. |

### 2.2 Tests
- `tests/test_events.py` — Event schema validation, serialization, deserialization
- `tests/test_ledger_hash.py` — Hash chain integrity, tamper detection, verification
- `tests/test_ledger_index.py` — Index creation, query by event_type/phase/agent_id/tool_id/step_id
- `tests/test_ledger_checkpoints.py` — Checkpoint save/load, state reconstruction accuracy

### 2.3 Exit criteria
- [ ] `core/events.py` exists with all 20+ event types
- [ ] Every run produces a single `ledger.jsonl` with structured events
- [ ] `ledger.hash` verifies the chain; tampering is detected
- [ ] `ledger.index` enables fast lookup by all 5 dimensions
- [ ] `checkpoints/` contains periodic state snapshots
- [ ] All ledger tests pass

---

## 3. Slice 2: Runtime Engine

**Goal:** Build the generic DAG execution engine that the roadmap specified but never created. Replace the sequential `for` loop in `workflows/base.py`.

**Entry criteria:** Slice 1 complete (event schema stable, ledger can record engine events)

### 3.1 Deliverables

| # | File / Component | What to build |
|---|------------------|---------------|
| 2.1 | `core/error_classification.py` | Enum `ErrorCategory`: `TRANSIENT`, `RECOVERABLE`, `VERIFICATION`, `CONFIGURATION`, `PERMISSION`, `FATAL`. Function `classify_error(exc: Exception) → ErrorCategory`. Strategy map: TRANSIENT → exponential backoff + provider switch; RECOVERABLE → retry with modified prompt; VERIFICATION → enter FIX_LOOP (bounded); CONFIGURATION → halt + report; PERMISSION → log + request approval; FATAL → halt + preserve state. |
| 2.2 | `core/retry_engine.py` | `RetryEngine` class: `execute_with_retry(fn, max_retries=3, backoff=2.0, error_category=ErrorCategory.TRANSIENT) → Result`. Integrates with `error_classification.py`. Logs retry attempts as events. Respects step budget. |
| 2.3 | `core/step_budget.py` | `StepBudgetEnforcer` class: `check_budget(context: StepContext, operation: str) → bool`. Enforces `max_tokens`, `max_time_seconds`, `max_tool_calls`, `max_agent_invocations` BEFORE every agent invocation and tool call. Emits `BUDGET_CHECKED` event on every check. Emits `BUDGET_EXCEEDED` and halts cleanly when any limit hit. |
| 2.4 | `core/workflow_runner.py` | `WorkflowRunner` class: `run(workflow: Workflow, repo_root: Path, metadata: dict) → list[StepResult]`. Features: (a) Execute DAG in topological order, (b) Honor `parallel_safe` flags — execute `parallel_groups()` concurrently using `ThreadPoolExecutor`, (c) Honor `workspace_isolation` — create isolated workspace dirs per agent, (d) Integrate `RetryEngine` for step failures, (e) Integrate `StepBudgetEnforcer` before every step, (f) Emit events for every transition, (g) Catch exceptions → classify → retry or halt, (h) Produce final report + artifacts via `ArtifactStore`. |
| 2.5 | `workflows/base.py` — Refactor | Keep `Workflow` ABC, `ExecutionDAG`, `Step`, `StepContext`, `StepResult`. Remove `run()` method from `Workflow` — delegate to `WorkflowRunner`. Keep backward-compat shim `Workflow.run()` that calls `WorkflowRunner().run(self, ...)` with deprecation warning. |

### 3.2 Tests
- `tests/test_error_classification.py` — Classify all 6 error categories from real exceptions
- `tests/test_retry_engine.py` — Retry success, retry exhaustion, backoff timing, budget respect
- `tests/test_step_budget.py` — Budget checks before agent/tool calls, halt on exhaustion
- `tests/test_workflow_runner.py` — Sequential execution, parallel group execution, retry on failure, budget enforcement, event emission
- `tests/test_workflow_runner_parallel.py` — Parallel safety levels, workspace isolation, resource contention

### 3.3 Exit criteria
- [ ] `core/workflow_runner.py` exists and replaces sequential `Workflow.run()`
- [ ] Parallel groups execute concurrently when `parallel_safe=True`
- [ ] Failed steps retry according to error classification
- [ ] Budgets are checked before every agent invocation and tool call
- [ ] All workflow tests still pass (backward compatibility)
- [ ] New runtime engine tests pass

---

## 4. Slice 3: Artifacts & Protocols

**Goal:** Complete the missing artifact production and agent protocol schemas. Create the public API facade.

**Entry criteria:** Slice 2 complete (workflow runner produces results, events are structured)

### 4.1 Deliverables

| # | File / Component | What to build |
|---|------------------|---------------|
| 3.1 | `core/artifact_store.py` | `ArtifactStore` class: `create_run(run_id, workflow_id, preset_id) → Path`. Produces ALL required artifacts: `run.json`, `timeline.jsonl`, `ledger.jsonl`, `ledger.index`, `ledger.hash`, `checkpoints/`, `config.redacted.json`, `context_bundle.md`, `context_manifest.json`, `plan.md`, `tool_calls.jsonl`, `policy_decisions.jsonl`, `patch.diff`, `verification.json`, `final_report.md`. Schema validation for each artifact. Helper `validate_completeness(run_dir) → list[str]` of missing artifacts. |
| 3.2 | `core/context_packer.py` | `ContextPacker` class: `pack(repo_root, run_config, tool_registry) → (context_bundle_md: str, context_manifest_json: dict)`. Scans repo, summarizes files, fits within model context window, redacts secrets, produces human-readable `context_bundle.md` + machine-readable `context_manifest.json`. Logs `CONTEXT_PACKED` event. |
| 3.3 | `core/agent_protocol.py` | `AgentMessage`, `AgentRequest`, `AgentResponse`, `AgentContext` dataclasses. `AgentMessage`: `role`, `content`, `metadata`. `AgentRequest`: `agent_id`, `messages`, `tools`, `context`. `AgentResponse`: `content`, `tool_calls`, `usage`, `finish_reason`. `AgentContext`: `run_id`, `step_id`, `repo_root`, `tools`, `policy`, `ledger`, `working_memory`, `prior_results`. |
| 3.4 | `core/public_api.py` | Stable facade exposing ONLY these symbols: `WorkflowRunner`, `RunLedger`, `PolicyEngine`, `ToolRegistry`, `ModelRegistry`, `CapabilityRegistry`, `Event`, `AgentRequest`, `AgentResponse`, `AgentContext`, `ContextPacker`, `ArtifactStore`, `ErrorCategory`, `RetryEngine`, `StepBudgetEnforcer`, `ToolContext`, `ToolResult`, `ToolSchema`, `BaseTool`, `AsyncBaseTool`. No internal modules exposed. |

### 4.2 Tests
- `tests/test_artifact_store.py` — All 15 artifacts produced, schema validation, completeness check
- `tests/test_context_packer.py` — Bundle generation, manifest generation, secret redaction, context window fitting
- `tests/test_agent_protocol.py` — Schema validation, serialization, round-trip
- `tests/test_public_api.py` — All expected symbols exported, no internal modules leaked

### 4.3 Exit criteria
- [ ] Every run produces all 15 required artifacts with correct schemas
- [ ] `context_bundle.md` + `context_manifest.json` are generated per run
- [ ] `core/agent_protocol.py` has all 4 schemas
- [ ] `core/public_api.py` exists and exposes only stable symbols
- [ ] All artifact/protocol tests pass

---

## 5. Slice 4: Boundaries & Loading

**Goal:** Fix the architectural boundary violations discovered in the audit.

**Entry criteria:** Slice 3 complete (`core/public_api.py` exists with stable interface)

### 5.1 Deliverables

| # | File / Component | What to build |
|---|------------------|---------------|
| 4.1 | `providers/__init__.py` — Lazy loading | Remove all eager imports. Replace with `PROVIDER_METADATA` dict mapping provider_id → module_path string. `create_provider(provider_id: str) → ModelProvider` uses `importlib.import_module()` + `getattr()` to load only when configured. `list_providers() → list[str]` returns IDs only (no class loading). |
| 4.2 | `workflows/` — Isolation refactor | Replace all direct imports from `core.model_registry`, `core.ledger`, `core.policy_engine`, `core.tool_protocol`, `core.run_executor`, `core.capability_registry` with imports from `core.public_api`. Refactor `register_workflow()` to not mutate global registry on import — use explicit registration call from CLI/API bootstrap instead. |
| 4.3 | `interfaces/` — Public API only | Replace all direct imports from `core.*` internals with imports from `core.public_api`. Update `interfaces/cli/cli.py`, `interfaces/api_server/app.py`, `interfaces/web_ui/app.py`, `interfaces/desktop_ui/app.py`, `interfaces/guided_tui/app.py`. |
| 4.4 | `scripts/roadmap-check.py` — Import linting | Add AST-based import check: scan all `interfaces/` files — any import NOT from `core.public_api` is a Level 3 breach. Scan `workflows/` files — any import from `core.` internals (except `core.public_api`) is a Level 3 breach. Scan `providers/__init__.py` — any eager concrete import is a Level 3 breach. |

### 5.2 Tests
- `tests/test_provider_lazy_loading.py` — `import providers` does not load concrete classes; `create_provider()` loads only the requested one
- `tests/test_workflow_isolation.py` — Workflow packs use only `core.public_api`; no direct core internals
- `tests/test_interface_isolation.py` — All interface files import only from `core.public_api`
- `tests/test_import_linting.py` — `roadmap-check.py` catches violations correctly

### 5.3 Exit criteria
- [ ] `providers/__init__.py` has zero eager imports
- [ ] `create_provider()` loads only the requested provider
- [ ] All workflow packs import only from `core.public_api`
- [ ] All interfaces import only from `core.public_api`
- [ ] `roadmap-check.py` enforces import boundaries in CI
- [ ] All boundary tests pass

---

## 6. Slice 5: Safety & Privacy

**Goal:** Make the approval workflow real and add privacy enforcement.

**Entry criteria:** Slice 4 complete (boundaries clean, public API stable)

### 6.1 Deliverables

| # | File / Component | What to build |
|---|------------------|---------------|
| 5.1 | `core/policies.py` — Approval workflow | `ApprovalWorkflow` class: `request_approval(decision: PolicyDecision, tool_id: str, params: dict, context: ToolContext) → ApprovalResult`. In CLI mode: prints 6 required fields (Action description, Risk explanation, Scope, Reversibility, Alternatives, Policy reference) and waits for `y/n` input. In API mode: returns ` ApprovalResult(status="pending", token=uuid)` and stores pending approval in memory. In Web UI mode: emits WebSocket message requesting approval. Records approval/denial in ledger as `POLICY_EVALUATED` event. |
| 5.2 | `core/policy_engine.py` — Audit trail | After every `evaluate()` call, write the full `PolicyDecision` to ledger as a `POLICY_EVALUATED` event including: `tool_id`, `params_hash`, `decision`, `reason`, `policy_id`, `override` (bool). |
| 5.3 | `core/policy_engine.py` — `allow+log` | Add `"allow_log"` as a valid action in risk rules. `NONE → allow`, `LOW → allow_log` (auto-execute + ledger event), `MEDIUM → ask`, `HIGH → ask` (with reason field), `CRITICAL → deny`. |
| 5.4 | `core/privacy.py` | `PrivacyMode` enum: `REMOTE_ALLOWED`, `LOCAL_PREFERRED`, `LOCAL_ONLY`, `STRICT_PRIVATE`. `PrivacyEnforcer` class with methods: `can_use_remote_model(mode) → bool`, `can_use_remote_fallback(mode) → bool`, `can_make_network_request(mode) → bool`, `can_upload_file(mode) → bool`. Integrated into `PolicyEngine.evaluate()` as the first two checks (before budget/path/command/network). |

### 6.2 Tests
- `tests/test_approval_workflow.py` — CLI approval prompt contains all 6 fields, `y` allows, `n` denies, timeout defaults to deny
- `tests/test_policy_audit.py` — Every policy decision is recorded in ledger
- `tests/test_privacy_enforcer.py` — All 4 modes enforce correct restrictions
- `tests/test_allow_log.py` — LOW risk tools execute + emit ledger event without prompting

### 6.3 Exit criteria
- [ ] MEDIUM/HIGH tools pause for human approval with 6-field disclosure
- [ ] Every policy decision is recorded in ledger
- [ ] `PrivacyMode` enum + `PrivacyEnforcer` exist and are integrated
- [ ] All safety/privacy tests pass

---

## 7. Slice 6: Advanced Routing & Resume

**Goal:** Add model cascading/fallback and end-to-end resume from interruption.

**Entry criteria:** Slices 1-5 complete (events, runner, artifacts, boundaries, safety all stable)

### 7.1 Deliverables

| # | File / Component | What to build |
|---|------------------|---------------|
| 6.1 | `core/model_registry.py` — Cascading router | `CascadingRouter` class: `resolve(agent_role, capabilities, budget, privacy_mode) → ModelBinding`. Sorts candidates by cost (cheapest first). Attempts primary → on failure, marks degraded → bounded retry → switches to fallback chain. Logs every attempt as `AGENT_INVOKED` event. Maintains health cache (60s TTL). Cold standby local model (Ollama/LM Studio) for zero-dependency operation. |
| 6.2 | `core/model_registry.py` — Fallback chains | Add `fallback_chain: list[str]` to `ModelBinding`. `resolve()` returns primary + fallback chain. `CascadingRouter` walks the chain on failure. |
| 6.3 | `interfaces/cli/cli.py` — Resume command | `agentheim resume <run_id>` loads last checkpoint → reconstructs state via `reconstruct_state()` → replays events after checkpoint → validates workspace → re-checks budgets → continues execution from current phase. Emits `RUN_RESUMED` event. |
| 6.4 | `core/ledger.py` — Replay | `reconstruct_state(events: list[Event]) → RunState`. Deterministic state reducer: applies each event in sequence to build current state. Used by resume and for debugging. |

### 7.2 Tests
- `tests/test_cascading_router.py` — Primary success, primary failure → fallback, budget exhaustion, privacy mode filtering, health cache TTL
- `tests/test_fallback_chains.py` — Chain walk on failure, chain exhaustion handling
- `tests/test_resume.py` — Interrupt mid-run, resume reconstructs exact state, does not re-execute completed steps, continues from current phase
- `tests/test_replay.py` — Same event sequence produces identical state; non-deterministic outputs (model responses) captured in events and replayed exactly

### 7.3 Exit criteria
- [ ] Model registry uses cost-aware cascading router with fallback chains
- [ ] Auto-failover works end-to-end (primary fails → fallback succeeds)
- [ ] Resume from interruption reconstructs state and continues execution
- [ ] Replay produces identical state for same event sequence
- [ ] All routing/resume tests pass

---

## 8. Phase 7 Exit Gates (Final Validation)

After all 6 slices are complete, verify:

| Gate | Requirement | Evidence |
|------|-------------|----------|
| **7.1** | Ledger is tamper-evident + replayable | `ledger.hash` verifies; `reconstruct_state()` tested; tamper detection works |
| **7.2** | Resume from interruption works end-to-end | CLI `resume <run_id>` loads checkpoint, replays events, continues execution |
| **7.3** | All missing core runtime files exist and tested | `workflow_runner.py`, `error_classification.py`, `retry_engine.py`, `step_budget.py`, `artifact_store.py`, `events.py`, `agent_protocol.py`, `context_packer.py` all exist with >80% coverage |
| **7.4** | Interfaces import ONLY from `core.public_api` | `grep -r "from core\." interfaces/` returns only `core.public_api` imports |
| **7.5** | Provider lazy loading enforced | `providers/__init__.py` has no eager imports; `create_provider()` loads only requested provider |
| **7.6** | Approval workflow with 6-field disclosure | MEDIUM/HIGH tools pause for human approval with Action description, Risk explanation, Scope, Reversibility, Alternatives, Policy reference |

---

## 9. File Inventory

### New files to create

| File | Slice | Purpose |
|------|-------|---------|
| `core/events.py` | 1 | Structured event schema |
| `core/error_classification.py` | 2 | Error taxonomy |
| `core/retry_engine.py` | 2 | Bounded retry with backoff |
| `core/step_budget.py` | 2 | Budget enforcement |
| `core/workflow_runner.py` | 2 | Generic DAG execution engine |
| `core/artifact_store.py` | 3 | Schema-managed artifact directory |
| `core/context_packer.py` | 3 | Context bundle + manifest generation |
| `core/agent_protocol.py` | 3 | Agent message schemas |
| `core/public_api.py` | 3 | Stable facade for interfaces |
| `core/privacy.py` | 5 | PrivacyMode + PrivacyEnforcer |
| `tests/test_events.py` | 1 | Event schema tests |
| `tests/test_ledger_hash.py` | 1 | Hash chain tests |
| `tests/test_ledger_index.py` | 1 | Index tests |
| `tests/test_ledger_checkpoints.py` | 1 | Checkpoint tests |
| `tests/test_error_classification.py` | 2 | Error taxonomy tests |
| `tests/test_retry_engine.py` | 2 | Retry engine tests |
| `tests/test_step_budget.py` | 2 | Budget enforcement tests |
| `tests/test_workflow_runner.py` | 2 | Runner tests |
| `tests/test_workflow_runner_parallel.py` | 2 | Parallel execution tests |
| `tests/test_artifact_store.py` | 3 | Artifact completeness tests |
| `tests/test_context_packer.py` | 3 | Context packing tests |
| `tests/test_agent_protocol.py` | 3 | Agent protocol tests |
| `tests/test_public_api.py` | 3 | Public API facade tests |
| `tests/test_provider_lazy_loading.py` | 4 | Lazy loading tests |
| `tests/test_workflow_isolation.py` | 4 | Workflow boundary tests |
| `tests/test_interface_isolation.py` | 4 | Interface boundary tests |
| `tests/test_import_linting.py` | 4 | Import linting tests |
| `tests/test_approval_workflow.py` | 5 | Approval workflow tests |
| `tests/test_policy_audit.py` | 5 | Policy audit trail tests |
| `tests/test_privacy_enforcer.py` | 5 | Privacy enforcement tests |
| `tests/test_allow_log.py` | 5 | Allow+log action tests |
| `tests/test_cascading_router.py` | 6 | Model routing tests |
| `tests/test_fallback_chains.py` | 6 | Fallback chain tests |
| `tests/test_resume.py` | 6 | Resume from interruption tests |
| `tests/test_replay.py` | 6 | Deterministic replay tests |

### Files to modify

| File | Slice | Change |
|------|-------|--------|
| `core/ledger.py` | 1 | Add hash chain, indexing, checkpoints, unified ledger |
| `workflows/base.py` | 2 | Remove `run()` method; delegate to `WorkflowRunner` |
| `providers/__init__.py` | 4 | Remove eager imports; add string-based lazy loading |
| `workflows/*/agents/*.py` | 4 | Replace direct `core.*` imports with `core.public_api` |
| `workflows/*/__init__.py` | 4 | Remove eager `register_workflow()` on import |
| `interfaces/cli/cli.py` | 4, 6 | Use `core.public_api`; implement real `resume` command |
| `interfaces/api_server/app.py` | 4 | Use `core.public_api` |
| `interfaces/web_ui/app.py` | 4 | Use `core.public_api` |
| `interfaces/desktop_ui/app.py` | 4 | Use `core.public_api` |
| `interfaces/guided_tui/app.py` | 4 | Use `core.public_api` |
| `core/policy_engine.py` | 5 | Add approval workflow integration, audit trail, `allow+log`, privacy checks |
| `core/model_registry.py` | 6 | Add cascading router, fallback chains |
| `scripts/roadmap-check.py` | 4 | Add AST-based import boundary checks |
| `CHANGELOG.md` | All | Append per-slice entries |
| `devtest/all-test-commands.md` | All | Add new test paths |

---

## 10. Estimated Scope

| Slice | New files | Modified files | Est. lines | Est. tests |
|-------|-----------|----------------|------------|------------|
| 1: Event Foundation | 2 | 1 | ~400 | ~25 |
| 2: Runtime Engine | 4 | 1 | ~600 | ~35 |
| 3: Artifacts & Protocols | 4 | 0 | ~400 | ~20 |
| 4: Boundaries & Loading | 1 | 10 | ~300 | ~15 |
| 5: Safety & Privacy | 1 | 1 | ~400 | ~20 |
| 6: Advanced Routing & Resume | 0 | 3 | ~300 | ~20 |
| **Total** | **12** | **16** | **~2,400** | **~155** |

**Timeline estimate:** If implemented sequentially by one agent, ~2-3 weeks of focused work. If parallelized (multiple agents on independent slices), ~1-2 weeks.

---

*End of Phase 7 Implementation Plan*
