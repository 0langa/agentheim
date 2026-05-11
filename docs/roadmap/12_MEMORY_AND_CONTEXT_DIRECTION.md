# 12 — MEMORY AND CONTEXT DIRECTION
## Memory Hierarchy, Context Packing, and Resume Capabilities

**Status:** DERIVED FROM 07_SUBSYSTEM_DEFINITIONS
**Enforcement:** All memory implementations must conform.
**Violation Classification:** BOUNDARY CONCERN (Level 2)

---

## 1. Memory Hierarchy

The system implements a three-tier memory model:

```
Tier 1: Working Memory (Ephemeral)
    └── Single run duration
    └── Active context pack, current plan, intermediate results
    └── Stored in ledger for reconstruction

Tier 2: Run Memory (Repository-Scoped)
    └── Cross-run for a specific repository
    └── Previous plans, patterns, frequently modified files
    └── Stored in `<repo-root>/.ai-team/memory/` within repo

Tier 3: Global Memory (Cross-Repository)
    └── Cross-project persistence
    └── User preferences, coding style, model profiles
    └── Stored in platform-appropriate user data dir via `platformdirs`
    └── Default: `~/.local/share/agent-arena/` (Linux), `~/Library/Application Support/agent-arena/` (macOS), `%LOCALAPPDATA%\agent-arena\` (Windows)
```

---

## 2. Tier 1: Working Memory

### 2.1 Scope
- Lives for the duration of a single run
- Analogous to human short-term memory

### 2.2 Contents
| Content | Description | Persistence |
|---------|-------------|-------------|
| Active context pack | Current repository snapshot | Ledger |
| Current plan | Generated execution plan | Ledger |
| Pending tasks | Steps yet to execute | Ledger |
| Intermediate results | Step outputs | Ledger |
| Agent messages | Recent conversation history | In-memory |
| Tool call queue | Pending tool invocations | In-memory |
| Policy decisions | Recent approval/denial decisions | Ledger |

### 2.3 Implementation
- **Module:** `memory/tiers/working.py`
- **Class:** `WorkingMemory`
- **API:** `set(key, value)`, `get(key, default)`, `append(key, item)`, `get_list(key)`, `snapshot()`, `flush()`, `clear()`
- **Persistence:** In-memory dict + optional `RunLedger` flush to `working_memory.json`
- **Integration:** `Workflow.run()` instantiates `WorkingMemory` and passes it via `StepContext.working_memory`

### 2.4 Working Memory Lifecycle
```
Run Start → Allocate working memory
    |
    v
Context pack built → Stored in working memory
    |
    v
Plan generated → Stored in working memory
    |
    v
Step execution → Results stored in working memory
    |
    v
Run End → Working memory flushed to ledger
    |
    v
Working memory deallocated
```

---

## 3. Tier 2: Run Memory

### 3.1 Scope
- Persists across runs for a specific repository
- Enables learning from previous runs

### 3.2 Contents
| Content | Description | Use Case |
|---------|-------------|----------|
| Previous plans | Plans from past runs | Reference for similar tasks |
| Common patterns | Frequently used patterns | Suggest proven approaches |
| Frequently modified files | Files changed often | Prioritize in context pack |
| Test outcomes | Test results from past runs | Predict test behavior |
| Lessons learned | Notes from failed attempts | Avoid repeated mistakes |
| Agent performance | Model performance per task | Improve model selection |

### 3.3 Storage Location
```
<repo-root>/.ai-team/memory/
    episodes/                 # EpisodicMemory JSONL files (monthly shards)
    semantic/                 # SemanticMemory JSONL files
    .project_scope            # Fingerprint file for project scoping validation
```

### 3.4 Implementation
- **EpisodicMemory:** `memory/episodic.py` — timeline of `Episode` records with importance scoring and LRU eviction (default `max_episodes=1000`)
- **SemanticMemory:** `memory/semantic.py` — concept graph of `Concept` records with bidirectional relations and vector similarity query
- **Brain:** `memory/brain.py` — unified orchestrator; `perceive()` records episodes + auto-extracts concepts; `remember()` fuses episodic recall + semantic query
- **MemoryBus:** `memory/bus.py` — cross-process safe locking via `filelock.FileLock` + `threading.RLock`; singleton per `repo_root`
- **EmbeddingEngine:** `memory/embeddings.py` — hash-based random projections for lightweight vector encoding

### 3.4 Run Memory Example
The Orchestrator can query: "Last time we modified the auth module, we broke 3 tests. Let's be careful this time."

### 3.5 Privacy
- Run memory is scoped to the repository
- Never sent to remote providers in strict-private mode
- Contains no sensitive data (redacted before storage)

---

## 4. Tier 3: Global Memory

### 4.1 Scope
- Persists across all projects
- User-level preferences and learned behavior

### 4.2 Contents
| Content | Description | Use Case |
|---------|-------------|----------|
| User preferences | Preferred models, settings | Default configuration |
| Coding style | Indentation, naming, patterns | Consistent code generation |
| Common decisions | Frequently approved/denied actions | Streamline approvals |
| Model performance profiles | Performance per model per task | Better model routing |
| Provider preferences | Preferred providers | Default provider selection |
| Privacy preferences | Default privacy mode | Consistent privacy behavior |

