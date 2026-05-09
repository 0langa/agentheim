# Coding AI Scripts

Primary project is [`Agent-Team/`](./Agent-Team): local-first orchestrator/coder/verifier runtime for bounded, auditable coding runs.

## Quick start

```powershell
cd Agent-Team
pip install -e .
python -m ai_team ping-models
python -m ai_team inspect --repo ..
```

## Run artifacts

Ledger artifacts are written under `.ai-team/runs/<run-id>` in target repo.
Artifacts avoid host-specific absolute-path coupling so repository rename/move remains portable.
