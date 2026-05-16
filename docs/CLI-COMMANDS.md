# CLI Commands Reference

> Entry points:
> - installed script: `agentheim <command> [options]`
> - repo-local: `python -m interfaces.cli.cli <command> [options]`

The CLI is built with Typer. The lists below are derived from the current command registrations in `interfaces/cli/cli.py`, `interfaces/cli/ctx_commands.py`, `interfaces/cli/provider_commands.py`, and `interfaces/cli/oci_commands.py`.

---

## Root Commands

| Command | Description | Key Options / Arguments |
| --- | --- | --- |
| `config-dump` | Print loaded config as JSON. | `--redacted` / `--raw` |
| `ping-models` | Ping configured models with a deterministic request. | none |
| `inspect` | Inspect a repo and produce a compact context summary. | `--repo`, `--json`, `--write-ledger` |
| `plan` | Build a structured implementation plan without editing files. | `TASK_TEXT`, `--repo`, `--write-ledger`, `--out` |
| `run` | Plan and apply bounded work orders without auto-commit. | `TASK_TEXT`, `--repo`, `--mode`, `--allow-dirty`, `--max-fix-attempts`, `--max-diff-lines`, `--command-timeout`, `--no-tests` |
| `list-runs` | List persisted runs under the repository. | `--repo` |
| `report` | Emit canonical run summary JSON for a run. | `--repo`, `--run-id` |
| `resume` | Resume a run from its ledger. | `--repo`, `--run-id` |
| `presets` | List all available presets. | none |
| `start` | Run a preset with the given inputs. | `PRESET_ID`, `--input key=value` |
| `guided` | Launch the guided TUI preset picker. | none |
| `memory` | Interact with global memory. | `ACTION` = `get|set|history|profile`, `--key`, `--value`, `--model-id` |
| `doctor` | Diagnose configuration and environment issues. | `--skip-connectivity`, `--oci` |
| `mcp-list` | List tools from configured MCP servers. | `--config` |
| `mcp-call` | Invoke an MCP tool directly. | `TOOL_NAME`, `--arg key=value`, `--config` |
| `desktop` | Launch the desktop UI wrapper. | `--port`, `--no-tray` |
| `copy` | Copy a file or directory within the workspace through the filesystem tool. | `SOURCE`, `DESTINATION` |

---

## Provider Commands

| Command | Description |
| --- | --- |
| `provider templates` | List provider setup templates. |
| `provider add` | Add a provider profile entry and initial role binding. |
| `provider list` | List providers and role bindings in a profile. |
| `provider use` | Set the default profile or write the project profile pointer. |
| `provider assign` | Bind a team role to a provider/model. |
| `provider rotate-secret` | Rotate a provider secret. |
| `provider remove` | Remove a provider and its role bindings. |
| `provider test` | Invoke the configured provider for a role with a small test request. |
| `provider import-env` | One-time migration from legacy environment variables. |

Notable options from current help:

- `provider add` supports `--template`, `--model`, `--role`, `--profile`, `--endpoint`, `--auth-mode`, `--api-key`, `--capability`
- `provider assign` supports `ROLE`, `--provider`, `--model`, `--profile`, `--capability`
- `provider test` supports `--role`, `--profile`

---

## Context Commands

| Command | Description | Key Options |
| --- | --- | --- |
| `ctx init` | Initialize repo for context processing. | `--project` |
| `ctx scan` | Scan repository and print inventory summary. | `--project` |
| `ctx run` | Run the full context generation pipeline. | `--project`, `--scope`, `--write`, `--allow-dirty` |
| `ctx verify` | Verify context lock against repository state. | `--project`, `--strict` |
| `ctx status` | Show stale-context detection status. | `--project`, `--strict` |
| `ctx clean` | Remove generated run artifacts. | `--project`, `--run-id`, `--keep-runs` |
| `ctx public-docs impact` | Map source changes to impacted public docs. | `--project`, `--scope` |
| `ctx public-docs update` | Generate patches for impacted public docs. | `--project`, `--scope`, `--write` |

### OCI Subcommands

The `ctx oci` subtree is registered from `interfaces/cli/oci_commands.py`. Use `python -m interfaces.cli.cli ctx oci --help` for the current command set.

---

## Run Modes

`agentheim run --mode` currently accepts:

| Mode | Meaning |
| --- | --- |
| `apply` | default path |
| `auto` | less interactive execution path |
| `ci` | non-interactive CI-oriented path |

The CLI validates only these three mode names.

---

## Privacy And Safety

Privacy and policy concepts exist in code, but the public CLI in this checkout does not expose a top-level privacy-mode selector.

Current user-visible safety behavior includes:

- policy-routed tool invocation
- approval prompts for medium-risk filesystem operations such as `copy`
- denial of high-risk operations through constrained interface paths

---

## Artifacts

Runs write under `.ai-team/runs/<run-id>/`, but the exact artifact set depends on the workflow/runtime. Common files visible in the current repository include:

- `run.json`
- `ledger.jsonl`
- `ledger.hash`
- `tool_calls.jsonl`
- `state_transitions.jsonl`
- `final_report.md`
- `final_report.json`
- workflow-specific diagnostics or summary files

Do not assume every run produces the same artifact inventory.

---

## Quick Examples

```bash
# CLI help
python -m interfaces.cli.cli --help

# Inspect a repo
python -m interfaces.cli.cli inspect --repo .

# Plan work
python -m interfaces.cli.cli plan "Add rate limiting middleware" --repo .

# Run work
python -m interfaces.cli.cli run "Refactor auth module" --repo . --mode apply

# Provider setup
python -m interfaces.cli.cli provider templates
python -m interfaces.cli.cli provider add openai --template openai_v1 --model gpt-4o-mini --role planner
python -m interfaces.cli.cli provider test --role planner

# Context operations
python -m interfaces.cli.cli ctx status --project . --strict
python -m interfaces.cli.cli ctx run --project . --scope changed --write patch
```
