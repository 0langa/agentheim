# Architecture

- `Orchestrator` plans bounded work orders.
- `Coder` edits only files allowed by a work order.
- `Verifier` evaluates diffs, command output, and acceptance criteria.
- `RunLedger` stores prompts, outputs, diffs, and reports.
- Optional adapters (`GitHub`, `MCP`, `web`) are capability layers and disabled by default.

## Runtime phases

`INIT -> LOAD_CONFIG -> PREPARE_WORKSPACE -> SCAN_REPOSITORY -> BUILD_CONTEXT_PACK -> PLAN -> EXECUTE_TASK -> BASIC_VERIFY -> VERIFY_TASK -> FIX_LOOP -> FINAL_VERIFY -> FINAL_REPORT -> RESUME_AVAILABLE -> DONE`