# Repository Baseline

`agentheim` is a local-first orchestration system with interchangeable providers, policy-gated tools, workflow packs, append-oriented run artifacts, and multiple interfaces.

Keep these boundaries intact:

- `core/` owns generic runtime contracts, registries, policy evaluation, ledgers, and shared execution machinery.
- `providers/` owns provider adapters.
- `workflows/` owns workflow behavior.
- `tools/` owns tool implementations behind the maintained tool protocol and policy path.
- `interfaces/` owns CLI, API, web, and desktop entrypoints.

Additional repo-specific rules:

- Do not hard-code provider, workflow, or tool behavior into `core/`.
- AICtx integration belongs behind the current ContextOps-related boundaries. Treat `../AICtx` as a reference project, not as a second source of standing instructions.
- Prefer current code over historical docs, plans, or changelog-era assumptions.
- Product behavior must be derived from product code and public docs, not from maintainer instructions, tests, devtest utilities, or agent-governance files.
