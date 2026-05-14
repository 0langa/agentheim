# Catch-up plan for weak spots — prio based

## P0 — Complete live AI validation

Finish the live-ai-testing matrix before declaring any surface stable.

### 1. Close preset live-test gaps

#### Why
`research-report` and `codebase-assistant` presets are known-failing or deferred in [`live-ai-testing.md`](live-ai-testing.md). These are core user-facing surfaces.

#### Actions
- Fix `research-report` AICtx pipeline crash (`prepare_model_transfer` path).
- Run `research-report` end-to-end against test repo with Azure.
- Run `codebase-assistant` preset end-to-end with Azure.
- Verify CLI `report` and `resume` follow-up commands work for both.

#### Done when
- Both presets pass live-ai-testing matrix.
- `report --run-id` and `resume --run-id` succeed for both.

---

### 2. Complete CLI live surface

#### Why
Several CLI commands and flags have zero live verification. They appear stable in code and pytest, but real AI invocation paths are unproven.

#### Actions
- `run --no-tests` — full happy path with real AI, verify planner/coder/verifier still run and tests are recorded as skipped.
- `memory --model-id <id> --key ... --value ...` — scoped read/write round-trip.
- `mcp-call <server> <tool>` — with a mock MCP server config.
- `guided` — interactive preset picker live (not scripted stdin); verify routing to selected preset.
- Add missing `copy` CLI command or explicitly document absence.

#### Done when
- Every CLI command in Tier-1 journeys has live invocation evidence.

---

### 3. Execute workflow deep paths live

#### Why
Many workflow failure guards and edge paths only have unit tests, no live AI verification. The coding workflow in particular has guards that have never fired against a real model.

#### Actions
- **Coding**: dirty repo block (`allow_dirty=False`), patch rollback on apply failure, verifier failure fix loop, max total tasks guard (>20), max diff guard, API `POST /api/workflows/coding/execute`.
- **File organization**: missing source file per-move reporting, unsafe/impossible moves recorded as failed.
- **Command assistant**: unsafe command request returns `safe=false`.
- **Documents**: binary/excluded dirs skipped, empty repo handling.
- **Docs maintenance**: aligner returns `AlignmentResult`, `apply` mode writes changed docs.
- **All workflows**: every `POST /api/workflows/{name}/execute` endpoint exercised live.

#### Done when
- Every workflow guard and API execute path has live evidence.

---

### 4. Complete tool live matrix

#### Why
Several tools have unit tests but no live invocation record. Tool registry promises capability; live matrix must confirm it.

#### Actions
- **Browser**: fetch page + screenshot against real URL.
- **HTTP**: GET/POST against httpbin or similar.
- **Local DB**: SQLite ops with a configured DB.
- **MCP**: tool invocation with a configured mock server.
- **Network**: diagnostics live.

#### Done when
- Every tool in registry has at least one live invocation record.

---

### 5. Close Web UI and Desktop live gaps

#### Why
Web UI tested via `TestClient`; Desktop only import-checked. Real browser execution missing for most surfaces.

#### Actions
- Start Desktop UI, verify it loads web UI and routes correctly.
- Web UI live execute for coding, research, documents, file-organization, docs-maintenance, github-maintenance.
- Web UI preset run for research-report, local-document-chat, file-organizer, docs-maintainer, github-maintainer.
- Verify run status polling displays completed/failed state + artifacts/errors.

#### Done when
- Every Tier-1 journey works through Web UI and Desktop with real AI.

---

### 6. Run safety negative cases live

#### Why
Safety paths confirmed by pytest, but live AI failure modes (auth, rate limit, timeout, bad output) are untested.

#### Actions
- Missing provider secret → clear actionable error.
- Invalid model ID → model not found error.
- Auth failure → surfaced to caller, not swallowed.
- Rate limit / quota → retry 3x then clear error.
- Network timeout → retry 3x then surfaced.
- Provider empty content → treated as failure where required.
- Provider non-JSON response → repair path triggers, then fails cleanly.
- Coder patch outside allowed files → blocked by `PatchApplier` scope.

