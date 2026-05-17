# V1 Roadmap

This roadmap is based on the current tracked codebase only. It does not assume unpublished test infrastructure, private maintainer docs, or future architecture work that is not already represented in the product tree.

## V1 Goal

Ship Agentheim as a coherent local-first product around a small number of reliable user journeys:

- set up a provider
- verify the environment
- run a preset successfully
- inspect, plan, run, report, and resume repository work
- use the HTTP API for the same core flows

## Current Product Surface In Code

The current tracked codebase already exposes:

- CLI root commands including `doctor`, `ping-models`, `inspect`, `plan`, `run`, `list-runs`, `report`, `resume`, `guided`, `start`, `presets`, `memory`, `mcp-list`, `mcp-call`, `desktop`, and `copy`
- provider management commands under `provider`
- context pipeline commands under `ctx`
- API routes for:
  - system health and metrics
  - tool listing, invocation, and approval
  - workflow listing, detail, and execution
  - preset listing and execution
  - memory read and write
  - model and provider inspection and provider mutation
  - run polling and live run streaming over SSE and WebSocket
  - context init, scan, run, verify, status, clean, and public-doc update operations
- eight built-in workflows:
  - `coding`
  - `command_assistant`
  - `context_maintainer`
  - `docs_maintenance`
  - `documents`
  - `file_organization`
  - `github_maintenance`
  - `research`
- eight presets:
  - `codebase-assistant`
  - `command-assistant`
  - `context-maintainer`
  - `docs-maintainer`
  - `file-organizer`
  - `github-maintainer`
  - `local-document-chat`
  - `research-report`

## V1 Product Scope

V1 should focus on the smallest set of flows that already have strong representation in the codebase:

### Core V1 Journeys

1. Provider setup and environment verification
2. Repository work loop
3. Document question answering
4. Command generation
5. API access to the same core runtime

### Official V1 Presets

These should be treated as the primary presets for v1:

- `codebase-assistant`
- `local-document-chat`
- `command-assistant`
- `context-maintainer`

These already map to concrete workflows and clear user jobs in the tracked code.

### Expansion Presets

These should remain secondary until the core journeys feel polished:

- `research-report`
- `docs-maintainer`
- `github-maintainer`
- `file-organizer`

They exist in code and should remain usable, but they should not define the first impression of the product.

## Roadmap Phases

### Phase 1: First-Run Success

Goal: a new user can install Agentheim, configure a provider, and complete a first successful run without needing maintainer context.

Focus areas:

- make `provider templates`, `provider add`, `provider assign`, `doctor`, and `ping-models` feel like one coherent onboarding flow
- tighten public docs around provider setup and first-run expectations
- keep failure messages actionable for bad endpoint, auth, or model-role configuration

Done when:

- the provider setup path is obvious from `README.md` and `docs/USER_GUIDE.md`
- `doctor` and `ping-models` are the clear default diagnostics path
- the most common setup errors are covered in `docs/TROUBLESHOOTING.md`

### Phase 2: Repository Work Loop

Goal: make the repository-assistant loop feel like the product center of gravity.

Focus areas:

- `inspect`
- `plan`
- `run`
- `report`
- `resume`
- `codebase-assistant`

Done when:

- the CLI loop is documented as one continuous flow
- outputs and artifacts are explained consistently in public docs
- the codebase assistant feels like the default example of Agentheim in action

### Phase 3: Official Preset Set

Goal: make the official preset set feel intentional rather than merely registered.

Focus areas:

- `codebase-assistant`
- `local-document-chat`
- `command-assistant`
- `context-maintainer`

Work:

- tighten descriptions and examples in public docs
- keep guided questions aligned with the actual preset inputs in code
- ensure each preset has a clear “when to use this” story

Done when:

- the four official presets are the ones highlighted in `README.md` and `docs/USER_GUIDE.md`
- each one has a crisp documented example
- secondary presets are presented as additional capabilities, not equal first-run paths

### Phase 4: API and Interface Consistency

Goal: make the product usable through both CLI and HTTP without surprise.

Focus areas:

- `/api/health`
- `/api/tools`
- `/api/workflows`
- `/api/presets`
- `/api/providers`
- `/api/runs`
- `/api/ctx/*`

Work:

- keep API docs aligned with the current request/response shapes in `interfaces/api_server/app.py`
- make CLI and API terminology match wherever possible
- keep Web/Desktop framed as wrappers over the same underlying product behaviors

Done when:

- public docs describe the API surface without drift
- CLI and API examples cover the same core jobs
- desktop/web descriptions do not overstate capabilities beyond the actual wrapped flows

### Phase 5: Decide What Stays Secondary

Goal: prevent v1 from becoming bloated.

Review these existing code surfaces and decide whether they are core, secondary, or future-facing:

- `research-report`
- `docs-maintainer`
- `github-maintainer` -- future
- `file-organizer`
- distributed workflow support under `workflows/distributed/`
- marketplace support
- multimodal support
- self-improving hooks under `agents/self_improving/`

Done when:

- the public product message is centered on a small number of obvious use cases
- advanced or niche surfaces are documented proportionally
- public docs no longer feel like an index of every subsystem

## V1 Non-Goals

These are present in code or repository history, but should not drive v1:

- turning every existing preset into a first-class product pillar
- leading with distributed orchestration
- leading with marketplace extensibility
- leading with multimodal or experimental surfaces
- expanding the public product story around unpublished maintainer infrastructure

## Product Rule For Future Work

From here on, product work should start with three questions:

1. Which user journey does this improve?
2. Which public surface changes?
3. How will a user know it worked?

If a change cannot answer those three questions, it is probably not v1 product work.
