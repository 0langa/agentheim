# Agentheim Agent Baseline

This repository keeps agent guidance intentionally small.

Start here, then read the binding files in [`.github/instructions/`](.github/instructions/):

1. [`.github/instructions/README.md`](.github/instructions/README.md)
2. [`.github/instructions/00-instruction-priority.md`](.github/instructions/00-instruction-priority.md)
3. [`.github/instructions/01-doctrine.md`](.github/instructions/01-doctrine.md)
4. [`.github/instructions/02-forbidden-behaviors.md`](.github/instructions/02-forbidden-behaviors.md)

Use this baseline when working in the repo:

- Inspect code before changing behavior or documentation.
- Keep `core/` generic. Provider, workflow, tool, and interface specifics belong in their own layers.
- Treat docs as secondary to code: update docs when public behavior changes, but do not preserve stale doctrine.
- Run the smallest verification that matches the risk. When changing agent files, instructions, skills, or validation docs/scripts, run `python scripts/check-agent-instructions.py`.

## Product vs Development

Agents must keep these surfaces separate:

- Product/public behavior comes from runtime code, presets, and public docs such as `README.md`, `docs/USER_GUIDE.md`, `docs/CLI-COMMANDS.md`, `docs/API_REFERENCE.md`, `docs/TROUBLESHOOTING.md`, and `docs/SAFETY.md`.
- Development-only guidance comes from `AGENTS.md`, `.github/agents/`, `.github/instructions/`, maintainer docs, tests, `devtest/`, and validation scripts.

Do not treat development-only files as product features, user-facing guarantees, or supported runtime behavior.
