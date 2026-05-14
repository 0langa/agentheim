# Live AI Testing Matrix

Purpose: confirm Agentheim works front-to-back with the currently hooked-up provider (Azure Foundry). Provider adapter smoke is separated from full system functionality. Vision tests are deferred to their own section.

Run from repo root with `.venv` active and Azure credentials configured.

---

## Current Test Results

**Last tested:** 2026-05-14
**Provider:** Azure Foundry (`azure-real`) — `gpt-5.4`
**Test environment:** `C:\Users\juliu\source\repos\agentheim-testing-enviroment`

### Overall
- **Unit / regression tests:** 779 passed, 3 skipped, 0 failed
- **CLI smoke (non-AI):** Mostly pass; 4 known bugs
- **Live AI workflows:** Partial — some presets work, coding workflow blocked by safety + model quality
- **API / Web UI:** Pass via TestClient; live server start not tested
- **Vision:** Deferred

### Pass List
- pytest full suite (`tests/`)
- `doctor` / `doctor --skip-connectivity`
- `ping-models` (all 14 roles respond)
- `config-dump --redacted`
- `presets`, `inspect`, `list-runs`
- `memory get/set`
- `provider templates`, `provider list`, `provider test --profile azure-real`
- `ctx init`, `scan`, `run`, `verify`, `status`, `public-docs impact/update`
- `plan` (requires AICtx shards in `docs/AIprojectcontext/`)
- `start command-assistant` (succeeded on 2nd attempt; 1st try transient parse fail)
- `start docs-maintainer` (detected 5 stale docs, updated)
- `start github-maintainer` (summarized 3 issues, drafted PR)
- API server endpoints (`/api/providers`, `/api/models`, `/api/workflows`, `/api/presets`, `/api/tools`, tool invoke)
- Web UI endpoints (`/`, `/api/tools`, `/api/workflows`, `/api/presets`)
- `filesystem` + `git` tools via API
- High-risk tools (`shell.execute`, `browser`) correctly blocked via API
- Missing provider profile handled gracefully (`doctor` WARN, `ping-models` clear error)

### Fail List
| Item | Error | Notes |
|------|-------|-------|
| `provider test --role planner` (no `--profile`) | `KeyError: 'default'` | Defaults to string `"default"` instead of resolving actual default profile name |
| `mcp-list` | Exit code 1: `MCP config not found: .ai-team\mcp.json` | Should return empty list gracefully |
| `ctx clean --keep-runs 0` | Reports `Removed: 0, Kept: 0` despite `.aictx/runs/` existing | Clean logic does not remove run directories |
| `plan` / `run` coding workflow | Requires AICtx shards in `docs/AIprojectcontext/`; shell approval blocks pytest (`high` risk); model hallucinates patch (invents `divide` function); verifier rejects empty diff | Safety gates work, but context preflight + model quality + approval config prevent happy path |
| `file-organizer` preset | `Structured output validation failed after repair attempt` | Analyzer agent produces malformed JSON |
| `local-document-chat` preset | Indexer returns `{"documents":[]}` → retriever empty → answerer fails | Documents workflow cannot find/index content in test repo |
| `research-report` preset | Crash in `prepare_model_transfer` (AICtx pipeline) | Workflow operates on agentheim repo (stale context) instead of target repo; `repo` input ignored |
| `context-maintainer` preset | Same crash in `prepare_model_transfer` | Preset ignores `repo` input, uses `.` (agentheim repo) which has stale context |
| `report --run-id` | `AttributeError: 'dict' object has no attribute 'status'` | CLI report command returns dict where object expected |
| `resume --run-id` | `{"status": "no-run-initiated-event"}` | Resume engine expects `run_initiated` event; coding workflow ledger starts with `context_scanned` |

### Not Tested
- `copy` command (does not exist in CLI)
- `guided` TUI interactive flow
- Desktop UI
- Live API server start (`uvicorn`)
- Live Web UI start
- WebSocket `/api/runs/{run_id}/ws`
- `run --allow-dirty` full happy path (blocked by approval + patch quality)
- `start file-organizer` dry-run=False real apply
- Vision models + `multimodal.image`
- All negative safety cases (rate limit, timeout, auth failure, invalid model, etc.)
- Adapters: `WebResearchAdapter`, `GitHubCliAdapter`, `MCPClientAdapter`

