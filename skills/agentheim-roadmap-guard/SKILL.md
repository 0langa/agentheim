---
name: agentheim-roadmap-guard
description: "Validate Agentheim directive governance and architecture boundaries after the roadmap-era shift: .github/instructions integrity, docs accuracy, core-ignorance rules, AICtx hard boundaries, and safety invariants. Use when making non-trivial code, docs, instruction, or integration changes."
---

# Agentheim Governance Guard

Verify that changes remain consistent with Agentheim's binding directive system and architecture boundaries.

## Run Directive Guard

Execute:

```powershell
python scripts/check-agent-instructions.py
```

Treat failures as blocking until docs, instructions, aliases, ignored paths, or references are aligned.

## Validate Boundary Rules

Check changed files for these invariants:

- keep `core/` provider-agnostic, workflow-agnostic, tool-agnostic, and AICtx-agnostic
- keep provider-specific logic under `providers/`
- keep workflow behavior under `workflows/` and presets under `presets/`
- keep policy enforcement explicit in policy/tool layers, not hidden in prompts
- keep the local `AICtx/` reference checkout gitignored

## Validate Runtime Safety Signals

For runtime or orchestration edits, verify at minimum:

- retry semantics remain explicit and bounded
- ledger/event writing remains append-oriented and auditable
- approval/policy pathways stay enforceable
- resume behavior remains deterministic

Run at least `targeted` devtest mode after runtime verification.

## Repair Documentation Drift

If behavior changes, update impacted docs in the same patch:

- `README.md` for GitHub-facing flow changes
- `docs/` for user/developer documentation
- `.github/instructions/` for binding governance changes
- `docs/CHANGELOG.md` before commit

## Legacy Roadmap Note

`scripts/roadmap-check.py` and `phase7` devtest mode are legacy paths. Use them only when investigating roadmap-era behavior or when explicitly requested.

## References

Load `references/guard-checklist.md` for the pre-handoff checklist.

