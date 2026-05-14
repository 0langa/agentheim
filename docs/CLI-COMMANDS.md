# CLI Commands Reference

> **Entry points**
> - Global install: `agentheim <command> [options]`
> - Repo-local (development): `python -m interfaces.cli.cli <command> [options]`

The Agentheim CLI is built with [Typer](https://typer.tiangolo.com/). All commands exit with code `0` on success and non-zero on failure.

---

## Root Commands (`agentheim`)

| Command | Description | Key Options / Arguments |
|---------|-------------|------------------------|
| `config-dump` | Print loaded config as JSON. | `--redacted` / `--raw` (default: redacted) |
| `ping-models` | Ping every configured model with a tiny deterministic request. | — |
| `inspect` | Inspect a repo and produce a compact context summary. | `--repo` *(required)*, `--json`, `--write-ledger` |
| `plan` | Build a structured implementation plan **without** editing files. | `TASK_TEXT`, `--repo` *(required)*, `--write-ledger`, `--out <file>` |
| `run` | Plan and apply bounded work orders (no auto-commit). | `TASK_TEXT`, `--repo` *(required)*, `--mode` (default: `apply`), `--allow-dirty`, `--max-fix-attempts` (default: `0`), `--max-diff-lines` (default: `1200`), `--command-timeout` (default: `120`), `--no-tests` |
| `list-runs` | List all runs stored in a repository. | `--repo` *(required)* |
| `report` | Show the full report for a completed run. | `--repo` *(required)*, `--run-id` *(required)* |
| `resume` | Resume a blocked or incomplete run from its ledger. | `--repo` *(required)*, `--run-id` *(required)* |
| `presets` | List all available presets. | — |
| `start` | Run a preset with the given inputs. | `PRESET_ID`, `--input key=value` *(repeatable)* |
| `guided` | Launch the interactive TUI preset picker. | — |
| `memory` | Interact with global memory (Tier 3). | `ACTION` (`get` \| `set` \| `history` \| `profile`), `--key`, `--value`, `--model-id` |
| `doctor` | Diagnose common configuration and environment issues. | `--skip-connectivity`, `--oci` |
| `mcp-list` | List MCP tools from configured servers. | `--config` (default: `.ai-team/mcp.json`) |
| `mcp-call` | Invoke an MCP tool directly. | `TOOL_NAME`, `--arg key=value` *(repeatable)*, `--config` |

---

## Context Operations (`agentheim ctx`)

| Command | Description | Key Options |
|---------|-------------|-------------|
| `ctx init` | Initialize a repo for context processing. | `--project` (default: `.`) |
| `ctx scan` | Scan repository and print an inventory summary. | `--project` (default: `.`) |
| `ctx run` | Run the full context-generation pipeline. | `--project` (default: `.`), `--scope` (default: `full`), `--write` (default: `patch`), `--allow-dirty` |
| `ctx verify` | Verify the context lock against the repository state. | `--project` (default: `.`), `--strict` |
| `ctx status` | Show stale-context detection status. | `--project` (default: `.`), `--strict` |
| `ctx clean` | Remove generated run artifacts. | `--project` (default: `.`), `--run-id`, `--keep-runs` |

### Public Docs Impact (`agentheim ctx public-docs`)

| Command | Description | Key Options |
|---------|-------------|-------------|
| `ctx public-docs impact` | Map source changes to impacted public documentation. | `--project` (default: `.`), `--scope` (default: `full`) |
| `ctx public-docs update` | Generate patches for impacted public docs. | `--project` (default: `.`), `--scope` (default: `changed`), `--write` (default: `patch`) |

### OCI Diagnostics (`agentheim ctx oci`)

> Requires `pip install agentheim[oci]`.

| Command | Description | Key Options |
|---------|-------------|-------------|
| `ctx oci doctor` | Run OCI readiness checks. | `--project` (default: `.`) |
| `ctx oci snapshot create` | Create a deterministic snapshot. | `--project` (default: `.`), `--run-id` *(optional)* |
| `ctx oci snapshot verify` | Verify snapshot integrity. | `--project` (default: `.`) |
| `ctx oci bundle create` | Create a result bundle for a run. | `--project` (default: `.`), `--run-id` *(required)* |
| `ctx oci bundle verify` | Verify result bundle integrity. | `--project` (default: `.`), `--run-id` *(required)* |

---

## Provider Management (`agentheim provider`)

| Command | Description | Key Options / Arguments |
|---------|-------------|------------------------|
| `provider templates` | List supported provider setup templates. | — |
| `provider add` | Add a provider and store its secret securely. | `PROVIDER_ID`, `--template` / `-t` *(required)*, `--model` *(required)*, `--role` (default: `planner`), `--profile` (default: `default`), `--endpoint`, `--auth-mode`, `--api-key`, `--capability` / `-c` (default: `text`, `json`) |
| `provider list` | List providers and role bindings in a profile. | `--profile` |
| `provider use` | Set the default or project profile pointer. | `PROFILE`, `--project` *(flag)* |
| `provider assign` | Bind a team role to a model. | `ROLE`, `--provider` *(required)*, `--model` *(required)*, `--profile` (default: `default`), `--capability` / `-c` (default: `text`, `json`) |
| `provider rotate-secret` | Rotate a provider's stored secret. | `PROVIDER_ID`, `--profile` (default: `default`), `--api-key` |
| `provider remove` | Remove a provider and delete its secret. | `PROVIDER_ID`, `--profile` (default: `default`) |
| `provider test` | Test provider connectivity for a role. | `--role` (default: `planner`), `--profile` (default: `default`) |
| `provider import-env` | One-time migration from legacy provider env vars. | `--profile` (default: `default`) |

---

## Run Modes

Used with `agentheim run --mode <mode>`.

| Mode | Behavior |
|------|----------|
| `apply` | **(default)** Plan, review, and apply changes. Stops for human approval on risky operations. |
| `auto` | Fully autonomous. Applies changes and runs verification without human intervention. |
| `ci` | Non-interactive, optimized for CI pipelines. Fails fast on any policy violation or test failure. |

---

## Privacy Modes

Agentheim enforces privacy through structured modes (defined in `core/privacy_enforcer.py`).

| Mode | Behavior |
|------|----------|
| `standard` | Default. Standard operation with no extra restrictions. |
| `local_only` | Blocks all network tools (e.g., `http.*`, `git.push`, `git.clone`). |
| `strict_private` | Blocks access to sensitive file paths (keys, certs, env files, secrets, tokens). |
| `encrypted` | Blocks sensitive paths **and** forces redaction of all parameters in logs and audits. |

---

## Artifacts

Every run produces artifacts under `.ai-team/runs/<run-id>/` inside the target repository:

| Artifact | Description |
|----------|-------------|
| `run.json` | Run metadata |
| `ledger.jsonl` | Append-only event log |
| `ledger.hash` | SHA-256 hash chain for tamper detection |
| `config.redacted.json` | Configuration (secrets redacted) |
| `context_bundle.md` | Human-readable context snapshot |
| `plan.md` | Execution plan |
| `tool_calls.jsonl` | All tool invocations |
| `policy_decisions.jsonl` | Policy evaluation results |
| `patch.diff` | File changes (if applicable) |
| `verification.json` | Verification results |
| `final_report.md` | Human-readable final report |

---

## Quick Examples

```bash
# Dump current config (redacted)
agentheim config-dump

# Inspect a repo
agentheim inspect --repo ./my-project --write-ledger

# Plan a task without touching files
agentheim plan "Add rate limiting middleware" --repo ./my-project

# Run a task in apply mode (default)
agentheim run "Refactor auth module" --repo ./my-project --mode apply

# Run in CI mode with no tests
agentheim run "Fix lint errors" --repo ./my-project --mode ci --no-tests

# List runs and view a report
agentheim list-runs --repo ./my-project
agentheim report --repo ./my-project --run-id 20260115-120000

# Resume a blocked run
agentheim resume --repo ./my-project --run-id 20260115-120000

# Initialize and run context pipeline
agentheim ctx init --project ./my-project
agentheim ctx run --project ./my-project --scope changed --write apply

# Check context status
agentheim ctx status --project ./my-project --strict

# Add an OpenAI provider
agentheim provider add openai -t openai_v1 --model gpt-4o-mini --role planner

# List providers
agentheim provider list

# Test connectivity
agentheim provider test --role executor

# Run a preset
agentheim start codebase_assistant --input repo=./my-project

# Check environment health
agentheim doctor --oci

# List MCP tools
agentheim mcp-list --config .ai-team/mcp.json

# Call an MCP tool
agentheim mcp-call filesystem.read --arg path=./README.md
```