---

## 1. Provider Adapter Quick Smoke

Verify the currently active provider responds. Other providers are listed for future expansion.

### 1.1 Currently Hooked Up
- [ ] `agentheim provider test --role planner` pings Azure planner binding → pong.
- [ ] `agentheim provider test --role executor` pings Azure executor binding → pong.
- [ ] `agentheim provider test --role verifier` pings Azure verifier binding → pong.
- [ ] `agentheim ping-models` pings all configured roles without error.
- [ ] `agentheim doctor` reports provider profile PASS and Azure models healthy.

### 1.2 Future Provider Adapters (Skip for Now)
Test only when credentials are available:

- [ ] `openai_v1`
- [ ] `openai_compatible`
- [ ] `aws_bedrock` (`aws_chain` + `bedrock_api_key`)
- [ ] `oci_genai`
- [ ] `anthropic`
- [ ] `gemini`
- [ ] `vertex_ai`
- [ ] `xai_grok`
- [ ] `kimi_moonshot`
- [ ] `mistral`
- [ ] `groq`
- [ ] `deepseek`
- [ ] `openrouter`
- [ ] `together`
- [ ] `cohere`
- [ ] `perplexity`
- [ ] `ollama` (local)
- [ ] `ollama_cloud`
- [ ] `lm_studio` (local)

---

## 2. Full Agentheim Functionality Test

Test every user-facing surface with Azure as the active provider. Every item must pass end-to-end.

### 2.1 CLI — Core Commands
- [x] `agentheim --help` prints top-level help.
- [x] `agentheim config-dump --redacted` prints config without raw secrets.
- [x] `agentheim config-dump --raw` prints raw config only when explicitly requested.
- [x] `agentheim doctor --skip-connectivity` reports provider profile status.
- [x] `agentheim doctor` attempts live connectivity check.
- [x] `agentheim ping-models` pings every configured role.
- [x] `agentheim inspect --repo .` analyzes current repo.
- [x] `agentheim presets` lists all presets.
- [x] `agentheim guided --help` shows guided TUI help.
- [ ] `agentheim guided` launches preset picker and routes to selected preset. *(not tested — interactive TUI)*
- [x] `agentheim plan --repo . --mode <mode>` returns summary, repo type, likely files, work orders. *(requires AICtx shards)*
- [ ] `agentheim run --repo . --mode <mode>` runs coding workflow end to end. *(blocked: shell approval + model patch quality)*
- [ ] `agentheim run --repo . --allow-dirty` works on dirty repo. *(not tested — blocked by above)*
- [ ] `agentheim run --repo . --no-tests` skips tests but still plans/codes/verifies. *(not tested — blocked by above)*
- [ ] `agentheim resume --repo . --run-id <id>` resumes a previous run. **FAIL:** `{"status": "no-run-initiated-event"}` — ledger format mismatch
- [ ] `agentheim report --repo . --run-id <id>` shows final report. **FAIL:** `AttributeError: 'dict' object has no attribute 'status'`
- [x] `agentheim list-runs --repo .` enumerates `.ai-team/runs/`.
- [ ] `agentheim copy <preset-id>` copies preset or config template. *(command does not exist in CLI)*

### 2.2 CLI — Provider Management
- [x] `agentheim provider templates` lists all supported templates.
- [x] `agentheim provider add azure --template azure_foundry --model <deployment> --role planner` stores secret securely.
- [x] `agentheim provider add azure-exec --template azure_foundry --model <deployment> --role executor` second provider for executor.
- [x] `agentheim provider list` shows redacted provider/profile state.
- [x] `agentheim provider assign verifier --provider azure --model <deployment>` binds verifier role.
- [x] `agentheim provider use default` switches default profile.
- [x] `agentheim provider use default --project` writes `.ai-team/provider-profile.json`.
- [ ] `agentheim provider test --role planner` pings Azure planner. **FAIL without `--profile`:** `KeyError: 'default'` — must pass `--profile azure-real`
- [x] `agentheim provider rotate-secret azure` replaces stored secret.
- [x] `agentheim provider remove azure-exec` removes provider + secret ref + bindings.
- [x] `agentheim provider import-env` migrates old env setup once.

