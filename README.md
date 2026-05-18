# Agentheim

[![Architecture](https://img.shields.io/badge/architecture-local_first-blue)](docs/ARCHITECTURE.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-unified-blue)](docs/README.md)

**A local-first, preset-driven AI automation platform.**

Agentheim lets you run multi-agent workflows on your own machine with policy-gated tools, append-only run ledgers, and interchangeable model providers.

## What it does

| Preset | What happens |
|--------|-------------|
| **Coder** | Starts a persistent local coding session for any existing directory, including empty folders |
| **Codebase Assistant** | Inspects, plans, patches, tests, and reports on your code |
| **Research Report** | Gathers sources, summarizes, compares, and writes a report |
| **Local Document Chat** | Indexes your documents and answers questions with citations |
| **File Organizer** | Analyzes, proposes, previews, and applies file organization |
| **Docs Maintainer** | Detects stale documentation and aligns it |
| **GitHub Maintainer** | Summarizes issues and drafts PR descriptions |
| **Command Assistant** | Parses natural language and generates safe shell commands |
| **Context Maintainer** | Scans a repository and runs the context pipeline for generated context artifacts |

## Documentation

| Document | Description |
|----------|-------------|
| [User Guide](docs/USER_GUIDE.md) | Install, configure, run presets, and recipes |
| [CLI Commands](docs/CLI-COMMANDS.md) | Full CLI command reference |
| [Architecture](docs/ARCHITECTURE.md) | System design, modules, and boundaries |
| [API Reference](docs/API_REFERENCE.md) | REST API and streaming routes |
| [V1 Roadmap](docs/ROADMAP.md) | Product roadmap and completion checklist |
| [Safety & Security](docs/SAFETY.md) | Privacy modes, approval gates, and security model |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and recovery steps |
| [Changelog](docs/CHANGELOG.md) | Release history |

## Quick start

### Install

**With pipx (recommended for end users):**

```powershell
pipx install agentheim
```

**With pip (editable for developers):**

```powershell
pip install -e .
```

### Configure

Run the interactive setup wizard. It creates a provider profile, stores your API key securely, and binds the core roles.

```powershell
agentheim setup
```

Or set up non-interactively:

```powershell
agentheim setup --provider openai --template openai_v1 --model gpt-4o-mini --api-key $env:OPENAI_API_KEY
```

### Check system health

```powershell
agentheim status
```

### Run your first task

```powershell
# Start a persistent coding session in the current folder
agentheim coder --workspace .

# Or open the dedicated coder UI
agentheim coder ui --workspace .

# Interactive guided mode — pick a preset
agentheim guided

# Or run a task directly by plain-language goal
agentheim use coder --input repo=. --input task="Build a FastAPI app here"

# Batch codebase workflow
agentheim use code --input repo=. --input task="Review the auth module"

# Or run a preset directly
agentheim start coder --input repo=. --input task="Create a CLI scaffold"
agentheim start codebase-assistant --input repo=. --input task="Review code"
```

### Inspect and recover runs

```powershell
agentheim runs                    # list recent runs
agentheim runs show <run-id>      # view a run
agentheim runs resume <run-id>    # resume a blocked run
```

### Open the web UI

```powershell
agentheim open

# Open the dedicated coder page directly
agentheim coder ui --workspace .
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
