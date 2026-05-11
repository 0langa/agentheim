# Phase 7 Audit

Last updated: 2026-05-11

## Codebase Inventory

- `core`: generic runtime, event ledger, replay/resume, router, policy, artifacts, public API facade
- `providers`: lazy-loaded provider adapters and provider base protocol
- `tools`: mediated tool implementations, MCP/browser integrations, registry glue
- `workflows`: workflow packs, runtime shims, explicit workflow registration
- `interfaces`: CLI, guided TUI, web UI, desktop UI, API server
- `memory`: working/global/semantic/episodic tiers and backends
- `monitoring`: metrics and health reporting
- `federation`: peer discovery, delegation, relay transport
- `marketplace`: manifest, manager, sandbox
- `presets`: preset registry and preset-facing entrypoints
- `docs`: roadmap, generated architecture docs, install/config/API docs
- `devtest`: local validation runner, command reference, overview tooling

## Roadmap-To-Code Audit

### Baseline before recovery

| Slice | Status before recovery | Evidence |
|---|---|---|
| Slice 1: Event Foundation | `done` | `core/events.py`, hash/index/checkpoint ledger support existed and targeted ledger tests passed |
| Slice 2: Runtime Engine | `done` | `workflow_runner`, `retry_engine`, `step_budget`, `error_classification` existed and targeted runtime tests passed |
| Slice 3: Artifacts & Protocols | `done` | `artifact_store`, `context_packer`, `agent_protocol`, `public_api` existed and targeted tests passed |
| Slice 4: Boundaries & Loading | `partial` | interfaces mostly migrated, providers lazy-loaded, but workflow-facing modules still imported `core.*` internals and workflow registration still relied on import side effects |
| Slice 5: Safety & Privacy | `done` | policy/privacy/approval suites passed in targeted validation |
| Slice 6: Advanced Routing & Resume | `partial` | router health TTL bug failed full suite; CLI `resume` surface was still a JSON dump; replay/resume internals existed |

### Current status after recovery

| Slice | Current status | Notes |
|---|---|---|
| Slice 1: Event Foundation | `done` | validated via ledger/event gate suites |
| Slice 2: Runtime Engine | `done` | validated via runtime engine suites and full repo run |
| Slice 3: Artifacts & Protocols | `done` | validated via artifact/protocol suites |
| Slice 4: Boundaries & Loading | `done` | workflow-facing modules moved to `core.public_api`; explicit workflow registration replaces import-time registry mutation; checker enforces interface and workflow boundaries |
| Slice 5: Safety & Privacy | `done` | validated via policy/privacy/approval suites |
| Slice 6: Advanced Routing & Resume | `done` | router TTL fixed, replay/resume tests green, CLI resume now reconstructs workflow-based runs from ledger metadata |

## Where Work Stopped Last Time

### Proof trail

- Last committed milestones:
  - `d0129fc` — Phase 6 full production implementation
  - `db02e86` — roadmap/docs update defining Phase 7
- Dirty worktree at recovery start already contained:
  - untracked/new Phase 7 runtime files in `core/`
  - new Phase 7 tests under `tests/`
  - partial checker/devtest/doc updates
- First observed blockers at recovery start:
  - `tests/test_cascading_router.py::TestCascadingRouterHealth::test_health_ttl_expires` failed
  - `python scripts/roadmap-check.py --phase 7 --ci` failed on a false positive in `core/resume.py`
  - workflow-facing modules still had many direct `core.*` imports
  - full suite still failed on an environment-sensitive desktop UI test

### Conclusion

Work had progressed well past the early Phase 7 slices before the interruption. The repo was not missing the Phase 7 subsystems; it was stuck in late-stage integration. Slice 6 had been partially implemented, but the remaining work was finish-grade integration, boundary cleanup, validation hardening, and release-truth documentation rather than greenfield subsystem construction.

## Release Blockers

### Blockers that existed at recovery start

- P0: `CascadingRouter` health TTL semantics were wrong, so full-suite routing validation was not green.
- P0: Phase 7 architecture checker still produced a false positive and did not yet enforce workflow-facing public API boundaries.
- P0: workflow registration still relied on import side effects, which kept the boundary story inconsistent.
- P0: release-facing docs still claimed Phase 6 / `372` passing tests.

### Current blocker status

- No known P0 prerelease blockers remain.
- Residual non-blocking validation notes:
  - `3` skipped tests are optional desktop GUI environment checks.
  - one Pydantic `ArbitraryTypeWarning` remains around lock validation in tests.
  - the local Python environment emits a `requests` dependency warning unrelated to repository code changes.

## Optimization Backlog

### P1

- Normalize the `requests`/`urllib3` environment mismatch in the local validation environment to remove noise from release runs.
- Eliminate the `ArbitraryTypeWarning` by explicitly marking lock fields as skip-validated or otherwise typing them safely.
- Tighten generated overview/report tooling so `PROJECT_OVERVIEW.md` and `docs/generated/*` can be refreshed deterministically without stale or misleading metadata.
- Expand CLI resume coverage with explicit tests for workflow-based resumed runs and unsupported run shapes.

### P2

- Reduce startup coupling further by auditing remaining workflow agent internals that still depend on internal runtime modules not yet exposed through the facade.
- Improve devtest output ergonomics and machine-readable summaries for release signoff.
- Review desktop UI fallback loops (`while True`) for lower CPU idle behavior in non-browser fallback mode.

## Validation Record

### Recovery-stage diagnostics

- `python scripts/roadmap-check.py --phase 7 --ci`
  - before recovery: failed with one Level 3 false positive in `core/resume.py`
  - after recovery: passed
- `pytest -q tests/test_events.py tests/test_ledger_hash.py tests/test_ledger_index.py tests/test_ledger_checkpoints.py tests/test_retry_engine.py tests/test_step_budget.py tests/test_workflow_runner.py tests/test_workflow_runner_parallel.py tests/test_public_api.py tests/test_provider_lazy_loading.py tests/test_policy_engine.py tests/test_resume.py`
  - passed at recovery start: `131 passed`
- `pytest -q --maxfail=1`
  - before recovery: failed first in `tests/test_cascading_router.py::TestCascadingRouterHealth::test_health_ttl_expires`
  - intermediate run: failed first in `tests/test_desktop_ui.py::TestDesktopUI::test_tkinter_import`
  - final run: passed

### Final validation commands and outcomes

- `pytest -q tests/test_workflow_isolation.py tests/smoke/test_cli.py tests/test_web_ui.py tests/test_api_server.py tests/test_import_linting.py`
  - passed: `59 passed`
- `powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode phase7 -NoPrompt`
  - passed: `270 passed`; architecture gate passed
- `powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode broad -NoPrompt`
  - passed:
    - functional subset: `526 passed, 1 skipped`
    - memory suite: `103 passed`
- `powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode full -NoPrompt`
  - passed: `692 passed, 3 skipped, 1 warning`
- `pytest -q`
  - final green pass: `692 passed, 3 skipped, 1 warning`

## Current Release Readiness Assessment

Phase 7 is complete by the repository’s executable gates:

- roadmap checker passes
- Phase 7 targeted suites pass
- workflow and interface boundary tests pass
- full pytest suite passes
- broad and full `devtest` modes pass
- release-facing README status now matches the validated repository state

This repository is at prerelease-ready quality for local validation and packaging, with only non-blocking cleanup items remaining.
