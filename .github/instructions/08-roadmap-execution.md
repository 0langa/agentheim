# Roadmap Execution

`BASELINE-ROADMAP.md` is the active baseline roadmap. It replaces deleted legacy roadmap directories and older phase-gate assumptions.

## Required Reads

Before planning or executing roadmap work, read:

- `BASELINE-ROADMAP.md`
- `docs/SUPPORT_MATRIX.md`
- `docs/TIER1_CONTRACTS.md`
- `docs/DEV_TESTING.md`
- `live-ai-testing.md`

Use current repository evidence over memory, summaries, or historical changelog entries.

## Provider Priority

Harden provider/model support in this order unless the user explicitly changes it:

1. OpenAI-compatible providers, including Azure-compatible endpoints
2. Google AI services: Gemini API, Vertex AI, and Google Cloud paths
3. Self-hosted OSS models via localhost or cloud VM endpoints

Other integrated providers must remain cleanly registered and theoretically functional, but they are not Tier-1 hardening targets until the roadmap says so.

## Support-State Evidence

Do not mark any provider, preset, interface, tool, workflow, or advanced subsystem as stable or polished without evidence in the same change.

A support-state promotion requires:

- implementation or configuration path
- focused tests for the changed contract
- docs update in the owning user/API/operator docs
- `docs/SUPPORT_MATRIX.md` update
- `docs/TIER1_CONTRACTS.md` update when a Tier-1 journey changes
- live evidence update when the claim depends on real provider connectivity
- `docs/CHANGELOG.md` entry
- `.kimi/memory.jsonl` update after significant milestone or architecture change

If live provider validation was not run, say so. Do not infer live support from mocks.

## Batch Discipline

Roadmap work must be split into small, reviewable batches with explicit success gates. A batch should normally complete one phase slice or one contract lane, not multiple unrelated goals.

For every roadmap batch:

- state the phase/slice being implemented
- identify affected contracts before editing
- preserve core ignorance, policy mediation, ledger truth, and local-first privacy
- keep docs, tests, skills, and instructions aligned
- leave the repo in a state where the next agent can continue from the roadmap

Do not expand advanced surfaces such as marketplace, federation, self-improving agents, or distributed workers until Phase 8 explicitly promotes or retires that surface.

## Required Gates

Use the smallest focused tests that cover the changed code, then run the baseline gate for roadmap-affecting changes:

```powershell
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode baseline -NoPrompt
```

For docs, instruction, skill, GitHub template, or validation-command changes, also run:

```powershell
python scripts/check-agent-instructions.py
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode directive -NoPrompt
```

`scripts/roadmap-check.py` and `phase7` devtest mode are legacy validation paths. Use them only for historical investigation or explicit user requests.
