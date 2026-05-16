# Working Rules

Avoid these failure modes:

- documenting commands, routes, files, or guarantees that are not present in the current tree
- preserving stale instruction layers just because they already exist
- adding concrete provider, workflow, tool, or AICtx implementation details to `core/`
- bypassing the maintained policy and tool invocation path for side-effecting tool work
- changing public behavior without updating the affected docs
- claiming validation that was not run
- treating maintainer-only docs, tests, agent instructions, or local tooling files as evidence of user-facing product features

For normal work:

- inspect the relevant code first
- keep edits scoped
- do not rewrite unrelated user changes
- run focused verification that matches the blast radius
- run `python scripts/check-agent-instructions.py` after changing agent files, instruction files, or validation docs/scripts