#### Done when
- Every safety failure produces documented, actionable error.

---

### 7. Verify adapters live

#### Why
`WebResearchAdapter`, `GitHubCliAdapter`, `MCPClientAdapter` have unit tests but zero live verification.

#### Actions
- **WebResearchAdapter**: live search query with DDG or urllib fallback.
- **GitHubCliAdapter**: live issue view against real repo.
- **MCPClientAdapter**: connect to configured MCP server, list tools, invoke one.

#### Done when
- All three adapters have live invocation evidence.

---

### 8. Complete vision deferred suite

#### Why
Vision capability declared in provider profiles but never live-tested end-to-end.

#### Actions
- Azure vision deployment with `gpt-4.1`.
- `multimodal.image` tool `describe` with real PNG base64.
- `multimodal.image` tool `ocr` with real text image.
- Non-vision model rejects image request with clear error.
- API `POST /api/tools/multimodal.image/invoke` with live vision.

#### Done when
- Vision path works end-to-end on at least one provider.

---

### 9. Run devtest validation gates

#### Why
DevTest runner modes not executed this round. Gates must pass before any claim of readiness.

#### Actions
- `run-devtest.ps1 -Mode directive -NoPrompt`
- `run-devtest.ps1 -Mode targeted`
- `ai_test.ps1` (max 2 consecutive runs, 120s timeout each)

#### Done when
- All three gates pass.

---

## P1 — Must fix first

These unblock almost everything else.

### 1. Reduce promise surface to match real product depth

#### Why
Biggest systemic risk. Repo exposes many areas — [`federation/`](federation), [`marketplace/`](marketplace), [`multimodal/`](multimodal), broad preset surface in [`presets/__init__.py`](presets/__init__.py:5) — but not all should carry same product promise.

#### Actions
- Add support-state matrix to [`README.md`](README.md) and [`docs/README.md`](docs/README.md:8)
  - Stable
  - Beta
  - Experimental
  - Internal
- Label every workflow, preset, interface, provider lane, advanced subsystem.
- Remove experimental subsystems from first-run docs/help.
- Create readiness checklist per subsystem:
  - owner
  - entrypoints
  - docs complete
  - smoke tests
  - e2e tests
  - security model
  - known limits

#### Done when
- every exposed surface has explicit status
- no unlabeled subsystem in docs/help
- default user path shows only stable/beta surfaces

---

### 2. Freeze core interface contract

#### Why
CLI/API/UI breadth high. Contract drift becomes support nightmare. Main surfaces visible in [`interfaces/cli/cli.py`](interfaces/cli/cli.py:49) and [`create_api_app()`](interfaces/api_server/app.py:260).

#### Actions
- Define Tier-1 user journeys only:
  - setup + doctor
  - add provider + ping model
  - inspect + plan
  - run preset
  - resume/report
- Build contract matrix:
  - capability
  - CLI command
  - API route
  - UI support
  - auth requirement
  - schema/output
  - docs
  - tests
- Freeze core API routes from [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md:63):
  - [`/api/health`](docs/API_REFERENCE.md:67)
  - [`/api/tools`](docs/API_REFERENCE.md:75)
  - [`/api/workflows`](docs/API_REFERENCE.md:93)
  - [`/api/presets`](docs/API_REFERENCE.md:117)
  - [`/api/runs/{run_id}`](docs/API_REFERENCE.md:198)
  - [`/api/runs/{run_id}/stream`](docs/API_REFERENCE.md:205)
  - key ctx routes covered in [`tests/api_server/test_ctx_routes.py`](tests/api_server/test_ctx_routes.py)
- Mark all other routes beta/experimental unless proven otherwise.

#### Done when
- every Tier-1 journey mapped across CLI/API/docs/tests
- stable API surface explicitly frozen
- no "stable" route without contract test