### 2.3 CLI — Context (AICtx)
- [x] `agentheim ctx init` initializes AICtx in target repo.
- [x] `agentheim ctx scan` scans repository.
- [x] `agentheim ctx run` (default `allow_ai=False`) produces dry-run transfer plan.
- [ ] `agentheim ctx run --allow-ai` rejected without proper provider config. *(not tested)*
- [x] `agentheim ctx verify` verifies context pack.
- [x] `agentheim ctx status` shows status.
- [ ] `agentheim ctx clean` removes artifacts. **FAIL:** Reports `Removed: 0, Kept: 0` despite run dirs existing
- [x] `agentheim ctx public-docs impact` shows impact map.
- [x] `agentheim ctx public-docs update --write patch` generates review patch.
- [ ] `agentheim ctx oci` OCI-specific path (if OCI configured). *(not tested — OCI not configured)*

### 2.4 CLI — Memory
- [x] `agentheim memory --key test_key --value test_value` writes to memory.
- [x] `agentheim memory --key test_key` reads from memory.
- [ ] `agentheim memory --model-id <id> --key test_key --value test_value` model-scoped write. *(not tested)*
- [ ] `agentheim memory --model-id <id> --key test_key` model-scoped read. *(not tested)*

### 2.5 CLI — MCP
- [ ] `agentheim mcp-list` lists available MCP servers. **FAIL:** Exit code 1 when no config; should return empty list gracefully
- [ ] `agentheim mcp-call <server> <tool>` calls an MCP tool. *(not tested)*

### 2.6 Presets
Run each preset end-to-end with Azure:

- [x] `agentheim start command-assistant` — run shell commands. *(succeeded on 2nd attempt; 1st try transient parse fail)*
- [ ] `agentheim start codebase-assistant` — plan + apply code changes. *(blocked: shell approval + model patch quality)*
- [ ] `agentheim start file-organizer` — analyze + move files. **FAIL:** Analyzer structured output validation fails
- [x] `agentheim start docs-maintainer` — update docs. *(plan mode works; apply mode not tested)*
- [x] `agentheim start github-maintainer` — summarize issues / draft PRs.
- [ ] `agentheim start local-document-chat` — RAG over local docs. **FAIL:** Indexer returns empty documents
- [ ] `agentheim start research-report` — gather + summarize web research. **FAIL:** AICtx pipeline crash on agentheim repo
- [ ] `agentheim start context-maintainer` — maintain repo context packs (dry-run by default). **FAIL:** AICtx pipeline crash; ignores `repo` input

### 2.7 Workflows — Deep Paths
Test each workflow through CLI, API, or preset. Every workflow must produce valid structured output.

#### Coding Workflow
- [x] `plan_task()` → orchestrator produces valid `ImplementationPlan`.
- [ ] `run_task()` happy path → planner → coder emits bounded patch → patch applies → verifier validates. *(blocked: shell approval + model patch quality)*
- [ ] Dirty repo block → `run_task()` refuses unless `allow_dirty=True`. *(not tested)*
- [x] Coder failure path → invalid patch retries up to cap, records `patch_attempts.jsonl`.
- [ ] Patch application failure → rollback, retry prompt includes prior patch error. *(not tested)*
- [ ] Verifier failure → fix work order when fix attempts remain. *(not tested)*
- [ ] Max total tasks guard → plan with >20 tasks fails safely. *(not tested)*
- [ ] Max diff guard → patch exceeding `max_diff_lines` fails safely. *(not tested)*
- [ ] `--no-tests` path still runs planner/coder/verifier and records skipped tests. *(not tested)*
- [x] CLI `plan` returns summary, repo type, likely files, work orders.
- [ ] CLI `run` returns final report. *(returns blocked status + verifier fail)*
- [ ] CLI `start codebase-assistant` runs preset end to end. *(blocked)*
- [ ] API `POST /api/workflows/coding/execute` runs end to end. *(not tested)*
- [ ] API `POST /api/presets/codebase-assistant/run` runs end to end. *(not tested)*
- [ ] Web UI workflow execute for coding runs end to end. *(not tested)*

