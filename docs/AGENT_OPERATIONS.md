# Agent Operations

This document explains how agents should operate in Agentheim. Binding rules live in `.github/instructions/`; this file provides rationale, workflow guidance, and examples.

## Directive System

Agentheim uses a layered directive system:

- `AGENTS.md` is the GitHub-facing entry point.
- `.github/agents/agentheim-autonomous-engineer.agent.md` is the main autonomous engineering agent.
- `.github/instructions/*.md` contains binding project rules.
- `skills/` contains task-specific operational helpers.
- `docs/` contains human-readable project documentation.
- `devtest/` contains local validation command references.

Agents must read `.github/instructions/README.md` and every binding instruction file before planning or editing.

## Instruction Priority

The active priority order is:

1. current user request
2. repository `AGENTS.md`
3. `.github/instructions/*.md`
4. `.github/agents/*.agent.md`
5. repository docs
6. skills

If a conflict appears, the agent must stop, cite the conflicting files or rules, and ask for direction.

## Documentation Enforcement

Documentation is part of the implementation. If behavior, commands, paths, configuration, CI, safety, workflow registration, or integration rules change, update the affected docs in the same change.

Historical entries in `docs/CHANGELOG.md` are exempt from stale-link cleanup because they preserve repository history.

## AICtx Reference Checkout

The local `AICtx/` directory is intentionally gitignored. It exists as reference material for the planned AICtx integration.

Agents may inspect it for parity and implementation details, but must not commit it or copy its source into Agentheim without an explicit integration task and boundary plan.

## Validation

For directive, docs, GitHub template, or skill changes, run:

```powershell
python scripts/check-agent-instructions.py
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode directive -NoPrompt
```

For runtime code changes, combine directive checks with focused pytest or devtest modes that match the risk surface.

`scripts/roadmap-check.py` and `phase7` devtest mode are legacy validation paths. Use them only for roadmap-era investigation or explicit user requests.

## Future MCP

MCP support should follow the same governance model:

- MCP instructions belong in `.github/instructions/` when binding.
- MCP usage examples belong in docs.
- MCP validation commands belong in `devtest/`.
- MCP tools must still respect Agentheim policy, approval, privacy, redaction, and traceability rules.

