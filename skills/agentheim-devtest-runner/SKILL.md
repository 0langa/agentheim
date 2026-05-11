---
name: agentheim-devtest-runner
description: Select and execute the right Agentheim validation slice using devtest scripts and pytest subsets, including mode selection, focused -k filters, and post-run cleanup choices. Use when changing core runtime, workflows, providers, tools, interfaces, memory, or presets and you need fast but defensible local validation.
---

# Agentheim DevTest Runner

Run validation in the smallest mode that still covers the risk surface.

## Choose Test Scope

Map the change to the first matching mode:

- Use `narrow` for low-risk CLI or registry touchpoints.
- Use `targeted` for most single-subsystem edits.
- Use `broad` for cross-cutting behavior changes.
- Use `full` for release-level confidence or unknown blast radius.
- Use `phase7` when validating phase-7 hardening slices specifically.

Use `-K` only to speed iteration before running an unfiltered confirming pass.

## Run DevTest Runner

Run from repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode targeted
```

Use optional keyword filtering when iterating:

```powershell
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode targeted -K ledger
```

If the script prompts for optional cleanup/re-run actions, answer conservatively:

- Prefer `N` during normal development to preserve artifacts.
- Use action `1` and `2` only when temp/cache artifacts are causing flaky results.
- Use action `3` only for immediate confirmation reruns.

## Direct Pytest Fallback

If `run-devtest.ps1` needs bypassing for diagnosis, run direct `pytest` commands from `devtest/all-test-commands.md`, then return to the scripted mode for final confirmation.

## Report Validation Outcome

Summarize:

- selected mode and why
- failing test IDs or subsets
- whether failures are pre-existing vs introduced
- next minimal rerun command

## References

Load `references/test-mode-map.md` before picking a mode if the risk surface is unclear.
