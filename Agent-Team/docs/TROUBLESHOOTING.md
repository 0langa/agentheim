# Troubleshooting

## Dirty repo blocked

Use `--allow-dirty` only when you intentionally want to work on an already modified tree.

## Failed run

Inspect the ledger:

```powershell
agentheim list-runs --repo <path>
agentheim report --repo <path> --run-id <id>
agentheim resume --repo <path> --run-id <id>
```

## Model issues

Run:

```powershell
agentheim config-dump --redacted
agentheim ping-models
```

## Optional integrations unavailable

Local workflows continue even when `gh`, MCP servers, or web research are unavailable.