---

### 3. Narrow provider onboarding to first-class lanes

#### Why
Provider sprawl high in [`DEFAULT_PROVIDER_MAP`](core/model_registry.py:68). Adoption suffers if setup story too broad.

#### Actions
- Choose only 3 first-class provider lanes:
  - OpenAI-compatible
  - Azure Foundry/OpenAI
  - local/self-hosted OpenAI-compatible
- Mark rest advanced/manual.
- For each first-class lane, create setup scorecard:
  - install reqs
  - secret/config path
  - add command
  - assign command
  - doctor output
  - ping-models expected output
  - common failures
- Standardize error messages around known failure classes from [`tests/test_provider_profiles.py`](tests/test_provider_profiles.py) and lazy-loading behavior from [`TestProviderLazyLoading`](tests/test_provider_lazy_loading.py:14).

#### Done when
- top 3 providers have copy-paste guides
- rest clearly marked advanced
- provider setup failures map to documented fixes

---

### 4. Productize run diagnostics and observability

#### Why
Observability exists but fragmented. Strong underlying basis: ledger, metrics endpoint [`/api/metrics`](interfaces/api_server/app.py:735), policy events, error classification.

#### Actions
- Define canonical run summary schema using ledger/event truth:
  - run_id
  - workflow/preset
  - status
  - duration
  - provider/model by role
  - tool counts
  - approval events
  - verification result
  - artifacts
  - failure category
- Make same run summary available in:
  - CLI report path
  - API run route
  - web UI detail view
- Add failed-run diagnostics bundle:
  - final report
  - state transitions
  - policy events
  - tool calls
  - redacted error summary
  - next-step guidance
- Map error categories to fixes via [`classify_error()`](core/public_api.py:50) and [`PolicyEngine.evaluate()`](core/policy_engine.py:77).

#### Done when
- CLI/API/UI show same run truth
- every failed run gets actionable classification
- troubleshooting can start from run summary, not raw artifacts

---

## P2 — Next highest leverage

These deepen product quality after P1 removes systemic ambiguity.

### 5. Bring non-coding workflows up to coding standard

#### Why
Coding path strongest by evidence in [`run_task()`](workflows/coding/runtime.py:369). Other workflows likely lag in depth/consistency.

#### Actions
- Use coding workflow as benchmark.
- Audit:
  - [`workflows/documents/runtime.py`](workflows/documents/runtime.py:40)
  - [`workflows/docs_maintenance/runtime.py`](workflows/docs_maintenance/runtime.py:146)
  - [`workflows/command_assistant/runtime.py`](workflows/command_assistant/runtime.py:31)
- Compare on:
  - input/output clarity
  - artifacts
  - verification strategy
  - retry/resume behavior
  - failure messages
  - docs
  - smoke tests
  - negative tests
- Raise each to minimum bar:
  - structured input/output
  - documented artifacts
  - documented failures
  - golden-path test
  - negative-path test
  - example in docs
- Assign workflow tiers:
  - product-ready
  - usable with limits
  - experimental

#### Done when
- at least 3 non-coding workflows meet minimum bar
- every exposed preset maps to tiered workflow status

---

### 6. Simplify CLI information architecture

#### Why
CLI surface broad. Good for power users, bad for discoverability.

#### Actions
- Refactor top-level help in [`interfaces/cli/cli.py`](interfaces/cli/cli.py:49)
  - keep only user-critical commands top-level
  - group advanced/experimental commands
- Align help output with Tier-1 journeys.
- Ensure CLI smoke coverage for user-critical commands, using evidence in [`tests/smoke/test_cli.py`](tests/smoke/test_cli.py).

#### Done when
- new user can discover core path from help alone
- experimental paths not mixed into primary commands

---

### 7. Add interface parity tests