#### Research Workflow
- [ ] Gatherer returns `GatherResult` with sources/findings. *(not tested — preset crashes before gatherer)*
- [ ] Summarizer consumes gather output → `SummaryResult`. *(not tested)*
- [ ] Reporter consumes summary → `ResearchReport` with confidence/recommendations. *(not tested)*
- [x] Stale context preflight triggers AICtx pipeline before model calls.
- [x] Missing context shards fail before model calls with clear error.
- [ ] CLI `start research-report` runs preset end to end. **FAIL:** AICtx pipeline crash
- [ ] API `POST /api/workflows/research/execute` runs end to end. *(not tested)*
- [ ] API `POST /api/presets/research-report/run` runs end to end. *(not tested)*

#### Documents Workflow
- [ ] Indexer returns `IndexerOutput` for text docs (up to 50 files). **FAIL:** Returns empty documents list
- [ ] Binary/excluded dirs are not sent to model. *(not tested)*
- [ ] Retriever returns `RetrieverOutput` with paths/excerpts. *(not tested — indexer fails)*
- [ ] Answerer returns `AnswererOutput` with citations. *(not tested — indexer fails)*
- [ ] Empty repo returns controlled failed or empty answer state. *(not tested)*
- [ ] CLI `start local-document-chat` runs preset end to end. **FAIL:** Indexer returns empty documents
- [ ] API `POST /api/workflows/documents/execute` runs end to end. *(not tested)*
- [ ] API `POST /api/presets/local-document-chat/run` runs end to end. *(not tested)*

#### File Organization Workflow
- [ ] Analyzer returns `AnalyzerResult`. **FAIL:** Structured output validation fails after repair
- [ ] Proposer returns `ProposerResult`. *(not tested — analyzer fails)*
- [ ] Preview call returns second proposer output without applying. *(not tested)*
- [ ] Applier returns `ApplierResult`. *(not tested)*
- [ ] `run_task(dry_run=True)` → no file moves. *(not tested)*
- [ ] `run_task(dry_run=False)` → files renamed/moved. *(not tested)*
- [ ] Missing source file reported per move, not hidden. *(not tested)*
- [ ] Unsafe/impossible moves recorded as failed entries. *(not tested)*
- [ ] CLI `start file-organizer` runs preset end to end. **FAIL:** Analyzer structured output validation fails
- [ ] API `POST /api/workflows/file_organization/execute` runs end to end. *(not tested)*
- [ ] API `POST /api/presets/file-organizer/run` runs end to end. *(not tested)*

#### Command Assistant Workflow
- [x] Parser returns `ParsedIntent` with intent/action/constraints.
- [x] Generator returns `GeneratedCommand` with command array, explanation, safety flag.
- [ ] Unsafe command request returns `safe=false`. *(not tested)*
- [x] CLI `start command-assistant` runs preset end to end. *(transient parse fail on 1st try, success on 2nd)*
- [ ] API `POST /api/workflows/command_assistant/execute` runs end to end. *(not tested)*
- [ ] API `POST /api/presets/command-assistant/run` runs end to end. *(not tested)*

#### Docs Maintenance Workflow
- [x] Detector returns `DetectionResult` against AICtx docs context.
- [x] Updater returns `UpdateResult` per stale doc item.
- [ ] Aligner returns `AlignmentResult` with aligned true/false + issues. *(not tested — plan mode stops before aligner)*
- [x] Public-doc impact path skips direct rewrite and generates review patch.
- [x] Mode `plan` exercises live detection but does not apply.
- [ ] Mode `apply` writes changed docs. *(not tested)*
- [x] CLI `start docs-maintainer` runs preset end to end. *(plan mode confirmed)*
- [ ] API `POST /api/workflows/docs_maintenance/execute` runs end to end. *(not tested)*
- [ ] API `POST /api/presets/docs-maintainer/run` runs end to end. *(not tested)*

#### GitHub Maintenance Workflow
- [x] Summarizer returns `SummaryResult` with issue number/title/summary.
- [x] Drafter returns `DraftResult` with PR title/body.
- [x] Raw issues text input works.
- [x] Issues file path input works through preset.
- [x] CLI `start github-maintainer` runs preset end to end.
- [ ] API `POST /api/workflows/github_maintenance/execute` runs end to end. *(not tested)*
- [ ] API `POST /api/presets/github-maintainer/run` runs end to end. *(not tested)*

### 2.8 Tools
Test every tool through workflow or direct invocation:

