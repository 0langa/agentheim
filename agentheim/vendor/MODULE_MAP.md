# AICtx Module Map — `agentheim/vendor/aictx/`

> Living document. Updated as integration milestones progress.

## Integration Status

| Milestone | Scope | Status |
|-----------|-------|--------|
| M0 | Architecture freeze, ADR-001 | ✅ Done |
| M1 | Source import, boundary definition, ContextOps API | ✅ Done |
| M2 | Context domain integration behind ContextOps | ✅ Done |
| M3 | Workflow/preset/CLI exposure | ✅ Done |
| M4 | Context-aware workflow adoption | ✅ Done |
| M5 | Public-docs impact integration | ✅ Done |
| M6 | Runtime/storage convergence | ✅ Done — all writes go to `.ai-team/runs/`; `.aictx/runs/` legacy readable only |
| M7 | Provider unification | ✅ Done — `run_local_context_pipeline()` requires injected provider; `llm/providers.py` emptied |
| M8 | OCI/remote backend adoption | ✅ Done — diagnostic commands wired; snapshot/bundle artifacts registered in `ArtifactStore`; remote execution out of scope |
| M9 | Decommissioning vendor duplicates | ✅ Done — vendor copy trimmed to library modules only; external project remains standalone |

---

## Module Disposition

### `cli.py` — Standalone CLI
- **M1:** Preserved as-is.
- **M3:** Thin wrapper around `agentheim ctx <subcommand>`.
- **M9:** Removed from vendor copy. External project at `../AICtx` remains independent.

### `config.py` — Configuration models
- **M1:** Preserved.
- **M2+:** Agentheim surfaces may inject overrides; AICtx config remains the internal schema.

### `errors.py` — Error taxonomy
- **M1:** Preserved.
- **M2+:** Mapped to Agentheim error hierarchy where appropriate.

### `_logging.py` — Rich logging setup
- **M1:** Preserved, renamed from `logging.py` to avoid stdlib shadowing.

### `context/` — Context generation domain
| File | Role | Disposition |
|------|------|-------------|
| `agents_md.py` | `AGENTS.md` generation | Preserved; called by ContextOps writer |
| `compressor.py` | Context compression | Preserved |
| `fact_extractor.py` | LLM fact extraction | Preserved |
| `lockfile.py` | Lockfile I/O | Preserved; Agentheim reads/writes same schema |
| `pipeline.py` | Local Phase-1 orchestration | Preserved; wrapped by ContextOps.generate |
| `planner.py` | Shard selection planner | Preserved |
| `writer.py` | Context shard writer | Preserved |

### `git/` — Git subprocess wrappers
- **M1:** Preserved; subprocess calls added to `SUBPROCESS_EXEMPTIONS`.
- **M2+:** May be routed through Agentheim `tools/git/` protocol if policy gating is required.

### `io/` — File I/O utilities
| File | Role | Disposition |
|------|------|-------------|
| `files.py` | Safe file writes | Preserved |
| `jsonl.py` | JSONL helpers | Preserved |
| `patches.py` | Unified-diff builder | Preserved; subprocess call exempted |

### `llm/` — Provider abstraction
| File | Role | Disposition |
|------|------|-------------|
| `base.py` | `ModelProvider` ABC + `ChatRequest`/`ChatResponse` | Preserved; `AgentheimToAictxAdapter` bridges Agentheim providers when injected, but AICtx default path still uses `llm/` stack |
| `dry_run.py` | Dry-run provider | Preserved |
| `oci_genai.py` | OCI GenAI provider | Preserved |
| `providers.py` | Provider factory | Preserved |
| `transfer.py` | Transfer-preflight / token estimator | Preserved |

**Provider Interface Delta (M1 analysis):**

| Aspect | AICtx (`llm/base.py`) | Agentheim (`providers/base.py`) |
|--------|----------------------|--------------------------------|
| Request type | `ChatRequest` (dataclass) | `ModelRequest` (Pydantic) |
| Request fields | `system_prompt`, `messages`, `temperature`, `max_output_tokens`, `json_schema`, `run_id`, `purpose` | `role`, `system_prompt`, `user_prompt`, `temperature`, `max_output_tokens` |
| Response type | `ChatResponse` (dataclass) | `ModelResponse` (Pydantic) |
| Response fields | `content`, `finish_reason`, `input_tokens`, `output_tokens` | `role`, `model`, `provider`, `content`, `raw` |
| Provider methods | `chat()`, `count_tokens()`, `metadata()` | `invoke()` |
| Config injection | None (provider constructs itself) | `AgentModelConfig` passed to `__init__` |

**Decision:** `AgentheimToAictxAdapter` (in `agentheim/provider_adapter.py`) written in M7. Bridges Agentheim `ModelRequest`/`ModelResponse` to AICtx `ChatRequest`/`ChatResponse`.

### `models/` — Data models
| File | Role | Disposition |
|------|------|-------------|
| `context_lock.py` | `ContextLock` schema | Preserved — contract artifact |
| `docs_map.py` | `DocsMap` schema | Preserved |
| `inventory.py` | `RepositoryInventory` schema | Preserved |
| `run_report.py` | `RunReport` + metrics | Preserved |

### `oci/` — Remote execution infrastructure
| File | Role | Disposition |
|------|------|-------------|
| `bundle.py` | Snapshot bundling | Preserved; adopted in M8 |
| `cleanup.py` | Remote cleanup | Preserved |
| `config.py` | OCI config models | Preserved |
| `doctor.py` | OCI readiness checks | Preserved; surfaced via `agentheim ctx oci doctor` and `agentheim doctor` in M8 |
| `object_storage.py` | OCI Object Storage | Preserved |
| `remote_job.py` | Remote job submission | Preserved |
| `runtime.py` | Remote runtime wrapper | Preserved |
| `snapshot.py` | Snapshot creation | Preserved |
| `worker.py` | Worker entry point | Preserved |

### `public_docs/` — Public-doc impact mapping
- **M1:** Preserved.
- **M2+:** Wrapped by `ContextOps.public_docs_impact()`.
- **M5:** Unified with Agentheim docs-maintenance workflow.

### `scan/` — Repository scanning
| File | Role | Disposition |
|------|------|-------------|
| `classify.py` | File classification | Preserved |
| `ignore.py` | Gitignore / pathspec handling | Preserved |
| `scanner.py` | Main scanner entry | Preserved; wrapped by `ContextOps.scan()` |
| `secrets.py` | Secret detection | Preserved; composed with `PrivacyEnforcer` |

### `verify/` — Lockfile verification
- **M1:** Preserved.
- **M2+:** Wrapped by `ContextOps.verify()`.

### `tests/` — AICtx test suite
- **M1:** Preserved in vendor directory.
- **M3:** Agentheim integration tests live in `tests/` (e.g., `test_context_ops_impl.py`). Vendor unit tests remain in `agentheim/vendor/aictx/tests/`.

---

## Hard Boundaries

1. `core/` must **never** import from `agentheim.vendor.aictx` directly.
2. All AICtx access from Agentheim code must go through `ContextOps` (or its public façade).
3. AICtx provider internals (`llm/`) can be bridged via `AgentheimToAictxAdapter` when Agentheim injects a provider, but AICtx default path still uses its own `llm/` stack (M7 partial).
4. AICtx transient artifacts (`.aictx/runs/`) are readable via `LegacyAictxReader`; canonical store is `.ai-team/runs/` but `.aictx/runs/` still actively used (M6 partial).
