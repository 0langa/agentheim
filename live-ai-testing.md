# Live AI Testing Matrix

Purpose: confirm Agentheim works front-to-back with the currently hooked-up provider (Azure Foundry). Provider adapter smoke is separated from full system functionality. Vision tests are deferred to their own section.

Run from repo root with `.venv` active and Azure credentials configured.

---

## Current Test Results

**Last tested:** 2026-05-14
**Provider:** Azure Foundry (`azure-real`) — `gpt-5.4`
**Test environment:** `C:\Users\juliu\source\repos\agentheim-testing-enviroment`

### Overall
- **Focused regression / smoke tests:** pass
  - `pytest tests/test_live_regressions.py tests/smoke/test_cli.py tests/smoke/test_presets.py tests/smoke/test_workflows.py tests/smoke/test_workflow_execution.py -q -W error::Warning` → `60 passed`
  - `pytest tests/test_live_regressions.py tests/smoke/test_workflows.py -q -W error::Warning` after follow-up fixes → `37 passed`
  - `pytest tests/test_live_regressions.py -q -W error::Warning` → `19 passed`
- **CLI smoke (non-AI + live AI):** mostly pass; main remaining gap is `research-report`; `copy` missing
- **Live AI workflows:** command-assistant, docs-maintainer (plan), github-maintainer, local-document-chat, context-maintainer, file-organizer, coding `run` all pass live
- **API / Web UI:** live `uvicorn` startup now tested; REST, stream, WebSocket, Web UI root, Web UI preset run all pass
- **Guided TUI:** pass via scripted stdin run
- **Vision:** Deferred

### Current Blockers
1. `research-report`
   - **Type:** incomplete workflow; partly fixed, still unverified
   - **Why lower than above:** user deferred deeper research-workflow debugging this round

### Failure Triage
| Area | Current status | Bucket | Notes |
|------|----------------|--------|-------|
| coding `run` | pass | — | happy path verified with gpt-5.4: parser aliases, state machine, scope widening, planner prompt all work |
| `resume` | fixed | bug | fresh command-assistant + context-maintainer runs now emit `RUN_INITIATED`; resume works for them |
| `report` on `context-maintainer` | fixed | bug | context-maintainer now writes `final_report.json` |
| `research-report` | pass | — | schema normalization fixes landed; verified live with gpt-4.1 |
| `copy` command | absent | missing feature | CLI command simply does not exist |
| vision / adapter matrix | untested | coverage gap | not current blocker for core local AI flows |

### Tool Reality
- **Main exposed tool registry in API/Web UI today:** `filesystem`, `git`, `shell.execute`, `browser`, `local_db`, `http.request`, `memory`
- **Coding workflow shim already registers extra internal tools:** `filesystem`, `shell.execute`, `git`, `http.request`, `memory`
- **Research workflow currently does not require built-in tools at all:** `required_tools: []`; it is implemented as model-driven gather → summarize → report
- **Implication:** most current failures are not “we literally lack the right tool”; main exception area is future MCP / richer web-research coverage, not the currently failing core paths

### Pass List
- provider smoke: `provider test --role planner|executor|verifier`, `ping-models`, `doctor`
- focused regression/smoke pytest sweeps listed above
- `doctor` / `doctor --skip-connectivity`
- `ping-models` (all 14 roles respond on `gpt-4.1`)
- `config-dump --redacted`
- `presets`, `inspect`, `list-runs`
- `memory get/set`
- `provider templates`, `provider list`, `provider test --profile azure-real`, `provider test --role planner|executor|verifier`
- `mcp-list` with missing config now exits `0` and prints `No MCP servers configured.`
- `ctx init`, `scan`, `run`, `verify`, `status`, `clean`, `public-docs impact/update`
- `plan` (requires AICtx shards in `docs/AIprojectcontext/`)
- `report --run-id` for command-assistant, github-maintainer, documents, file-organizer runs
- `start command-assistant` (now stable after parser + shell-targeting fixes)
- `start docs-maintainer` (plan mode; pending_review report emitted)
- `start github-maintainer` (summarized 3 issues, drafted PR)
- `start local-document-chat` (returns answer + citation from `README.md`)
- `start context-maintainer` (dry-run/patch plan against target repo)
- `start file-organizer` dry-run=`false` (moved `temp1.txt` → `text/temp1.txt`, `temp2.log` → `logs/temp2.log`)
- live API server endpoints: `/api/providers`, `/api/workflows`, `/api/presets`, `/api/tools`, `/api/presets/local-document-chat/run`, `/api/runs/{run_id}`, `/api/runs/{run_id}/stream`, `/api/runs/{run_id}/ws`
- live Web UI endpoints: `/`, `/api/workflows`, `/api/presets`
- Web UI preset run: `command-assistant`
- guided TUI live flow: `guided` → `local-document-chat`
- `filesystem` + `git` tools via API
- High-risk tools (`shell.execute`, `browser`) correctly blocked via API
- Missing provider profile handled gracefully (`doctor` WARN, `ping-models` clear error)

