# Instruction Priority

Use this precedence order:

1. Current user request
2. `AGENTS.md`
3. `.github/instructions/*.md`
4. `.github/agents/*.agent.md`
5. Repository docs
6. Repo-local skills

If two standing instructions conflict, prefer the simpler, code-grounded reading and remove the stale one instead of stacking exceptions.
