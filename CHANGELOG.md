# Changelog

## 2026-05-09

### cc2059b
- Added initial local CLI runner using Grok-4-1-fast-reasoning.
- Established base command execution path for single-agent workflow.

### cc78c78
- Restructured repository layout around `Agent-Team`.
- Removed absolute-path coupling from persisted artifacts for move/rename safety.

### fb5e158
- Refactored provider/model wiring toward provider-agnostic registry flow.
- Introduced workflow-pack direction and strengthened runtime abstraction boundaries.

### f1cdc21
- Added `devtest/ai_test.ps1` for live role-model connectivity checks.
- Expanded `devtest` command surface for narrow/targeted/broad/full testing flows.

### unreleased (working tree)
- Added interactive `Y/N/A` post-run actions in `devtest/run-devtest.ps1`.
- Added timeout/retry policy guidance in `AGENTS.md` for `devtest/ai_test.ps1`.
- Renamed docs usage file to `Agent-Team/docs/CLI_RUNBOOK.md`.
- Added centralized repo-level agent rules and evolving `devtest` governance.
- Fixed cross-platform patch path normalization for Windows-style separators.
- Fixed `ai_team/workflows/base.py` provider creation call to match registry interface.
- Made `ModelRegistry` model mapping generic over configured model entries (not hardcoded IDs).
- Added optional `AI_TEAM_MODELS_JSON` for explicit model registry definitions.
- Added legacy compatibility capabilities so planner/executor/verifier resolution works.
- Switched neutral default model placeholders and removed Grok-implied defaults from `.env.example`.
- Added lazy provider class loading in registry to avoid eager provider imports.
