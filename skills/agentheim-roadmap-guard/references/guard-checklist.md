# Guard Checklist

Run this checklist before finalizing substantial changes.

## 1) Static Boundary Audit

- no provider imports introduced into `core/`
- no preset/workflow identifiers hardcoded into generic runtime paths
- no policy bypass shortcuts in tool execution paths

## 2) Roadmap Compliance

- run `python scripts/roadmap-check.py --phase 7 --ci`
- reconcile all reported phase/boundary violations

## 3) Runtime Risk Audit

- verify retry limits and error classification are still coherent
- verify ledger/events remain durable and queryable
- verify approval workflow still gates risky operations

## 4) Validation

- run `devtest/run-devtest.ps1 -Mode targeted` minimum
- escalate to `broad` for cross-subsystem edits

## 5) Documentation Sync

- update any stale architecture or operator docs in same patch
