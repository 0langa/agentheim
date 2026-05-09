# Safety

- Local-first by default.
- Only `safe` commands auto-run.
- `install`, `destructive`, and `deploy` commands are blocked unless explicitly approved in future extensions.
- Patch paths are constrained to the repo root.
- Diffs are limited by `--max-diff-lines`.
- Secrets are redacted before logging and reporting.
- Optional GitHub, MCP, and web integrations do not block local operation when unavailable.