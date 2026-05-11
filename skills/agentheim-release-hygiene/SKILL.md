---
name: agentheim-release-hygiene
description: "Apply Agentheim release hygiene for local changes: synchronize devtest command docs, preserve AGENTS.md operational rules, append changelog entries before commits, and perform final smoke validations. Use when preparing a patch for commit or handoff."
---

# Agentheim Release Hygiene

Close patches with consistent validation, documentation, and repository hygiene.

## Required Repository Rules

Apply these repository rules every time:

- update files in `devtest/` when test structure or recommended execution paths change
- append a short technical entry to `CHANGELOG.md` before commit
- treat `devtest/ai_test.ps1` as max two consecutive attempts per validation, each with a hard 120s timeout

## Finalization Workflow

1. Confirm validation path and executed commands are reflected in `devtest/all-test-commands.md` and `devtest/run-devtest.ps1` when relevant.
2. Append one concise entry to `CHANGELOG.md` describing what changed and why.
3. Run the smallest meaningful validation sweep:

```powershell
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode targeted
```

4. If running AI connectivity checks, enforce timeout and retry ceiling exactly.
5. Produce a handoff summary with changed files, test results, and remaining risks.

## AI Connectivity Check Pattern

Use:

```powershell
Measure-Command { powershell -ExecutionPolicy Bypass -File .\devtest\ai_test.ps1 }
```

If elapsed time exceeds 120 seconds, treat as failed attempt.
Stop after two consecutive failed attempts.

## References

Load `references/release-checklist.md` for a commit-ready checklist.