### 4.3 Storage Location
```
<platform-user-data>/agent-arena/
    global_memory.db          # SQLite database (WAL mode)
        preferences           # key-value JSON store
        approval_history      # approval decision log
        model_profiles        # per-model performance stats
```

### 4.4 Implementation
- **Module:** `memory/tiers/global_.py`
- **Class:** `GlobalMemory`
- **API:** `get_preference(key, default)`, `set_preference(key, value)`, `record_approval(decision, tool_name, context)`, `get_approval_history(limit)`, `record_model_result(model_id, task_type, success, latency_ms)`, `get_model_profile(model_id)`
- **Privacy:** Values redacted via `core.redaction.redact_dict()` before JSON serialization; never stores repo-specific data
- **CLI:** `python -m core memory get --key <key>`, `python -m core memory set --key <key> --value <json>`

### 4.4 Global Memory Privacy
- Global memory is stored locally
- Never sent to remote providers
- Contains no repository-specific information
- User controls what is stored

---

## 5. Memory Types

### 5.1 Structured Memory (Key-Value)
- Simple key-value storage for project facts
- JSON/JSONL format via `JsonlBackend` (`memory/backends/jsonl.py`)
- SQLite format via `SqliteBackend` (`memory/backends/sqlite.py`)
- Synchronous read/write
- Used for: project configuration, known issues, dependencies

### 5.2 Episodic Memory (What Happened)
- Vector-backed timeline of run episodes
- Retrieved via semantic similarity over embeddings
- Used for: "Has this agent ever dealt with a CORS issue before?"
- **Implemented:** `memory/episodic.py` — `EpisodicMemory` class

### 5.3 Semantic Memory (What Is True)
- Structured knowledge graph of domain concepts
- Updated by the Orchestrator via `Brain._extract_concepts()`
- Used for: "This is how authentication works in this codebase"
- **Implemented:** `memory/semantic.py` — `SemanticMemory` class
- Deduplication: similarity > 0.85 merges, > 0.60 relates, below creates new

### 5.4 Procedural Memory (How To Do Things)
- Learned workflows and patterns
- Derived from successful run histories
- Used for: "For this codebase, write tests first, then implementation"
- **Status:** Partial — deduplicated concepts in SemanticMemory capture patterns; full procedural extraction deferred

---

## 6. Context Packing

### 6.1 Purpose
The context pack is the snapshot of repository state fed to agents. It is a critical bottleneck — irrelevant context degrades agent performance significantly.

### 6.2 Context Packing Process

```
1. Repository Scan
   └── Identify all relevant files
   └── Build dependency graph
   └── Rank files by relevance to task

2. File Summarization
   └── Large code files: AST-based summarization
   └── Markdown files: Heading extraction
   └── Config files: Key-value extraction
   └── Binary files: Skip with note

3. Token Budget Enforcement
   └── Allocate token budget per model capability
   └── Summarize when budget exceeded
   └── Prioritize most relevant files

4. Secret Redaction
   └── Detect secrets via patterns
   └── Redact before packing
   └── Replace with [REDACTED-<hash>]

5. Context Bundle Generation
   └── Human-readable: context_bundle.md
   └── Machine-readable: context_manifest.json
```

### 6.3 Context Pack Contents

```
context_bundle.md:
    # Project Context
    ## Overview
    - Project name, language, framework
    - Directory structure (summary)

    ## Task Description
    - Current task and constraints

    ## Relevant Files
    - File path + summary + key definitions

    ## Dependencies
    - External dependencies
    - Internal module dependencies

    ## Recent Changes
    - Recent git commits (if applicable)

    ## Known Issues
    - Known bugs, TODOs, FIXMEs

context_manifest.json:
    {
        "files": [
            {
                "path": "src/auth.py",
                "relevance_score": 0.95,
                "token_count": 500,
                "summary": "Authentication module with login/logout",
                "definitions": ["AuthManager", "login", "logout"]
            }
        ],
        "total_tokens": 15000,
        "budget_used": 0.75
    }
```

### 6.4 Context Pack Requirements
- Must be human-readable (context_bundle.md)
- Must be machine-readable (context_manifest.json)
- Must fit within model's context window
- Must have secrets redacted
- Must be reproducible (same scan → same pack)
- Must be logged in ledger

---

## 7. Resume and Continuation

### 7.1 Resume Capabilities
Any interrupted run can be resumed from its exact state:
- Event-sourced ledger captures all state transitions
- Idempotent operations where possible
- Explicit checkpointing at phase boundaries
- The `RESUME_AVAILABLE` state enables resumption

### 7.2 Resume Triggers
- System crash
- API rate limit exceeded
- User interruption (Ctrl+C)
- Budget exhaustion (with remaining budget on resume)
- Network outage

### 7.3 Resume Process
```
1. Load ledger for interrupted run
2. Find last checkpoint or reconstruct from start
3. Replay events to reconstruct state
4. Validate workspace matches expected state
5. Check remaining budget
6. Continue execution from current phase
```

### 7.4 Resume Requirements
- Resume must not re-execute completed steps
- Resume must validate workspace state
- Resume must re-check budgets (with remaining allocation)
- Resume must handle changed external state (new files, git changes)
- Resume must be logged as `run.resumed` event

---

*End of 12_MEMORY_AND_CONTEXT_DIRECTION.md*