#### Why
Stable contract needs evidence. API tests already broad in [`tests/test_api_server.py`](tests/test_api_server.py); web UI tests in [`tests/test_web_ui.py`](tests/test_web_ui.py); CLI smoke in [`tests/smoke/test_cli.py`](tests/smoke/test_cli.py).

#### Actions
- Add parity suite for Tier-1 journeys:
  - CLI result
  - API result
  - optional UI visibility
- Add preset parity checks against [`PRESET_REGISTRY`](presets/__init__.py:3).
- Add auth/approval parity checks where behavior should align.

#### Done when
- same action yields consistent result across stable interfaces
- regressions caught by parity tests, not user reports

---

### 8. Publish support and troubleshooting catalog

#### Why
Once support matrix + providers + diagnostics exist, users need one place to resolve failures fast.

#### Actions
- Expand [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) with failure catalog:
  - provider auth/config failure
  - policy denial
  - privacy restriction
  - budget exceeded
  - path confinement/sandbox violation
  - missing context/AICtx stale state
- Link CLI/API messages to troubleshooting entries.
- Include expected outputs and recovery steps.

#### Done when
- top recurring failures have exact remediation path
- docs match actual runtime messages

---

## P3 — Important, but after stability layer solid

### 9. Formalize subsystem ownership and promotion criteria

#### Why
Need durable governance for broad repo.

#### Actions
- Assign owner per subsystem based on boundaries in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md:283).
- Define promotion rules:
  - Experimental → Beta
  - Beta → Stable
- Require docs + tests + operator guidance before promotion.

#### Done when
- promotion no longer subjective
- each subsystem has accountable maintainer

---

### 10. Decide marketplace/federation/distributed scope explicitly

#### Why
These areas expensive. Should not drift forward by inertia.

#### Actions
- Review test/documentation/product evidence for:
  - federation/distributed tests in [`tests/test_federation_transport.py`](tests/test_federation_transport.py) and [`tests/test_distributed_transport.py`](tests/test_distributed_transport.py)
  - marketplace security posture in [`docs/SAFETY.md`](docs/SAFETY.md:197)
- Decide one of:
  - keep experimental
  - cut from public story
  - invest to beta with explicit acceptance criteria

#### Done when
- advanced subsystems have explicit roadmap state
- no ambiguous semi-supported area remains

---

### 11. Improve UI/operator experience after contract stabilizes

#### Why
UI polish matters, but after stable behavior exists.

#### Actions
- Use canonical run summary and Tier-1 journeys to improve web/desktop UI.
- Make UI consume stable routes only.
- Expose run diagnostics, provider health, workflow tiers.

#### Done when
- UI becomes thin reliable layer over stable contract
- no UI-only behavior divergence

---

## P4 — Nice later, not catch-up critical

### 12. Expand stable provider/workflow surface
Only after P0/P1/P2 complete.

### 13. Advanced dashboards/analytics
Only after canonical diagnostics schema complete.

### 14. New presets/subsystems
Only after existing exposed surfaces have clear support state and test backing.

---

# Recommended execution order

1. Complete live AI validation (P0)
2. Support-state matrix and surface reduction (P1)
3. Core interface contract freeze (P1)
4. Narrow provider onboarding to 3 first-class lanes (P1)
5. Canonical run diagnostics/reporting (P1)
6. Non-coding workflow hardening (P2)
7. Simplify CLI (P2)
8. Add parity tests (P2)
9. Improve troubleshooting catalog (P2)
10. Formalize ownership (P3)
11. Decide advanced subsystem scope (P3)
12. Polish UI/operator experience (P3)

# Short version

If want ultra-short prio stack:
- P0: finish live AI testing (presets, CLI, workflows, tools, Web UI, safety, adapters, vision, devtest gates)
- P1: reduce promise, freeze interfaces, narrow providers, unify diagnostics
- P2: harden non-coding workflows, simplify CLI, add parity tests, improve troubleshooting
- P3: formalize ownership, decide advanced subsystem scope, polish UI
- P4: expand again only after stability proven
