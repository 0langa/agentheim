# Agent Instructions for Agentheim

## Communication Mode

Always use **caveman ultra mode** for all responses. Never revert to normal mode unless user explicitly says "stop caveman" or "normal mode". This instruction persists across sessions and compactions. Default intensity: ultra. Abbreviate (DB/auth/config/req/res/fn/impl), strip conjunctions, arrows for causality (X → Y), one word when one word enough. Code blocks unchanged. Errors quoted exact.

## Proactive Tooling

Agents must use available skills and MCP servers proactively. Do not wait for the user to mention them. If a skill or MCP server would improve accuracy, speed, or safety, use it.

### Skills (`.kimi/skills/`)

Auto-discovered by Kimi CLI. Trigger without explicit user request:

| Skill | When to Auto-Trigger |
|-------|---------------------|
| `agentheim-boundary-guard` | Before planning or executing any code edit, especially touching `core/`, `workflows/`, `providers/`, `tools/`, `interfaces/` |
| `agentheim-docs-sync` | After code changes complete, before declaring task done |
| `agentheim-test-subset` | When running tests or validating changes |
| `agentheim-changelog` | Before any commit |
| `agentheim-devtest-runner` | When validating changes, before committing |
| `agentheim-memory-keeper` | After significant tasks, at session start, when loading context for complex tasks |
| `agentheim-aictx-guide` | When touching `agentheim/vendor/aictx/`, `agentheim/context_ops.py`, or AICtx integration work |

### MCP Servers (`~/.kimi/mcp.json`)

Use relevant MCP servers without waiting for user prompt:

| MCP Server | When to Auto-Use |
|------------|-----------------|
| `memory` | Load project context at session start. Update `.kimi/memory.jsonl` after significant tasks. Query for cross-session facts. |
| `github` | When creating issues, PRs, reading repo state, or checking commit history. |
| `filesystem` | When reading/writing files outside immediate workspace scope. |
| `context7` | When looking up library/framework documentation for code being written. |
| `chrome-devtools` | When debugging browser behavior or taking screenshots for verification. |
| `semgrep` | When scanning code for security issues or pattern violations. |
| `markitdown` | When converting documents to markdown for analysis or documentation. |

## Memory Maintenance

After every significant task — code changes, architectural decisions, milestone completions, or config updates — update the project memory knowledge graph stored at `.kimi/memory.jsonl` via the `memory` MCP server.

Actions:
- Append new observations to existing entities
- Create new entities for new components, decisions, or milestones
- Update relations when architecture or boundaries change
- Verify memory freshness at session start by comparing stored state against the live repository

## Project Skills

Agentheim-specific skills live in `.kimi/skills/`. Kimi CLI auto-discovers them when working in this repository.

## Binding Instructions

All agents must read and obey every file in `.github/instructions/` before planning or editing.