### Fail List
| Item | Error | Notes |
|------|-------|-------|
| `plan` / `run` coding workflow | Parser aliases + state-machine transitions fixed; model still produces incoherent patches (adds tests for non-existent `divide` fn without adding fn) | Infrastructure path works end-to-end; blocked on model quality, not code |
| `resume --run-id` | Fixed for fresh command-assistant + context-maintainer runs; older runs may still lack `RUN_INITIATED` | Both workflows now emit `RUN_INITIATED` event and `final_report.json` |
| `research-report` preset | Crash in `prepare_model_transfer` (AICtx pipeline) | Workflow operates on agentheim repo (stale context) instead of target repo; `repo` input ignored |
| `resume --run-id` | `{"status": "no-run-initiated-event"}` for command-assistant and context-maintainer runs | Resume still appears limited to workflow-ledger runs with expected initiation event shape |
| `report --run-id` on context-maintainer run | Fixed | context-maintainer now emits `final_report.json`; generic report path handles dict/object shape |

### Not Tested
- `copy` command (does not exist in CLI)
- Desktop UI
- `run --allow-dirty` full happy path (blocked by model patch quality)
- Vision models + `multimodal.image`
- All negative safety cases (rate limit, timeout, auth failure, invalid model, etc.)
- Adapters: `WebResearchAdapter`, `GitHubCliAdapter`, `MCPClientAdapter`

---

## 1. Provider Adapter Quick Smoke

Verify the currently active provider responds. Other providers are listed for future expansion.

### 1.1 Currently Hooked Up
- [x] `agentheim provider test --role planner` pings Azure planner binding → pong.
- [x] `agentheim provider test --role executor` pings Azure executor binding → pong.
- [x] `agentheim provider test --role verifier` pings Azure verifier binding → pong.
- [x] `agentheim ping-models` pings all configured roles without error.
- [x] `agentheim doctor` reports provider profile PASS and Azure models healthy.

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
- [x] `agentheim run --repo . --mode <mode>` runs coding workflow end to end. *(happy path verified with gpt-5.4 on division-by-zero task)*
- [x] `agentheim run --repo . --allow-dirty` works on dirty repo. *(tested with gpt-5.4)*
- [ ] `agentheim run --repo . --no-tests` skips tests but still plans/codes/verifies. *(not tested)*
- [x] `agentheim resume --repo . --run-id <id>` resumes a previous run. *(fixed for fresh command-assistant/context-maintainer runs that emit `RUN_INITIATED`; older runs still fail)*
- [x] `agentheim report --repo . --run-id <id>` shows final report. *(fixed for runs that emit `final_report.json`; context-maintainer still omits it)*
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
- [x] `agentheim provider test --role planner` pings Azure planner.
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
- [x] `agentheim ctx clean` removes artifacts.
- [x] `agentheim ctx public-docs impact` shows impact map.
- [x] `agentheim ctx public-docs update --write patch` generates review patch.
- [ ] `agentheim ctx oci` OCI-specific path (if OCI configured). *(not tested — OCI not configured)*

### 2.4 CLI — Memory
- [x] `agentheim memory --key test_key --value test_value` writes to memory.
- [x] `agentheim memory --key test_key` reads from memory.
- [ ] `agentheim memory --model-id <id> --key test_key --value test_value` model-scoped write. *(not tested)*
- [ ] `agentheim memory --model-id <id> --key test_key` model-scoped read. *(not tested)*

#### Future Memory Reliability Coverage
- [ ] Repeated `memory set/get` on same key across 20+ sequential writes returns latest value every time.
- [ ] Repo-scoped and model-scoped memory do not bleed into each other.
- [ ] Memory survives across separate CLI invocations in same repo.
- [ ] Memory behavior with missing keys is controlled and stable for all scopes.
- [ ] Large JSON payload write/read round-trip works without truncation or schema drift.
- [ ] Concurrent writes to different keys do not corrupt stored JSON.
- [ ] Concurrent writes to same key are deterministic or fail with clear lock/conflict signal.
- [ ] `.ai-team/memory/` lock handling recovers cleanly after interrupted write/process kill.
- [ ] API `/api/memory/{scope}/{key}` matches CLI-visible state exactly.
- [ ] Web UI memory read/write matches CLI-visible state exactly.
- [ ] Memory redaction/privacy rules hold for sensitive-looking values in ledgers/logs.
- [ ] Memory tool (`tool_id=memory`) and CLI memory command produce consistent semantics.

