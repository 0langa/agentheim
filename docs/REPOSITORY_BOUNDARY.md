# Repository Boundary

This document classifies the current tree into product-facing surface versus maintainer-only development surface.

The goal is simple: agents and humans should not infer product features from repository-maintenance files.

## Rule

Only these sources should define user-facing behavior:

- runtime code under product modules
- registered presets
- public docs such as `README.md`, `docs/USER_GUIDE.md`, `docs/CLI-COMMANDS.md`, `docs/API_REFERENCE.md`, `docs/TROUBLESHOOTING.md`, and `docs/SAFETY.md`

Everything else is either implementation detail or repository-maintenance material.

## Public Product Surface

These paths belong in a clean public product repo:

| Path | Why it belongs |
| --- | --- |
| `README.md`, `LICENSE`, `SECURITY.md`, `CODE_OF_CONDUCT.md` | Public project entry and policy surface |
| `pyproject.toml`, `uv.lock` | Installation and packaging |
| `agentheim/` | Installed package surface |
| `agents/self_improving/` | Runtime hook subsystem used by `interfaces/run_hooks.py` |
| `config/`, `core/`, `federation/`, `interfaces/`, `marketplace/`, `memory/`, `monitoring/`, `multimodal/`, `presets/`, `providers/`, `tools/`, `workflows/` | Product/runtime implementation |
| `docs/USER_GUIDE.md`, `docs/CLI-COMMANDS.md`, `docs/API_REFERENCE.md`, `docs/TROUBLESHOOTING.md`, `docs/SAFETY.md` | Public usage and support documentation |
| `docs/ARCHITECTURE.md` | Public technical reference for integrators and contributors |
| `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md` | Public repository collaboration metadata |

## Public But Non-Product

These files can stay public if you want open development, but they are not product features and should never be used as feature evidence:

| Path | Why it is non-product |
| --- | --- |
| `CONTRIBUTING.md` | Contributor process |
| `docs/CONTRIBUTING.md` | Maintainer workflow |
| `docs/CHANGELOG.md` | Historical record, not current feature contract |
| `tests/` | Verification artifacts, not supported user surface |
| `scripts/roadmap-check.py` and similar maintenance scripts | Internal validation or migration utilities |

## Maintainer-Only Development Surface

For a strict end-user-facing public repo, these should not be present. If you keep them in the working repository, treat them as private or clearly internal:

| Path | Why it should not define product surface |
| --- | --- |
| `AGENTS.md` | Agent maintainer entrypoint |
| `.github/agents/` | AI-development agent definitions |
| `.github/instructions/` | Development-only standing instructions |
| `.github/mcp.json` | Local maintainer tooling config |
| `.kimi/` | Repo-specific agent rules, memory, and skills |
| `skills/` | Repo-local development skills |
| `devtest/` | Development validation harness |
| `docs/AGENT_OPERATIONS.md` | Maintainer agent guidance |
| `docs/DEV_TESTING.md` | Development-only verification guidance |
| `docs/SUPPORT_MATRIX.md` | Internal support-state classification |
| `docs/TIER1_CONTRACTS.md` | Internal quality contract mapping |
| `docs/superpowers/` | Planning/process artifacts |

## Current Recommendation

If you want a truly product-facing public repo:

1. Keep the product surface and public docs.
2. Move maintainer-only agent instructions, local skill packs, `.kimi/`, and `devtest/` to a private maintainer repo or a separate internal branch/worktree.
3. Keep tests public only if you explicitly want open development. Otherwise they also belong outside the end-user repo.

## Important Distinction Found In Code

Not everything with an "agent" name is development scaffolding.

- `agents/self_improving/` is actual runtime code imported by `interfaces/run_hooks.py`.
- `AGENTS.md`, `.github/agents/`, `.github/instructions/`, `.kimi/`, and repo-local skills are development-governance surfaces.

That distinction should remain explicit.
