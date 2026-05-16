# Agentheim

[![Architecture](https://img.shields.io/badge/architecture-local_first-blue)](docs/ARCHITECTURE.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-unified-blue)](docs/README.md)

**A local-first, preset-driven AI automation platform.**

Agentheim lets you run multi-agent workflows on your own machine with policy-gated tools, append-only run ledgers, and interchangeable model providers.

## What it does

| Preset | What happens |
|--------|-------------|
| **Codebase Assistant** | Inspects, plans, patches, tests, and reports on your code |
| **Research Report** | Gathers sources, summarizes, compares, and writes a report |
| **Local Document Chat** | Indexes your documents and answers questions with citations |
| **File Organizer** | Analyzes, proposes, previews, and applies file organization |
| **Docs Maintainer** | Detects stale documentation and aligns it |
| **GitHub Maintainer** | Summarizes issues and drafts PR descriptions |
| **Command Assistant** | Parses natural language and generates safe shell commands |

## Documentation

| Document | Description |
|----------|-------------|
| [User Guide](docs/USER_GUIDE.md) | Install, configure, and run presets |
| [CLI Commands](docs/CLI-COMMANDS.md) | Current CLI command surface derived from code |
| [Architecture](docs/ARCHITECTURE.md) | System design, modules, and boundaries |
| [API Reference](docs/API_REFERENCE.md) | REST API and streaming routes |
| [Safety & Security](docs/SAFETY.md) | Privacy modes, approval gates, and security model |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and recovery steps |
| [Changelog](docs/CHANGELOG.md) | Release history |

## Quick start

### Install

```powershell
pip install -e .
```

### Configure

```powershell
agentheim provider add openai --template openai_v1 --model gpt-4o-mini --role planner
```

### Run a preset

```powershell
agentheim guided
agentheim start codebase-assistant --input repo=./my-project --input task="Review code"
```

### Check system health

```powershell
agentheim doctor
agentheim ping-models
agentheim list-runs --repo .
agentheim resume --repo . --run-id <run-id>
```

## Repository layout

```text
agentheim/
├── core/         # Generic runtime engine
├── providers/    # Lazy-loaded provider adapters
├── workflows/    # Workflow packs
├── tools/        # Mediated tools with policy gating
├── memory/       # Memory subsystem
├── interfaces/   # CLI, API server, Web UI, Desktop UI
├── presets/      # Preset definitions
├── config/       # Configuration schemas and loader
├── agents/       # Runtime self-improving hook subsystem
└── docs/         # Public documentation
```

## License

MIT — see [LICENSE](LICENSE).