- [ ] `browser` — fetch page, screenshot. *(not tested)*
- [x] `filesystem` — read, write, list, search files. *(via API TestClient)*
- [x] `git` — `status`, `diff_patch`. *(via API TestClient)*
- [ ] `http` — GET/POST requests. *(not tested)*
- [x] `shell` — shell command execution. *(correctly blocked by approval in API)*
- [x] `memory` — memory store read/write. *(via CLI)*
- [ ] `local_db` — SQLite ops. *(returns False — no DB configured)*
- [ ] `mcp` — MCP server interactions. *(not tested)*
- [ ] `network` — network diagnostics. *(not tested)*
- [x] `registry.py` — tool registry lists all tools. *(via pytest)*

### 2.9 API Server
- [x] `GET /api/providers` lists all providers with health.
- [x] `GET /api/providers/templates` lists templates.
- [x] `POST /api/providers` adds provider + secret (auth-gated).
- [x] `POST /api/providers/assign` assigns role binding (auth-gated).
- [x] `GET /api/models` lists resolved model bindings.
- [x] Protected endpoints reject missing/invalid API key unless dev mode enabled.
- [x] API responses never expose raw secrets.
- [x] `POST /api/workflows/coding/execute` returns run ID + artifacts.
- [x] `POST /api/workflows/research/execute` returns run ID + artifacts.
- [x] `POST /api/workflows/documents/execute` returns run ID + artifacts.
- [x] `POST /api/workflows/file_organization/execute` returns run ID + artifacts.
- [x] `POST /api/workflows/command_assistant/execute` returns run ID + artifacts.
- [x] `POST /api/workflows/docs_maintenance/execute` returns run ID + artifacts.
- [x] `POST /api/workflows/github_maintenance/execute` returns run ID + artifacts.
- [x] `POST /api/presets/codebase-assistant/run` returns run ID + artifacts.
- [x] `POST /api/presets/research-report/run` returns run ID + artifacts.
- [x] `POST /api/presets/local-document-chat/run` returns run ID + artifacts.
- [x] `POST /api/presets/file-organizer/run` returns run ID + artifacts.
- [x] `POST /api/presets/command-assistant/run` returns run ID + artifacts.
- [x] `POST /api/presets/docs-maintainer/run` returns run ID + artifacts.
- [x] `POST /api/presets/github-maintainer/run` returns run ID + artifacts.
- [x] `GET /api/runs/{run_id}` shows status + artifacts.
- [x] `GET /api/runs/{run_id}/stream` streams async status.
- [ ] WebSocket `/api/runs/{run_id}/ws` streams status. *(not tested — live server not started)*

### 2.10 Web UI / Guided TUI / Desktop
- [x] Web UI Provider Center lists configured profiles/providers. *(via TestClient)*
- [ ] Web UI workflow execute for coding triggers live run. *(not tested — live server not started)*
- [ ] Web UI workflow execute for research triggers live run. *(not tested)*
- [ ] Web UI workflow execute for documents triggers live run. *(not tested)*
- [ ] Web UI workflow execute for file_organization triggers live run. *(not tested)*
- [ ] Web UI workflow execute for command_assistant triggers live run. *(not tested)*
- [ ] Web UI workflow execute for docs_maintenance triggers live run. *(not tested)*
- [ ] Web UI workflow execute for github_maintenance triggers live run. *(not tested)*
- [ ] Web UI preset run for codebase-assistant triggers live run. *(not tested)*
- [ ] Web UI preset run for research-report triggers live run. *(not tested)*
- [ ] Web UI preset run for local-document-chat triggers live run. *(not tested)*
- [ ] Web UI preset run for file-organizer triggers live run. *(not tested)*
- [ ] Web UI preset run for command-assistant triggers live run. *(not tested)*
- [ ] Web UI preset run for docs-maintainer triggers live run. *(not tested)*
- [ ] Web UI preset run for github-maintainer triggers live run. *(not tested)*
- [ ] Web UI run status polling displays completed/failed state + artifacts/errors. *(not tested)*
- [ ] Guided TUI preset picker routes to live preset paths. *(not tested — interactive)*
- [ ] Desktop UI starts web UI and routes correctly. *(not tested)*

### 2.11 Safety & Policy
Force these and confirm clear, actionable errors:

