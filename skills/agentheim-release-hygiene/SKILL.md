---
name: agentheim-release-hygiene
description: "Apply Agentheim release hygiene for local changes: synchronize devtest command docs, preserve AGENTS.md and .github/instructions rules, append docs/CHANGELOG.md entries before commits, and perform final smoke validations. Use when preparing a patch for commit or handoff."
---

# Agentheim Release Hygiene

Close patches with consistent validation, documentation, and repository hygiene.

## Required Repository Rules

Apply these repository rules every time:

- update files in `devtest/` when test structure or recommended execution paths change
- append a short technical entry to `docs/CHANGELOG.md` before commit
- run directive checks after changing docs, GitHub templates, `.github/agents/`, `.github/instructions/`, skills, or validation guidance
- treat `devtest/ai_test.ps1` as max two consecutive attempts per validation, each with a hard 120s timeout

## Finalization Workflow

1. Confirm validation paths and executed commands are reflected in `devtest/all-test-commands.md` and `docs/DEV_TESTING.md` when relevant.
2. Append one concise entry to `docs/CHANGELOG.md` describing what changed and why.
3. Run the smallest meaningful validation sweep.
4. If docs, instructions, GitHub templates, or skills changed, run:

```powershell
python scripts/check-agent-instructions.py
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode directive -NoPrompt
```

5. If running AI connectivity checks, enforce timeout and retry ceiling exactly.
6. Produce a handoff summary with changed files, test results, and remaining risks.

## AI Connectivity Check Pattern

Use a hard timeout of 120 seconds per attempt. Stop after two consecutive failed attempts.

```powershell
$job = Start-Job { powershell -ExecutionPolicy Bypass -File .\devtest\ai_test.ps1 }
if (-not (Wait-Job $job -Timeout 120)) {
    Stop-Job $job
    throw "devtest/ai_test.ps1 timed out after 120 seconds"
}
Receive-Job $job
```

## References

Load `references/release-checklist.md` for a commit-ready checklist.

