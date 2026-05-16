# Tier-1 Journey Contracts

Maintainer-only document. This file maps internal quality targets to code and tests; it is not the primary end-user feature list.

Tier-1 journeys are the baseline user promises derived from the current CLI, API, Web UI, and tests.

| Journey | CLI | API | Web/Desktop | Output Contract | Evidence |
| --- | --- | --- | --- | --- | --- |
| Install and run diagnostics | `doctor`, `doctor --skip-connectivity` | `GET /api/health` | Web `/api/health`; Desktop launches local Web UI | diagnostic table or health response | CLI help/smoke tests, API route tests |
| Add provider and inspect provider state | `provider templates`, `provider add`, `provider list`, `provider assign`, `provider test`, `ping-models` | `GET /api/providers`, `GET /api/providers/templates`, `POST /api/providers`, `POST /api/providers/assign`, `GET /api/models` | Web provider/profile routes | redacted provider/profile information; no raw secrets | config tests, provider CLI/API tests, Web route tests |
| Inspect repository | `inspect --repo <path>` | no dedicated stable inspect route | not a stable Web/Desktop contract | compact repository summary | CLI implementation and smoke coverage |
| Plan repository work | `plan <task> --repo <path>` | workflow execute route exists but is not a frozen plan API | not a stable Web/Desktop contract | structured plan summary and optional JSON output | coding runtime/workflow tests, CLI implementation |
| Run presets | `start <preset>` | `POST /api/presets/{preset_id}/run` | Web run route; Desktop wraps Web UI | async `run_id` and persisted artifacts when workflow writes them | preset registration tests, API/Web route tests |
| Report run status | `report --repo <path> --run-id <id>` | `GET /api/runs/{run_id}` | Web run-status route | canonical run summary JSON | run summary and API/Web tests |
| Resume a run | `resume --repo <path> --run-id <id>` | no stable resume API route | no stable Web/Desktop contract | resumed-step summary or explicit failure reason | resume code and tests |
| Inspect artifacts | `.ai-team/runs/<run-id>/`, `list-runs` | `GET /api/runs/{run_id}` | Web status route | artifact-aware run summary plus on-disk artifacts | resume/run summary tests, run executor/ledger tests |
| Invoke mediated tools | `copy <source> <destination>` for filesystem copy; most tool use is workflow-internal | `POST /api/tools/{tool_id}/invoke` | `POST /api/tools/invoke` | tool result or approval-required payload | tool invocation and approval-flow tests |
| Run context maintenance operations | `ctx init|scan|run|verify|status|clean`, `ctx public-docs impact|update` | `POST /api/ctx/*` routes | Web ctx routes | ContextOps result payloads and summaries | ctx CLI tests and ctx API tests |

## Run State Contract

Current async executor states from `core/run_executor.py`:

| State | Meaning |
| --- | --- |
| `pending` | Submitted but not yet running |
| `running` | Active execution |
| `completed` | Finished without uncaught failure |
| `failed` | Finished with error |
| `cancelled` | Cancelled before completion |

## Artifact Contract

Runs write under `.ai-team/runs/<run-id>/`, but the artifact set varies by workflow/runtime. Common files in the current tree include:

- `run.json`
- `ledger.jsonl`
- `ledger.hash`
- `tool_calls.jsonl`
- `state_transitions.jsonl`
- `final_report.md`
- `final_report.json`

Additional diagnostics, summaries, or context artifacts may appear depending on the workflow.
