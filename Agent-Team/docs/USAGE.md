# Usage

## Install

```powershell
pip install -e .
```

## Ping models

```powershell
python -m ai_team ping-models
```

## Inspect and plan

```powershell
python -m ai_team inspect --repo <path>
python -m ai_team plan "Add a README section" --repo <path>
```

## Run modes

```powershell
python -m ai_team run "Task text" --repo <path> --mode apply
python -m ai_team run "Task text" --repo <path> --mode auto
python -m ai_team run "Task text" --repo <path> --mode ci
```

## Ledger

Runs are stored under `.ai-team/runs/<run-id>` inside the repo root.

## Resume and reports

```powershell
python -m ai_team list-runs --repo <path>
python -m ai_team report --repo <path> --run-id <id>
python -m ai_team resume --repo <path> --run-id <id>
```