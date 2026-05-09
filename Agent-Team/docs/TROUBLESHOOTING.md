# Troubleshooting

## Dirty repo blocked

Use `--allow-dirty` only when you intentionally want to work on an already modified tree.

## Failed run

Inspect the ledger:

```powershell
python -m ai_team list-runs --repo <path>
python -m ai_team report --repo <path> --run-id <id>
python -m ai_team resume --repo <path> --run-id <id>
```

## Model issues

Run:

```powershell
python -m ai_team config-dump --redacted
python -m ai_team ping-models
```

## Optional integrations unavailable

Local workflows continue even when `gh`, MCP servers, or web research are unavailable.