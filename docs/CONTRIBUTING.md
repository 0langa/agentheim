# Contributing to Agentheim

Maintainer-only document. This file describes repository development workflow and is not a product feature contract.

> Development setup, coding standards, PR workflow, and governance for contributors.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Before You Start](#before-you-start)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [How to Contribute](#how-to-contribute)
- [Code Standards](#code-standards)
- [Commit Messages](#commit-messages)
- [Governed Development](#governed-development)
- [Cross-Boundary Changes](#cross-boundary-changes)

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/0langa/agentheim.git
cd agentheim

# 2. Install dependencies
pip install -e .

# 3. Run the test suite
pytest tests\ -q                  # Windows
PYTHONPATH="." pytest tests/ -q   # Linux/Mac

# 4. Run directive governance checks
python scripts/check-agent-instructions.py
```

---

## Before You Start

### Read Binding Instructions

This project is governed by binding repository instructions in `.github/instructions/`. Every contributor and agent must understand:

- **[README.md](../.github/instructions/README.md)** — instruction set overview and read order
- **[00-instruction-priority.md](../.github/instructions/00-instruction-priority.md)** — precedence rules
- **[01-doctrine.md](../.github/instructions/01-doctrine.md)** — repository baseline and architectural boundaries
- **[02-forbidden-behaviors.md](../.github/instructions/02-forbidden-behaviors.md)** — minimal working rules and validation expectations

### Context Preamble for AI Agents

When starting work with an AI agent, paste this preamble:

```markdown
## OPERATING CONTEXT
**Project:** agentheim
**My Subsystem:** [your assigned directory]
**Task:** [description]

### Laws Check
- [ ] No provider-specific logic in core/
- [ ] No workflow-specific logic in core/
- [ ] All tool calls through policy engine
- [ ] Event-sourced, no mutable state
- [ ] Local-first, privacy-respecting
- [ ] Safety by default
- [ ] Progressive disclosure preserved
```

### Run Directive Checks

```bash
# Before committing
python scripts/check-agent-instructions.py

# In CI (blocks merge on failure)
python scripts/check-agent-instructions.py
```

---

## Development Setup

### Requirements

- **Python 3.12+**
- **Git**
- **(Optional) Playwright** for browser tool tests: `playwright install chromium`

### Install in Editable Mode

```bash
pip install -e .
```

### Running Tests

```bash
# Full suite
pytest tests\ -v

# Specific module
pytest tests\test_api_server.py -v

# With coverage
pytest tests\ --cov=core --cov=tools --cov=workflows

# DevTest runner modes
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode narrow
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode full -NoPrompt
```

See [Development & Testing](DEV_TESTING.md) for the complete test reference.

### Running the CLI Locally

```bash
python -m interfaces.cli.cli doctor
python -m interfaces.cli.cli ping-models
python -m interfaces.cli.cli inspect --repo .
```

---

## Project Structure

```
core/           # Generic runtime engine — provider/workflow/tool agnostic
providers/      # Lazy-loaded provider adapters
workflows/      # Workflow packs (coding, research, documents, ...)
tools/          # Mediated tools with policy gating
memory/         # Three-tier memory system
interfaces/     # CLI, TUI, Web UI, API server, Desktop UI
presets/        # Beginner-friendly preset definitions
tests/          # Full test suite
docs/           # Documentation (user guide, API, architecture, governance)
scripts/        # Tooling (directive checks and legacy helpers)
```

**Key rule:** `core/` knows no provider, model, workflow, or tool names. Everything concrete lives in its own subsystem.

> Exception: `core/model_registry.py` holds `DEFAULT_PROVIDER_MAP` as a bootstrapping default. The `ModelRegistry` class remains fully generic.

---

## How to Contribute

### 1. Pick an Issue

- Check [open issues](https://github.com/0langa/agentheim/issues) for `good first issue` or `help wanted`
- Or propose a new feature via an issue first

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

- Follow existing code style (type hints, docstrings for public methods)
- Add tests for new code
- Keep changes focused — one concern per PR
- Respect subsystem boundaries described in [Architecture](ARCHITECTURE.md) and `.github/instructions/`

### 4. Run Checks Before Submitting

```bash
# Tests must pass
pytest tests\ -q

# Directive check must pass
python scripts/check-agent-instructions.py
```

### 5. Submit a PR

- Fill out the [PR template](../.github/PULL_REQUEST_TEMPLATE.md)
- Link related issues
- Keep the description focused on *what* and *why*

---

## Code Standards

### Architecture Invariants

- Core runtime is provider-agnostic, workflow-agnostic, tool-agnostic
- All tool calls go through `core.tool_protocol`
- All provider access goes through `providers.base`
- All workflow execution goes through `workflows.base.Workflow`
- Runs write to `.ai-team/runs/<run-id>/`, but artifact sets vary by workflow/runtime
- All events are append-only in the ledger

### Import Rules

| Module | May Import From | May NOT Import From |
|--------|----------------|-------------------|
| `core/` | `core.*`, `providers.base`, `workflows.base` | Concrete providers, workflow packs, tool implementations, AICtx implementation logic |
| `workflows/` | `core.public_api`, `workflows.base` | Concrete provider adapters |
| `providers/` | `providers.base` | Unnecessary coupling to sibling provider adapters |
| `tools/` | `core.tool_protocol`, `core.public_api` | Unreviewed cross-tool coupling |
| `interfaces/` | Prefer `core.public_api` | New direct imports of unstable `core.*` internals without justification |

### Testing

- Unit tests: >80% coverage for all new code
- Integration tests for all cross-subsystem interactions
- Run `pytest` before submitting PR
- Run `python scripts/check-agent-instructions.py` before submitting docs, instruction, template, skill, or validation changes

### Documentation

- Docstrings for all public methods
- Update relevant docs in `docs/` for user-facing changes
- Add CHANGELOG entry for all changes

---

## Commit Messages

```
[subsystem] Brief description

- What changed
- Why it changed
- Which phase gate it advances (if any)
```

---

## Governed Development

**Rules:**
- Preserve the repository boundaries in `.github/instructions/01-doctrine.md`
- Do NOT add concrete provider, workflow, tool, or AICtx implementation details to `core/`
- Do NOT modify unrelated subsystems without explaining the cross-boundary impact
- Do NOT leave docs, tests, or agent instructions stale after behavior changes

### Governance Update Protocol

When project governance changes:

1. Update the relevant `.github/instructions/*.md` file
2. Update `.github/agents/agentheim-autonomous-engineer.agent.md` only if the stable agent contract changes
3. Update affected docs under `docs/`
4. Update `devtest/all-test-commands.md` if validation commands change
5. Run docs and instruction smoke checks

Do not change governance by editing only prose in a downstream doc.

---

## Cross-Boundary Changes

If your change touches multiple subsystems:

1. Describe the cross-boundary impact in the PR or issue
2. Keep subsystem-owner implications explicit
3. Run the integration tests relevant to the touched boundaries
4. Update docs and instructions in the same change

---

## See Also

- [Architecture](ARCHITECTURE.md) — system design and module overview
- [Development & Testing](DEV_TESTING.md) — complete test reference
- [Repository Baseline](../.github/instructions/01-doctrine.md) — architectural boundaries
- [Working Rules](../.github/instructions/02-forbidden-behaviors.md) — editing and verification rules
