# Test Mode Map

## Mode Selection Heuristics

- `narrow`: quick confidence for critical core + CLI + preset smoke.
- `targeted`: default for day-to-day changes across a single subsystem.
- `broad`: high-signal integration pass for cross-module edits.
- `full`: entire test tree; use before major merge/release.
- `phase7`: constrained hardening set for phase-7 verification.

## Trigger Examples

Use `targeted` for:

- edits in `core/` limited to one module
- changes in `tools/` without interface or policy impact
- preset/workflow updates with no runtime contract change

Use `broad` for:

- changes touching both runtime and tooling
- event/ledger/retry/protocol interactions
- interface/API behavior that may cross boundaries

Use `full` for:

- uncertain blast radius
- late-stage integration confidence
- broad refactors

## Quick Commands

```powershell
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode narrow
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode targeted
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode broad
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode full
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode phase7
```