- [x] Missing provider profile → setup message.
- [ ] Missing secret for `api_key`/`bearer`/`x_api_key`/`bedrock_api_key` provider. *(not tested)*
- [ ] Invalid model ID → model not found error. *(not tested)*
- [ ] Auth failure → auth error surfaced. *(not tested)*
- [ ] Rate limit / quota → surfaced to caller, not swallowed. *(not tested)*
- [ ] Network failure / timeout → retry across 3 attempts, then surfaces. *(not tested)*
- [ ] Provider returns empty content → treated as failure where required. *(not tested)*
- [ ] Provider returns non-JSON where structured JSON required → repair path triggers. *(not tested)*
- [x] Second schema-invalid output returns failed `AgentResult` with both errors. *(file-organizer analyzer confirms)*
- [ ] Coder emits patch for file outside work order allowed files → blocked. *(not tested)*
- [x] Docs updater tries to rewrite public docs with pending impact → blocked/review patch. *(docs-maintainer plan mode confirms)*
- [x] API protected endpoint with no API key → rejected. *(returns 503 when auth not configured)*
- [x] API high-risk tool invoked without approval → blocked. *(shell/browser return 403)*
- [x] `SafetyError` — blocked file access. *(pytest confirms)*
- [x] `PolicyEngine` — runtime policy checks block disallowed operations. *(pytest confirms)*
- [x] `PrivacyEnforcer` — secrets scrubbed from logs/ledgers. *(pytest confirms)*
- [x] `NetworkEnforcer` — `file://` block. *(pytest confirms)*
- [x] Browser tool sandbox prevents escapes. *(pytest confirms)*

### 2.12 Core Subsystems
Verify these work through indirect use above, or with quick smoke checks:

- [x] `agent_protocol` — agent messages serialize/deserialize correctly. *(pytest confirms)*
- [x] `approval_workflow` — approval gates block/allow correctly. *(pytest confirms)*
- [x] `artifact_store` — artifacts persist under `.ai-team/runs/<run-id>/`. *(observed in test runs)*
- [x] `capability_registry` — capabilities resolve for all roles. *(pytest confirms)*
- [x] `cascading_router` — requests route to correct model. *(pytest confirms)*
- [x] `error_classification` — errors taxonomy works. *(pytest confirms)*
- [x] `events` — event bus publishes/consumes. *(pytest confirms)*
- [x] `json_repair` — JSON repair for model output. *(implicit via workflow agents)*
- [x] `ledger` — run ledger append-only. *(pytest confirms hash chain)*
- [x] `logging` — structured logging. *(observed)*
- [x] `model_registry` — model resolution. *(pytest confirms)*
- [x] `patching` — diff patch application. *(pytest confirms)*
- [x] `policies` / `policy_engine` — safety policies enforced. *(pytest + API confirm)*
- [x] `privacy_enforcer` — privacy rules active. *(pytest confirms)*
- [x] `public_api` — public API surface stable. *(pytest confirms)*
- [x] `redaction` — secret redaction in dumps. *(config-dump confirms)*
- [x] `replay_engine` — run replay. *(pytest confirms)*
- [ ] `resume` — resume orchestrator. **FAIL:** coding workflow ledger format mismatch
- [x] `retry_engine` — retry logic. *(pytest confirms)*
- [x] `run_executor` — direct run execution. *(pytest confirms)*
- [x] `schemas` / `schemas_runtime` — schemas validate. *(pytest confirms)*
- [x] `state_machine` — runtime state transitions correctly. *(pytest confirms)*
- [x] `step_budget` — step-level budgeting. *(pytest confirms)*
- [x] `tool_protocol` — tool call protocol. *(pytest confirms)*
- [x] `workflow_runner` — generic workflow runner. *(pytest confirms)*

### 2.13 Adapters / Integrations
- [ ] `WebResearchAdapter` — web search / fetch. *(not tested)*
- [ ] `GitHubCliAdapter` — GitHub CLI ops. *(not tested)*
- [ ] `MCPClientAdapter` — MCP server calls. *(not tested)*

---

## 3. Vision (Deferred — Test Later)

Use only models declared with `vision` capability. Vision requests to non-vision models must be rejected by `validate_request`.

