# Agent Operations

Maintainer-only document. This file describes repository workflow and agent governance. It does not define product features.

This repo now keeps agent guidance intentionally small. The goal is to reduce inherited behavior and keep agents anchored to current code.

## Active Surfaces

- `AGENTS.md` is the top-level entry point.
- `.github/agents/agentheim-autonomous-engineer.agent.md` is the GitHub agent definition.
- `.github/instructions/` contains the minimal standing rules.
- `docs/` is human-facing explanation, not a second instruction stack.
- repo-local skills are not part of the baseline contract and may be absent.

## Baseline Approach

Agents working here should:

- inspect code before editing
- prefer simple, local changes over adding process
- keep `core/` generic and push concrete behavior to the right subsystem
- update docs when public behavior changes
- use focused verification instead of ritual full-suite runs by default

## AICtx Note

AICtx still lives in the workspace project at `../AICtx`. It is implementation context, not a binding source of repo behavior. Use it as reference material when needed and keep integration behind current ContextOps-related boundaries.

## Validation

When changing agent files, instructions, or validation docs/scripts, run:

```powershell
python scripts/check-agent-instructions.py
```

For code changes, add the smallest relevant pytest or `devtest` command from [DEV_TESTING.md](DEV_TESTING.md).