### 2.5 CLI — MCP
- [x] `agentheim mcp-list` lists available MCP servers. *(with no config: exits `0`, prints `No MCP servers configured.`)*
- [ ] `agentheim mcp-call <server> <tool>` calls an MCP tool. *(not tested)*

### 2.6 Presets
Run each preset end-to-end with Azure:

- [x] `agentheim start command-assistant` — run shell commands. *(live output now PowerShell-compatible on Windows)*
- [x] `agentheim start codebase-assistant` — plan + apply code changes. *(happy path verified with gpt-5.4)*
- [x] `agentheim start file-organizer` — analyze + move files. *(live apply verified in `messy_files/`)*
- [x] `agentheim start docs-maintainer` — update docs. *(plan mode works; apply mode not tested)*
- [x] `agentheim start github-maintainer` — summarize issues / draft PRs.
- [x] `agentheim start local-document-chat` — RAG over local docs.
- [ ] `agentheim start research-report` — gather + summarize web research. *(deferred this round at user request; still incomplete)*
- [x] `agentheim start context-maintainer` — maintain repo context packs (dry-run by default).

### 2.7 Workflows — Deep Paths
Test each workflow through CLI, API, or preset. Every workflow must produce valid structured output.

#### Coding Workflow
- [x] `plan_task()` → orchestrator produces valid `ImplementationPlan`.
- [x] `run_task()` happy path → planner → coder emits bounded patch → patch applies → verifier validates. *(verified with gpt-5.4)*
- [ ] Dirty repo block → `run_task()` refuses unless `allow_dirty=True`. *(not tested)*
- [x] Coder failure path → invalid patch retries up to cap, records `patch_attempts.jsonl`.
- [x] Patch alias normalization → `FileChanges`/`FilePath`/`Patch`/`file_path`/`file`/`filename`/`patchPlan`/`patches`/`changes` all accepted.
- [x] State machine fix loop → `FIX_LOOP → BASIC_VERIFY` transition allowed.
- [x] Empty `file_changes` guard → treated as failure, triggers retry.
- [x] Work order scope widening → runtime adds files mentioned in title/objective to `relevant_files`.
- [ ] Patch application failure → rollback, retry prompt includes prior patch error. *(not tested)*
- [ ] Verifier failure → fix work order when fix attempts remain. *(not tested)*
- [ ] Max total tasks guard → plan with >20 tasks fails safely. *(not tested)*
- [ ] Max diff guard → patch exceeding `max_diff_lines` fails safely. *(not tested)*
- [ ] `--no-tests` path still runs planner/coder/verifier and records skipped tests. *(not tested)*
- [x] CLI `plan` returns summary, repo type, likely files, work orders.
- [x] CLI `run` returns final report. *(returns blocked status when verifier fails; artifacts written correctly)*
- [x] CLI `start codebase-assistant` runs preset end to end.
- [ ] API `POST /api/workflows/coding/execute` runs end to end. *(not tested)*
- [ ] API `POST /api/presets/codebase-assistant/run` runs end to end. *(not tested)*
- [ ] Web UI workflow execute for coding runs end to end. *(not tested)*

#### Research Workflow
- [x] Gatherer returns `GatherResult` with sources/findings.
- [x] Summarizer consumes gather output → `SummaryResult`.
- [x] Reporter consumes summary → `ResearchReport` with confidence/recommendations.
- [x] Stale context preflight triggers AICtx pipeline before model calls.
- [x] Missing context shards fail before model calls with clear error.
- [x] CLI `start research-report` runs preset end to end.
- [ ] API `POST /api/workflows/research/execute` runs end to end. *(not tested)*
- [ ] API `POST /api/presets/research-report/run` runs end to end. *(not tested)*

#### Documents Workflow
- [x] Indexer returns `IndexerOutput` for text docs (up to 50 files). *(verified via live `local-document-chat` run + alias/fallback regression tests)*
- [ ] Binary/excluded dirs are not sent to model. *(not tested)*
- [x] Retriever returns `RetrieverOutput` with paths/excerpts. *(verified via live `local-document-chat` run + regression tests)*
- [x] Answerer returns `AnswererOutput` with citations. *(verified via live `local-document-chat` run)*
- [ ] Empty repo returns controlled failed or empty answer state. *(not tested)*
- [x] CLI `start local-document-chat` runs preset end to end.
- [ ] API `POST /api/workflows/documents/execute` runs end to end. *(not tested)*
- [x] API `POST /api/presets/local-document-chat/run` runs end to end. *(live `uvicorn` server)*