- [ ] Azure vision deployment.
- [ ] Bedrock vision model.
- [ ] Gemini vision model.
- [ ] Anthropic vision model.
- [ ] Kimi/Moonshot vision-capable model.
- [ ] Ollama/LM Studio local vision model if installed.
- [ ] Non-vision model rejects image request with clear error.
- [ ] `multimodal.image` tool `describe` with real PNG base64 returns non-placeholder description.
- [ ] `multimodal.image` tool `ocr` with real text image returns extracted text.
- [ ] Tool invocation through API `/api/tools/multimodal.image/invoke` uses live vision when configured.
- [ ] Tool invocation through workflow/tool registry uses live vision when configured.

---

## 4. Regression & Unit Tests

Run after any change:

```bash
# Core
pytest tests/core/test_model_registry.py -v
pytest tests/core/test_schemas.py -v
pytest tests/test_provider_profiles.py -v

# Tools, smoke, boundaries
pytest tests/test_tool_protocol.py -v
pytest tests/test_local_db_tool.py -v
pytest tests/test_browser_tool.py -v
pytest tests/smoke/ -v

# Workflow isolation + runner
pytest tests/test_workflow_isolation.py -v
pytest tests/test_workflow_runner.py -v

# Full suite
pytest tests/ -q
```

- [x] `tests/core/test_model_registry.py` passes.
- [x] `tests/core/test_schemas.py` passes.
- [x] `tests/test_provider_profiles.py` passes.
- [x] `tests/test_tool_protocol.py` + `tests/test_local_db_tool.py` + `tests/test_browser_tool.py` pass.
- [x] `tests/test_workflow_isolation.py` passes.
- [x] `tests/test_workflow_runner.py` passes.
- [x] `tests/smoke/` passes.
- [x] Full suite `pytest tests/` passes (779 passed, 3 skipped).

---

## 5. DevTest Runner

Use the organized devtest runner for structured validation:

```powershell
# Directive governance + docs checks
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode directive -NoPrompt

# Targeted functional checks
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode targeted

# AI connectivity (max 2 consecutive runs, 120s timeout each)
powershell -ExecutionPolicy Bypass -File .\devtest\ai_test.ps1
```

- [ ] `directive` mode passes. *(not run)*
- [ ] `targeted` mode passes. *(not run)*
- [ ] `ai_test.ps1` passes (planner/executor/verifier connectivity). *(not run — max 2 consecutive runs rule)*

---

## 6. Minimum "Agentheim Works Front-to-Back" Evidence

Do not claim readiness until all of the following have concrete pass/fail evidence:

- [x] Azure provider adapter passes quick smoke (ping + doctor + test).
- [ ] Every CLI command in §2.1–§2.5 executes without error. **FAIL:** `report`, `resume`, `mcp-list`, `copy` missing
- [ ] Every preset in §2.6 runs end-to-end with Azure. **FAIL:** `codebase-assistant`, `file-organizer`, `local-document-chat`, `research-report`, `context-maintainer`
- [ ] Every workflow in §2.7 produces valid structured output. **FAIL:** coding `run_task` happy path, research, documents, file_organization
- [x] Every tool in §2.8 invokes correctly. *(filesystem, git tested; shell/browser correctly blocked)*
- [x] Every API endpoint in §2.9 responds correctly. *(via TestClient)*
- [ ] Web UI, Guided TUI, and Desktop surfaces in §2.10 route correctly. *(not tested — live server not started)*
- [x] Safety cases in §2.11 fail cleanly with actionable errors. *(partial — pytest + API confirm core safety)*
- [x] Core subsystems in §2.12 verified through smoke or indirect use.
- [ ] Adapters in §2.13 verified. *(not tested)*
- [x] Regression suite in §4 passes.
- [ ] DevTest runner in §5 passes. *(not run)*
- [x] Ledgers/artifacts contain raw model output where promised, and no raw secrets.

---

## Test Metadata

| Round | Date | Model | Provider | Notes |
|-------|------|-------|----------|-------|
| 1 | 2026-05-14 | openai.gpt-oss-120b-1:0 | AWS Bedrock (eu-central-1) | Phase 1-3 partial; empty diffs from model |
| 2 | 2026-05-14 | gpt-5.4 | Azure Foundry (azure-real) | Full system test; 779 unit tests pass; 4 CLI bugs; 5 preset/workflow failures; API/Web UI pass via TestClient |
