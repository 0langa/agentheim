# Agentheim V1 Product Roadmap

This roadmap is the executable V1 plan for turning Agentheim from a developer-oriented automation project into an end-user focused open-source product.

The order is strict. Each phase depends on the phases before it. A human or agent can follow this document from top to bottom without choosing a strategy or inventing missing decisions.

V1 means:

1. A user can install Agentheim.
2. A user can connect one provider.
3. A user can verify readiness.
4. A user can choose a task by plain-language goal.
5. A user can run the task.
6. A user can find the result.
7. A user can recover from common failures.
8. Advanced users keep the existing command/API power.

V1 does not mean every internal subsystem becomes a beginner-facing product feature. Existing advanced and integration-heavy surfaces remain available, but V1 must clearly label, gate, or hide them from the beginner path until they are configured and usable.

## External Baselines

This roadmap uses these external baselines:

- [Command Line Interface Guidelines](https://clig.dev/) for concise help, discoverability, human-friendly output, stable machine output, helpful errors, and no surprise behavior.
- [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) for packaging metadata, scripts, optional dependencies, and installable command behavior.
- [OpenSSF Scorecard](https://github.com/ossf/scorecard) for CI, security policy, branch protection, token permissions, dependency updates, SAST, package health, and release hygiene.
- [Semantic Versioning](https://semver.org/) for the V1 requirement that public API and CLI compatibility are declared and documented.

## Product Decisions

These decisions are final for V1.

| Area | V1 Decision |
| --- | --- |
| Beginner command layer | Add it. Keep all current commands. |
| Default beginner commands | `setup`, `status`, `use`, `runs`, `open` |
| Full command inventory | Keep `agentheim commands` and `agentheim commands --json` |
| Default local UI | `agentheim open` launches the Web UI on localhost |
| Desktop wrapper | Keep as `agentheim desktop`; `agentheim open --desktop` delegates to it |
| Provider setup | Beginner flow configures one provider and binds core roles automatically |
| Advanced provider roles | Keep `provider assign` and `provider assign-all` |
| Recommended beginner presets | Codebase Assistant, Local Document Chat, Command Assistant, Context Maintainer |
| Advanced presets | Research Report, Docs Maintainer, File Organizer, GitHub Maintainer |
| MCP/Web/Vision/GitHub integrations | Available only when configured; otherwise fail closed with setup guidance |
| Marketplace/distributed/self-improving/federation | Quarantine from beginner surfaces for V1; keep advanced/internal tests and docs honest |
| V1 distribution | Publish GitHub release, source archive, sdist, wheel, and PyPI package |
| Default protected branch | Use the current default branch `master` and align docs/security policy to it |
| Public API policy | Declare V1 API routes and CLI commands before version `1.0.0` |
| Telemetry | No telemetry in V1 |

## Product Model

Agentheim has three V1 layers.

### Layer 1: Beginner Product Layer

This is the default user path.

| Command | Purpose | Wraps |
| --- | --- | --- |
| `agentheim setup` | Configure and verify one provider | `provider templates`, `provider add`, `provider assign-all`, `doctor`, `ping-models` |
| `agentheim status` | Show readiness, provider state, optional integration state, and recent runs | `doctor`, `provider list`, `list-runs`, run summaries |
| `agentheim use` | Launch a recommended task by goal | `guided`, `presets`, `start`, preset validation |
| `agentheim runs` | List, inspect, report, resume, and open artifacts | `list-runs`, `report`, `resume` |
| `agentheim open` | Open the local Web UI | `interfaces.web_ui`, `desktop` fallback when requested |

### Layer 2: Advanced User Layer

These commands stay available and documented as advanced reference:

- `provider ...`
- `doctor`
- `ping-models`
- `presets`
- `guided`
- `start`
- `inspect`
- `plan`
- `run`
- `list-runs`
- `report`
- `resume`
- `ctx ...`
- `mcp-list`
- `mcp-call`
- `memory`
- `commands`
- `config-dump`
- `desktop`
- `copy`

### Layer 3: Developer And Integration Layer

These remain documented outside the beginner path:

- HTTP API
- workflow packs
- provider adapters
- tool protocol
- MCP integration
- context internals
- marketplace internals
- distributed workflow internals
- self-improving hooks
- federation internals

## Product Rules

1. Do not delete existing commands during V1 simplification.
2. Do not rename existing commands without aliases and tests.
3. Do not expose unconfigured integrations as successful.
4. Do not show internal subsystem names in beginner docs unless necessary.
5. Do not require users to read architecture docs for first run.
6. Do not add telemetry.
7. Do not publish V1 until README quickstart commands are tested.
8. Do not call a route, command, or preset stable unless it has tests, docs, and clear failure behavior.

## Phase 1: Shared Product Foundations

Goal: create shared product services so CLI, API, Web UI, and Desktop UI stop duplicating readiness, preset, run, and error logic.

### 1.1 Create Readiness Service

Code work:

- Create `interfaces/readiness.py`.
- Move provider-readiness logic out of `interfaces/cli/cli.py`.
- Expose a `ReadinessState` model with these states: `ready`, `needs_provider`, `needs_secret`, `needs_model`, `needs_roles`, `endpoint_unreachable`, `auth_failed`, `model_failed`, `optional_integration_unavailable`.
- Include provider profile name, missing roles, configured providers, optional integration states, and next actions.
- Use this service from `doctor`, `status`, API provider/status routes, Web UI, and Desktop UI.

Tests:

- Add `tests/test_readiness.py`.
- Cover missing profile, missing provider, missing role, placeholder endpoint, missing secret, failed auth, failed model call, local provider unavailable, ready profile, and optional integration unavailable.
- Update CLI/API/Web tests to use the shared readiness state.

Done when:

- No product surface computes provider readiness independently.
- `doctor` and `status` report consistent results.

### 1.2 Create Preset Catalog Service

Code work:

- Create `presets/catalog.py`.
- Add product metadata to presets: `product_tier`, `recommended_for`, `requires_integrations`, `estimated_time`, `output_kind`, `example_inputs`.
- Product tiers are `recommended`, `advanced`, and `hidden`.
- Set tiers:
  - `codebase-assistant`: `recommended`
  - `local-document-chat`: `recommended`
  - `command-assistant`: `recommended`
  - `context-maintainer`: `recommended`
  - `research-report`: `advanced`
  - `docs-maintainer`: `advanced`
  - `file-organizer`: `advanced`
  - `github-maintainer`: `advanced`
- Add a `QuestionSchema` model instead of exposing `Question.__dict__`.
- Use the catalog from CLI, API, Web UI, and docs checks.

Tests:

- Add catalog tests for grouping, ordering, metadata completeness, required-input schemas, defaults, and example inputs.
- Add parity tests asserting CLI/API/Web return the same catalog tiers.

Done when:

- All user-facing surfaces render presets from one catalog.
- Beginner surfaces show recommended presets first.

### 1.3 Create Run View Service

Code work:

- Create `core/run_view.py` and expose `RunView` through `core.public_api`.
- Define `RunView` with `run_id`, `status`, `summary`, `workflow_id`, `preset_id`, `started_at`, `completed_at`, `report_path`, `artifact_dir`, `resume_available`, `next_actions`.
- Build `RunView` from existing run summaries and run directories.
- Use `RunView` from CLI, API, Web UI, and Desktop UI.

Tests:

- Add tests for completed run, failed run, blocked run, missing report, missing run, and resumable run.
- Add JSON contract tests for `RunView`.

Done when:

- Every product surface shows the same run status and artifact information.

### 1.4 Create Error Catalog

Code work:

- Create `core/error_catalog.py` and expose public types through `core.public_api`.
- Define stable categories: `validation_error`, `configuration_error`, `provider_error`, `auth_error`, `policy_block`, `integration_unavailable`, `not_found`, `run_failed`, `unexpected_error`.
- Each category includes a human message, machine code, exit code, and next actions.
- Route CLI expected errors through this catalog.
- Route API/Web expected errors through this catalog.

Tests:

- Add category tests.
- Add CLI exit-code tests.
- Add API/Web error-shape tests.

Done when:

- Common failures never surface as raw tracebacks in beginner flows.

## Phase 2: Beginner CLI Layer

Goal: make first-run and daily use available through five commands.

### 2.1 Add `agentheim setup`

Code work:

- Create `interfaces/cli/product_commands.py`.
- Register `setup` under a `Getting Started` help panel.
- Support interactive prompts.
- Support non-interactive flags: `--provider`, `--template`, `--model`, `--endpoint`, `--api-key`, `--profile`, `--local`, `--yes`, `--json`, `--dry-run`.
- Supported beginner provider choices: `openai-compatible`, `openai`, `azure`, `anthropic`, `gemini`, `ollama`, `lm-studio`.
- Advanced templates remain accessible through `provider add`.
- Store secrets through the existing secret store.
- Bind planner, executor, verifier, context, and recommended-preset roles to the selected provider/model when compatible.
- Run readiness checks after setup.
- Print `agentheim status` and `agentheim use` as next commands.

Tests:

- Add setup tests for each beginner provider choice.
- Mock secret input and model invocation.
- Verify dry-run writes nothing.
- Verify `--json` output has `status`, `profile`, `provider`, `model`, `readiness`, and `next_actions`.

Done when:

- A user can configure one provider without knowing role names.

### 2.2 Add `agentheim status`

Code work:

- Register `status` under `Getting Started`.
- Show provider readiness, active profile, missing roles, optional integrations, recent runs, and next action.
- Support `--json`.
- Support `--profile`.
- Support `--repo` for recent run lookup, defaulting to current directory.

Tests:

- Cover no config, partial config, ready config, optional integration unavailable, recent runs present, and JSON shape.

Done when:

- `agentheim status` is the single command users run when they are unsure what is wrong.

### 2.3 Add `agentheim use`

Code work:

- Register `use` under `Getting Started`.
- Interactive mode displays recommended tasks by plain-language goal.
- Direct mode accepts `agentheim use <task-id>`.
- Task IDs for V1: `code`, `docs-chat`, `command`, `context`, `research`, `docs-maintain`, `organize-files`, `github`.
- Recommended task IDs are `code`, `docs-chat`, `command`, and `context`.
- Advanced task IDs remain visible under an `Advanced tasks` section.
- Collect required inputs through preset schemas.
- Validate through `Preset.validate_inputs`.
- Submit the run.
- Print run id, status, report path, artifact folder, and `agentheim runs show <run-id>`.
- Support `--input key=value`, `--repo`, `--json`, and `--yes`.

Tests:

- Cover interactive selection with mocked prompt input.
- Cover direct task ID execution.
- Cover missing required input.
- Cover advanced task execution.
- Cover JSON shape.

Done when:

- Users launch tasks by goal instead of memorizing preset IDs.

### 2.4 Add `agentheim runs`

Code work:

- Register `runs` under `Getting Started`.
- Implement subcommands: `list`, `show`, `report`, `resume`, `open-folder`.
- `agentheim runs` defaults to `list`.
- Support `--repo` and `--json`.
- `show` displays the `RunView`.
- `report` prints or opens the human report.
- `resume` delegates to existing resume behavior.
- `open-folder` opens the artifact directory with OS-specific behavior.

Tests:

- Cover default list, show, report, resume, open-folder command construction, JSON shape, missing run, and empty run history.

Done when:

- Users can inspect and recover prior work from one command family.

### 2.5 Add `agentheim open`

Code work:

- Register `open` under `Getting Started`.
- Default behavior launches Web UI at `http://127.0.0.1:<port>`.
- Support `--port`, `--no-browser`, `--desktop`, and `--json`.
- `--desktop` delegates to the existing Desktop UI path.
- Bind to localhost only.
- Print local URL and stop instructions.

Tests:

- Cover default Web launch, no-browser mode, desktop delegation, port option, and JSON shape.

Done when:

- The beginner UI command is obvious and safe by default.

## Phase 3: Web UI Productization

Goal: make Web UI a first-class local product surface.

### 3.1 Remove Prototype Identity

Code work:

- Remove prototype wording from `interfaces/web_ui/__init__.py`.
- Remove prototype wording from FastAPI title, description, version strings, route docstrings, and dashboard copy.
- Set version display from package version.

Tests:

- Web UI tests assert no `Prototype`, `prototype`, or `0.1.0-prototype` appears in HTML, health responses, or OpenAPI metadata.

Done when:

- Web UI presents itself as Agentheim local dashboard.

### 3.2 Replace Unsafe Dynamic HTML Rendering

Code work:

- Stop concatenating unescaped provider, preset, run, and error data into `innerHTML`.
- Use DOM creation APIs or a small HTML-escape helper for every dynamic value.
- Keep static dashboard HTML server-rendered if no frontend build step is introduced.

Tests:

- Add tests with malicious provider/preset/run strings and assert rendered HTML escapes them.
- Add browser smoke coverage for dashboard load without console errors.

Done when:

- Dynamic dashboard data cannot inject markup or script.

### 3.3 Add Product Home Screen

Code work:

- Home screen sections:
  - readiness status
  - connect provider call-to-action
  - recommended tasks
  - advanced tasks
  - recent runs
  - optional integrations
- Use readiness service, preset catalog, and run view service.
- Required input forms come from `QuestionSchema`.
- Run buttons remain disabled until required inputs are present.

Tests:

- Cover readiness display, recommended/advanced grouping, required input disabling, run submission, and recent runs.

Done when:

- A user can start from the Web UI and complete the same beginner path as CLI.

## Phase 4: API V1 Contract

Goal: define stable programmatic behavior before `1.0.0`.

### 4.1 Declare Public V1 Routes

Public V1 routes:

- `GET /api/health`
- `GET /api/status`
- `GET /api/tasks`
- `POST /api/tasks/{task_id}/run`
- `GET /api/runs`
- `GET /api/runs/{run_id}`
- `GET /api/runs/{run_id}/stream`
- `GET /api/providers/templates`
- `GET /api/providers`
- `POST /api/providers/setup`

Advanced V1 routes:

- existing tool routes
- existing workflow routes
- existing preset routes
- existing memory routes
- existing context routes
- existing metrics route

Code work:

- Add public routes where missing.
- Keep existing routes for compatibility.
- Mark advanced routes in API docs.
- Add consistent error schemas from the error catalog.
- Add request IDs to responses.

Tests:

- OpenAPI tests assert public routes exist.
- Error-shape tests cover validation, auth, provider, policy, and missing-resource failures.
- Compatibility tests assert existing routes still exist.

Done when:

- Programmatic users have documented V1 routes and existing routes do not disappear.

## Phase 5: Runs, Artifacts, And Recovery

Goal: every task has an understandable ending.

Code work:

- Use `RunView` after every beginner task submission and completion.
- Standardize CLI final output:
  - run id
  - status
  - summary
  - report path
  - artifact folder
  - next action
- Add `report_path` and `artifact_dir` to canonical summaries where missing.
- Add resume guidance for resumable failures.
- Add progress/watch behavior to `agentheim use --watch` and `agentheim runs show --watch`.

Tests:

- Cover successful run output, failed run output, blocked run output, resumable run output, and JSON output.
- Cover CLI/API/Web consistency.

Done when:

- A user never has to inspect `.ai-team/runs` manually to find normal results.

## Phase 6: Provider And Integration Hardening

Goal: configured integrations work; unconfigured integrations fail closed with setup guidance.

Code work:

- Web research reports `unavailable` with setup guidance when disabled or failed.
- MCP enabled path calls a real configured MCP backend or raises `integration_unavailable`.
- Vision tools return clear failure until provider/model vision support is configured.
- GitHub Maintainer requires explicit GitHub enablement and authenticated `gh` or configured API token.
- Browser tooling reports missing Playwright/browser install steps.
- Optional integration states appear in `agentheim status` and Web UI.

Tests:

- Cover unavailable states for web research, MCP, vision, GitHub, and browser.
- Cover configured mocked success for each integration.

Done when:

- No optional integration gives fake success or unexplained failure.

## Phase 7: Packaging And Installation

Goal: Agentheim installs like a product, not only like a local checkout.

Code work:

- Update `pyproject.toml` metadata:
  - `version = "1.0.0"` only in the final release commit.
  - Add maintainers.
  - Add end-user and developer classifiers.
  - Use current SPDX license metadata supported by setuptools.
  - Review and bound runtime dependencies.
- Add extras: `web`, `desktop`, `browser`, `mcp`, `cloud-aws`, `cloud-google`, `cloud-oci`, `dev`.
- Keep `agentheim = "interfaces.cli.cli:main"` as the only installed CLI script.
- Add wheel and sdist build checks.
- Add clean-venv install smoke test.
- Add pipx install instructions.

Distribution decision:

- V1 ships as GitHub release, source archive, sdist, wheel, and PyPI package.

Tests:

- Build wheel.
- Build sdist.
- Install wheel in clean virtual environment.
- Run `agentheim --help`.
- Run `agentheim status --json`.
- Run mocked first-run smoke.

Done when:

- Editable install is no longer the only documented installation path.

## Phase 8: CI, Security, And Release Gates

Goal: V1 quality is enforced in CI.

Code work:

- Add `.github/workflows/ci.yml`.
- Run default tests on Python 3.12 and 3.13.
- Run no-addopts full suite on Python 3.12.
- Run `compileall`.
- Run docs command checks.
- Run package build.
- Run architecture/import checks.
- Add `.github/workflows/security.yml`.
- Run dependency audit.
- Run CodeQL.
- Run OpenSSF Scorecard.
- Set workflow token permissions to read-only by default.
- Add `.github/dependabot.yml`.
- Add branch protection documentation for `master`.
- Update `SECURITY.md` to reference `master`.
- Add `docs/RELEASE_CHECKLIST.md`.

Tests:

- CI must execute the same commands documented in release checklist.
- Docs checks must fail if README/User Guide mention missing commands.

Done when:

- V1 cannot be released without test, docs, package, and security gates passing.

## Phase 9: Safety And Privacy V1

Goal: local-first and safety claims are visible and enforced.

Code work:

- Add selectable privacy mode to beginner surfaces: `standard`, `local-only`, `strict-private`.
- Show active privacy mode in `agentheim status` and Web UI.
- Enforce privacy mode through existing privacy enforcer and policy engine.
- Add policy explanations to approval prompts.
- Add diagnostic bundle command: `agentheim status --debug-bundle`.
- Redact secrets from bundle, ledgers, reports, logs, API responses, and Web UI.
- Keep network metadata endpoint protections.

Tests:

- Redaction tests for artifacts and debug bundle.
- Privacy mode tests through CLI, API, Web UI, and workflow paths.
- Network deny-list tests for metadata endpoints.
- Approval prompt tests for medium-risk operations.

Done when:

- The safety model is not only internal; users can see and control it.

## Phase 10: Documentation As Tested Product Surface

Goal: beginner docs are short, accurate, and executable.

Code work:

- Rewrite README around:
  - install
  - `agentheim setup`
  - `agentheim status`
  - `agentheim use`
  - `agentheim runs`
  - `agentheim open`
- Rewrite User Guide with beginner path first, recipes second, advanced reference links third.
- Keep full command inventory in `docs/CLI-COMMANDS.md`.
- Generate or validate `docs/CLI-COMMANDS.md` from Typer command registration.
- Add recipes:
  - connect OpenAI-compatible provider
  - connect local Ollama
  - connect LM Studio
  - run Codebase Assistant
  - ask questions over documents
  - inspect prior runs
  - recover from provider failure
- Update stale changelog entries only by adding a top note that historical entries can mention removed prototypes or stubs.
- Remove current-doc references to missing files.

Tests:

- Docs command validation for README and User Guide.
- Local link check for docs.
- CLI command reference generation check.

Done when:

- A first-run user needs README only.
- Advanced users can still find every command.

## Phase 11: Architecture Cleanup For V1 Maintainability

Goal: product additions do not turn interface files into catch-all modules.

Code work:

- Keep `core.public_api` as the only core import boundary for interfaces.
- Split `interfaces/cli/cli.py` into focused modules:
  - product commands
  - repository work commands
  - diagnostics commands
  - MCP commands
  - memory commands
  - shared rendering helpers
- Split `interfaces/web_ui/app.py` into focused modules:
  - models
  - API route registration
  - dashboard rendering
  - WebSocket/SSE helpers
  - error handling
- Move repeated interface logic into shared services:
  - readiness
  - preset catalog
  - run views
  - error catalog
- Quarantine marketplace, federation, distributed, and self-improving surfaces from beginner docs, beginner commands, and default Web UI.
- Keep advanced/import tests for quarantined surfaces.

Tests:

- Existing import-boundary tests stay green.
- Product-surface tests assert quarantined surfaces do not appear in beginner output.
- Architecture checker runs in CI.

Done when:

- V1 product code is maintainable and boundaries remain enforceable.

## Phase 12: V1 Release

Goal: publish `1.0.0` only after all V1 gates pass.

Code work:

- Set package version to `1.0.0`.
- Update changelog with V1 release notes.
- Run release checklist.
- Build wheel and sdist.
- Publish GitHub release.
- Publish PyPI package.
- Tag release as `v1.0.0`.

Required verification:

- `python -m pytest -q`
- `python -m pytest -q -o addopts=`
- `python -m compileall -q agentheim core config interfaces providers presets tools workflows memory agents federation marketplace monitoring multimodal scripts tests`
- package build
- clean wheel install smoke
- docs command check
- link check
- architecture/import check
- security workflow

Done when:

- The public release contains working beginner commands, working advanced compatibility, tested docs, package artifacts, and declared V1 compatibility policy.

## Compatibility Contract

V1 preserves:

- Existing advanced commands.
- Existing preset IDs.
- Existing core API facade imports.
- Existing run artifact directory structure.
- Existing API routes unless explicitly marked internal and replaced by public V1 routes.

V1 adds:

- Beginner command layer.
- Shared readiness model.
- Shared preset catalog.
- Shared run view.
- Shared error catalog.
- Tested docs and release gates.

Breaking changes require:

- changelog entry
- migration note
- test updates
- SemVer-compliant version bump after V1

## V1 Completion Checklist

- [x] Shared readiness service exists and is used by CLI/API/Web/Desktop.
- [x] Shared preset catalog exists and is used by CLI/API/Web/Desktop.
- [x] Shared run view exists and is used by CLI/API/Web/Desktop.
- [x] Shared error catalog exists and is used by CLI/API/Web/Desktop.
- [x] `agentheim setup` works interactively and non-interactively.
- [x] `agentheim status` shows readiness and supports JSON.
- [x] `agentheim use` runs recommended and advanced tasks.
- [x] `agentheim runs` lists, shows, reports, resumes, and opens artifacts.
- [x] `agentheim open` launches localhost Web UI.
- [x] Web UI no longer contains prototype identity.
- [x] Web UI escapes dynamic data.
- [x] Public V1 API routes are documented and tested.
- [x] Optional integrations fail closed with setup guidance.
- [x] Package builds as wheel and sdist.
- [x] Clean wheel install smoke passes.
- [x] GitHub Actions CI exists at repo root.
- [x] Security workflow exists.
- [x] Dependabot exists.
- [x] `SECURITY.md` references `master`.
- [x] README uses beginner commands only for quickstart.
- [x] User Guide starts with beginner path.
- [x] CLI command docs are generated or validated.
- [x] Docs links pass.
- [x] Architecture/import checks run in CI.
- [x] Privacy mode is selectable from beginner surfaces.
- [x] Debug bundle redacts secrets.
- [ ] Changelog contains V1 release notes.
- [ ] Version is `1.0.0` in the release commit.

## Product Decision Rule

Every V1 change must answer:

1. Which V1 phase does this complete?
2. Which user-facing command, route, UI screen, or doc changes?
3. What does the user see on success?
4. What does the user see on failure?
5. Which test proves it works?

If a change cannot answer all five, it is not ready for V1 implementation.
