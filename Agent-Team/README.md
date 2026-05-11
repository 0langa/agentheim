# Agent-Team

Local-first multi-agent automation runtime for [Agentheim](../README.md).

## Scope

- `Agent-Team/` is the primary system.
- Runtime is local-first, policy-gated, and ledger-backed for inspectable/resumable runs.

## Model configuration

- Runtime is provider-agnostic.
- Providers are configured in a provider registry (`AI_TEAM_PROVIDER_*` env vars).
- Workflow roles bind to logical models:
  - planner
  - executor
  - verifier
  - gatherer, summarizer, reporter (research workflow)
  - indexer, retriever, answerer (documents workflow)

## Install

```powershell
pip install -e .
```

## Environment variables

See `.env.example` for all model roles.

## Core commands

```powershell
agentheim config-dump --redacted
agentheim ping-models
agentheim inspect --repo <path>
agentheim plan "Task text" --repo <path>
agentheim run "Task text" --repo <path> --mode apply
agentheim run "Task text" --repo <path> --mode auto
agentheim run "Task text" --repo <path> --mode ci
agentheim list-runs --repo <path>
agentheim report --repo <path> --run-id <id>
agentheim resume --repo <path> --run-id <id>
```

## Ledger

Run artifacts are written to `.ai-team/runs/<run-id>` under the target repo.

Blocked runs remain resumable from the ledger.

## Safety

- only safe commands auto-run
- patch paths cannot escape repo root
- destructive/deploy/install commands are blocked by default
- optional GitHub, MCP, and web adapters are disabled by default and never required for local operation

## Documentation

- `docs/CLI_RUNBOOK.md`
- `docs/ARCHITECTURE.md`
- `docs/SAFETY.md`
- `docs/TROUBLESHOOTING.md`
