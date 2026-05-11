# Release Checklist

## Mandatory

- devtest docs/scripts reflect current preferred test paths
- changelog entry appended (no rewrite)
- relevant tests executed and reported

## Connectivity Rule

- `devtest/ai_test.ps1` max two back-to-back attempts for one validation effort
- 120s hard timeout per attempt
- on second failure, stop and report

## Suggested Final Smoke

```powershell
pytest -q tests/smoke/test_cli.py tests/smoke/test_presets.py
agentheim --help
agentheim doctor
```

## Handoff Fields

- Summary of code/docs touched
- Validation commands run and outcomes
- Known residual risks or follow-ups
