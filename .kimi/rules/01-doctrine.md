# PROJECT DOCTRINE — BINDING LAW

## Identity
agentheim (formerly known as local-agent-orchestration) is a preset-driven, local-first AI automation platform. The core is a generic orchestration runtime. Coding is ONE workflow pack among many — not the product identity.

## The 7 Immutable Laws

These laws are ABSOLUTE. Violating any law is an architectural breach that blocks merge.

### Law 1: Core Ignorance
The `core/` directory MUST NOT contain provider names (Grok, OpenAI, Ollama), workflow types (coding, research), agent roles (planner, executor), or tool implementations. Core knows only protocols and registries.

### Law 2: Workflow Pack Autonomy
Workflow packs in `workflows/` define their own agents, steps, policies, and verification. They MUST NOT import provider implementations directly, mutate core state, or bypass the policy engine.

### Law 3: Provider Interchangeability
Provider adapters in `providers/` are lazy-loaded configuration objects. All providers are interchangeable. No provider shapes the architecture.

### Law 4: Progressive Disclosure
The same system serves beginners (preset picker), power-users (configurable settings), and developers (extensible APIs). Complexity is hidden until requested. Never dumb down; never force complexity.

### Law 5: Event-Sourced Truth
All run state derives from an append-only event log. No mutable run state exists outside the ledger. This enables replayability, auditability, and fault recovery.

### Law 6: Local-First Sovereignty
Default operation requires zero external services beyond model APIs. Privacy modes (remote-allowed, local-preferred, local-only, strict-private) are enforced at the policy engine, not advisory.

### Law 7: Safety by Default
All destructive operations require explicit approval. Policies are defined in code, not by models. Side effects are mediated through the tool protocol.