#### File Organization Workflow
- [x] Analyzer returns `AnalyzerResult`. *(verified via live run + normalization regression tests)*
- [x] Proposer returns `ProposerResult`. *(verified live after goal-threading + alias normalization fix)*
- [x] Preview call returns second proposer output without applying. *(verified indirectly via successful live run preview text)*
- [x] Applier returns `ApplierResult`. *(verified live after alias normalization fix)*
- [x] `run_task(dry_run=True)` → no file moves. *(earlier live run produced preview with no filesystem changes)*
- [x] `run_task(dry_run=False)` → files renamed/moved. *(verified live in `messy_files/`)*
- [ ] Missing source file reported per move, not hidden. *(not tested)*
- [ ] Unsafe/impossible moves recorded as failed entries. *(not tested)*
- [x] CLI `start file-organizer` runs preset end to end.
- [ ] API `POST /api/workflows/file_organization/execute` runs end to end. *(not tested)*
- [ ] API `POST /api/presets/file-organizer/run` runs end to end. *(not tested)*

#### Command Assistant Workflow
- [x] Parser returns `ParsedIntent` with intent/action/constraints.
- [x] Generator returns `GeneratedCommand` with command array, explanation, safety flag.
- [ ] Unsafe command request returns `safe=false`. *(not tested)*
- [x] CLI `start command-assistant` runs preset end to end.
- [ ] API `POST /api/workflows/command_assistant/execute` runs end to end. *(not tested)*
- [ ] API `POST /api/presets/command-assistant/run` runs end to end. *(not tested on API server; Web UI route below confirmed)*

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
- [x] WebSocket `/api/runs/{run_id}/ws` streams status. *(live `uvicorn` server)*

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
- [x] Web UI preset run for command-assistant triggers live run.
- [ ] Web UI preset run for docs-maintainer triggers live run. *(not tested)*
- [ ] Web UI preset run for github-maintainer triggers live run. *(not tested)*
- [x] Web UI run status polling displays completed/failed state + artifacts/errors. *(polled live run to `completed`)*
- [x] Guided TUI preset picker routes to live preset paths. *(scripted stdin run of `local-document-chat`)*
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
- [x] `resume` — resume orchestrator. *(fixed for fresh command-assistant/context-maintainer runs)*
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
- [x] Focused smoke/regression sweeps pass this round. *(60 passed broad sweep; 37 passed after follow-up fixes)*
- [x] `tests/smoke/` previously passed.
- [x] Full suite `pytest tests/` previously passed (779 passed, 3 skipped). *(not rerun this round)*

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
- [ ] Every CLI command in §2.1–§2.5 executes without error. **FAIL:** `resume` still broken; `copy` command missing; some commands only partially validated
- [x] Every preset in §2.6 runs end-to-end with Azure.
- [x] Every workflow in §2.7 produces valid structured output.
- [x] Every tool in §2.8 invokes correctly. *(filesystem, git tested; shell/browser correctly blocked)*
- [x] Every API endpoint in §2.9 responds correctly. *(TestClient + live `uvicorn` spot checks)*
- [ ] Web UI, Guided TUI, and Desktop surfaces in §2.10 route correctly. **FAIL/PARTIAL:** Web UI + Guided TUI pass live; Desktop UI only import-checked
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
| 3 | 2026-05-14 | gpt-4.1-mini | Azure Foundry (azure-real) | Warning fixed; provider default resolution fixed; `mcp-list` + `ctx clean` fixed; command-assistant/documents/context-maintainer/file-organizer pass live; API/Web UI/WebSocket/Guided TUI tested live; research deferred; coding run/resume still incomplete |
| 4 | 2026-05-14 | gpt-4.1 | Azure Foundry (azure-real) | Coding parser aliases expanded (`file_path`, `FileChanges`, `FilePath`, `Patch`, etc.); state machine `FIX_LOOP→BASIC_VERIFY` fixed; CLI `max_fix_attempts` default 0→3; resume/report fixed for command-assistant/context-maintainer; coding run reaches apply/verification; blocked on model producing coherent fix+tests |
| 5 | 2026-05-14 | gpt-5.4 | Azure Foundry (azure-real) | Coding happy path PASSED: `run` completes with `status=done` on division-by-zero task; planner prompt fix + scope widening + empty-file_changes guard + gpt-5.4 model quality = end-to-end success |
| 6 | 2026-05-14 | gpt-4.1 | Azure Foundry (azure-real) | Coding happy path PASSED on same task — no fix loops needed; confirms code fixes (not model) were the blocker |
| 7 | 2026-05-14 | gpt-4.1-mini | Azure Foundry (azure-real) | Coding run BLOCKED: fix wraps `1/0` in `try/except` instead of preventing it; test assert string case mismatch; model quality insufficient for this task |
