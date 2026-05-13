# Traceability — EVERY CHANGE LEAVES EVIDENCE

Every meaningful change must leave enough evidence for a reviewer to understand what changed, why it changed, and how it was verified.

## Required Change Evidence

For implementation work, include or update:

- code changes
- focused tests for changed behavior
- docs for changed public behavior, commands, architecture, configuration, safety, or workflow expectations
- `docs/CHANGELOG.md` before any commit
- relevant `devtest/` guidance when test structure or recommended commands change

For docs-only or instruction-only work, include:

- local Markdown-link validation
- command/example validation when examples were changed
- explicit note if no code tests were needed

## Canonical Artifact Paths

Agentheim run artifacts live under `.ai-team/runs/<run-id>/` unless a specific integration plan says otherwise. Typical artifacts include:

```text
.ai-team/runs/<run-id>/
    run.json
    ledger.jsonl
    ledger.hash
    config.redacted.json
    context_bundle.md
    plan.md
    tool_calls.jsonl
    policy_decisions.jsonl
    patch.diff
    verification.json
    final_report.md
```

AICtx may still use `.aictx/` internally while it is a reference repository or during compatibility migration. Do not present `.aictx/` as Agentheim's canonical runtime store unless the active AICtx integration phase explicitly requires it.

## What To Report

Final responses and handoffs should identify:

- files changed
- subsystems affected
- tests or smoke checks run
- commands that failed and whether failures are project defects or local environment limits
- docs updated or verified
- remaining risks or unverified assumptions

## Reviewer Questions

Before completion, a reviewer should be able to answer:

- What changed?
- Why was it changed?
- Which subsystem owns the behavior?
- Does it preserve the 7 immutable laws?
- What tests or smoke checks ran?
- Which docs or instructions were updated?
- Are any claims unverified?

If any answer is unclear, the task is not complete.
