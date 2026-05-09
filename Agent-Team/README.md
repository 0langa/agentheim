# Agent-Team

Local-first three-agent coding team runtime.

## Scope

- `Agent-Team/` is the primary system.
- Runtime is local-first, policy-gated, and ledger-backed for inspectable/resumable runs.

## Roles

- orchestrator -> `grok-4-20-reasoning`
- coder -> `grok-4-1-fast-reasoning`
- verifier -> `grok-4-20-non-reasoning`

## Install

```powershell
pip install -e .
```

## Environment variables

See `.env.example` for all three model roles.

## Core commands

```powershell
python -m ai_team config-dump --redacted
python -m ai_team ping-models
python -m ai_team inspect --repo <path>
python -m ai_team plan "Task text" --repo <path>
python -m ai_team run "Task text" --repo <path> --mode apply
python -m ai_team run "Task text" --repo <path> --mode auto
python -m ai_team run "Task text" --repo <path> --mode ci
python -m ai_team list-runs --repo <path>
python -m ai_team report --repo <path> --run-id <id>
python -m ai_team resume --repo <path> --run-id <id>
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

- `docs/USAGE.md`
- `docs/ARCHITECTURE.md`
- `docs/SAFETY.md`
- `docs/TROUBLESHOOTING.md`
