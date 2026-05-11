# Usage

## Install

```powershell
pip install -e .
```

## Ping models

```powershell
agentheim ping-models
```

`ping-models` reads provider/model registry config and tests planner/executor/verifier bindings.

## Inspect and plan

```powershell
agentheim inspect --repo <path>
agentheim plan "Add a README section" --repo <path>
```

## Run modes

```powershell
agentheim run "Task text" --repo <path> --mode apply
agentheim run "Task text" --repo <path> --mode auto
agentheim run "Task text" --repo <path> --mode ci
```

## Ledger

Runs are stored under `.ai-team/runs/<run-id>` inside the repo root.

## Resume and reports

```powershell
agentheim list-runs --repo <path>
agentheim report --repo <path> --run-id <id>
agentheim resume --repo <path> --run-id <id>
```
