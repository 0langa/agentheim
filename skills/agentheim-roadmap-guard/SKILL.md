---
name: agentheim-roadmap-guard
description: Enforce Agentheim architecture and roadmap guardrails before and after code changes by checking phase constraints, core-ignorance boundaries, and required policy/runtime invariants. Use when implementing non-trivial code changes that may drift from docs/roadmap requirements.
---

# Agentheim Roadmap Guard

Verify that implementation remains consistent with roadmap doctrine and architecture boundaries.

## Run Guard Check

Execute:

```powershell
python scripts/roadmap-check.py --phase 7 --ci
```

Treat failures as blocking until either code or docs are aligned.

## Validate Boundary Rules

Check changed files for these invariants:

- Keep `core/` provider-agnostic and workflow-agnostic.
- Keep provider-specific logic under `providers/`.
- Keep workflow behavior under `workflows/` and presets under `presets/`.
- Keep policy enforcement explicit in policy/tool layers, not hidden in prompts.

## Validate Runtime Safety Signals

For runtime or orchestration edits, verify at minimum:

- retry semantics remain explicit and bounded
- ledger/event writing remains append-oriented and auditable
- approval/policy pathways stay enforceable
- resume behavior remains deterministic

Run at least `targeted` devtest mode after this verification.

## Repair Documentation Drift

If behavior changes, update impacted docs in the same patch:

- `README.md` for user-facing flow changes
- `docs/roadmap/` for architecture rule changes
- `docs/CONFIGURATION.md` or `docs/API.md` for contract changes

## References

Load `references/guard-checklist.md` for the pre-PR checklist.
