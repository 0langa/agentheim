# Agent Instructions For Agentheim

This file is the GitHub-facing entry point for agents working in this repository.

## Binding Instructions

All agents must read and obey every file in `.github/instructions/` before planning or editing:

- `.github/instructions/README.md`
- `.github/instructions/00-instruction-priority.md`
- `.github/instructions/01-doctrine.md`
- `.github/instructions/02-forbidden-behaviors.md`
- `.github/instructions/03-traceability.md`
- `.github/instructions/04-AICtx-integration.md`
- `.github/instructions/05-documentation-integrity.md`
- `.github/instructions/06-tooling-and-verification.md`

Those files are binding project rules. They cannot be ignored, skipped, or treated as optional context.

## Main Agent

The primary autonomous engineering agent is:

- `.github/agents/agentheim-autonomous-engineer.agent.md`

Use it for implementation, refactoring, debugging, docs maintenance, verification, and AICtx integration work.

## Current Project References

- `docs/README.md` — documentation index
- `docs/ARCHITECTURE.md` — current system layout and boundaries
- `docs/DEV_TESTING.md` — test and smoke-check guidance
- `docs/AGENT_OPERATIONS.md` — human-readable guide to the directive system
- `docs/AICTX_INTEGRATION_PLAN.md` — AICtx integration milestone plan
- `docs/CHANGELOG.md` — canonical changelog
- `REPOSITORY_AUDIT_REPORT.md` — historical audit findings and risk context

## Local AICtx Reference

The original AICtx repository may be present at `AICtx/`. It is intentionally gitignored and exists only as local reference material until an explicit integration task imports or adapts code.

Agents working on AICtx integration must follow `.github/instructions/04-AICtx-integration.md`.

## Repository Rules

- Keep `core/` generic and free of concrete provider, workflow, tool, and AICtx implementation details.
- Use Agentheim's provider, policy, tool, workflow, and ledger systems instead of creating parallel paths.
- Keep root GitHub-facing files useful: `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, and this file.
- Keep `docs/` accurate and current when behavior, commands, architecture, or file paths change.
- Update `devtest/` guidance when recommended local validation commands change.
- Append to `docs/CHANGELOG.md` before any commit.

## Required Validation Habit

Before completing work, run relevant tests or smoke checks. For docs and instruction changes, run `python scripts/check-agent-instructions.py` or the directive devtest mode documented in `devtest/all-test-commands.md`.
