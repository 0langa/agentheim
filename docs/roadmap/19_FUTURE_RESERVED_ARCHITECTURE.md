# 19 — FUTURE RESERVED ARCHITECTURE
## Post-Roadmap Integrations, Research, and Deferred Systems

**Status:** POST-PHASE-6 — Items here are NOT unlocked for implementation until Phase 7 (Production Hardening) is complete.
**Enforcement:** Implementing these before Phase 7 completion is an ARCHITECTURAL BREACH (Level 3).
**Last Updated:** 2026-05-10

---

## 1. What Moved to Phase 6 or Phase 7

The following items were formerly in this document as "reserved" but have since been implemented:

| Formerly Reserved | Now In | Status |
|-------------------|--------|--------|
| MCP Integration | Phase 6 ✅ | `tools/mcp/` — persistent pool, stdio transport |
| Browser Tool | Phase 6 ✅ | `tools/browser/` — session reuse, async variant |
| Local DB Tool | Phase 6 ✅ | `tools/local_db/` — SQLite operations |
| Web UI | Phase 6 ✅ | `interfaces/web_ui/` — execution, streaming, dashboard |
| Desktop UI | Phase 6 ✅ | `interfaces/desktop_ui/` — scaffold |
| API Server | Phase 6 ✅ | `interfaces/api_server/` — OpenAPI, metrics, auth |
| Distributed Workers | Phase 6 ✅ | `workflows/distributed/` — HTTP transport |
| Plugin Marketplace | Phase 6 ✅ | `marketplace/` — sandbox, signatures |
| Monitoring | Phase 6 ✅ | `monitoring/` — MetricsCollector, Prometheus |
| Self-Improving Agents | Phase 6 ✅ | `agents/self_improving/` — feedback loop, strategies |
| Cross-Modal Capabilities | Phase 6 ✅ | `multimodal/` — GPT-4o, Claude vision |
| Federated Agent Networks | Phase 6 ✅ | `federation/` — HTTP transport, peer discovery |
| Guided TUI | Phase 5 ✅ | `interfaces/guided_tui/` — rich preset picker |

The following items were formerly "reserved" but are now recognized as **missing foundational subsystems** and have been moved to **Phase 7 (Production Hardening)**:

| Formerly Reserved / Missing | Now In | Gap |
|-----------------------------|--------|-----|
| Event-sourced ledger (hash chain, replay) | Phase 7 🔒 | No SHA-256, no replay, no resume |
| Core runtime files | Phase 7 🔒 | `workflow_runner.py`, `retry_engine.py`, etc. missing |
| Public API facade | Phase 7 🔒 | No `core/public_api.py` |
| Approval workflow | Phase 7 🔒 | No human-in-the-loop for MEDIUM/HIGH |
| Provider lazy loading | Phase 7 🔒 | Eager imports in `providers/__init__.py` |
| Parallel execution | Phase 7 🔒 | `Workflow.run()` is sequential |
| Privacy enforcer | Phase 7 🔒 | No `PrivacyMode` enum |

---

## 2. Remaining Future Integrations (Phase 8+)

These are genuinely new capabilities beyond the original roadmap scope.

### 2.1 IDE Extensions
- VS Code extension for inline agent assistance
- JetBrains plugin for context-aware suggestions
- Neovim Lua plugin for terminal-centric workflows
- **Unlock:** Phase 7 complete

### 2.2 CI/CD Integration
- GitHub Actions marketplace action
- GitLab CI template
- Azure DevOps pipeline task
- Trigger Agentheim runs from PR events, issue labels, or scheduled jobs
- **Unlock:** Phase 7 complete

### 2.3 AICtx Context Intelligence Layer
- Project scanning and context compilation outsourced to AICtx
- Integration contract: LLM-readable output + machine-readable JSON manifests
- **Unlock:** Both projects stable + integration contract reviewed

---

## 3. Research Frontiers (No Phase Assigned)

These are exploratory areas without committed implementation timelines.

### 3.1 Formal Verification
- Mathematical proof of correctness for critical outputs
- SMT solver integration for constraint checking
- Property-based testing for agent behavior
- **Status:** Research only. No committed phase.

### 3.2 Advanced Kernel Monitoring
- eBPF-based syscall interception (Linux)
- ETW-based event tracing (Windows)
- Real-time policy violation detection at kernel level
- **Status:** Deferred indefinitely. Requires security review and platform-specific expertise.

---

## 4. Modification Rules

- Future architecture may be refined for clarity
- Future architecture may not be implemented before Phase 7 unlock
- Modifications require Architecture Lead approval

---

*End of 19_FUTURE_RESERVED_ARCHITECTURE.md*
