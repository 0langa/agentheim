# Release Checklist

## Mandatory

- devtest docs/scripts reflect current preferred test paths
- `docs/CHANGELOG.md` entry appended, not rewritten
- relevant tests or directive checks executed and reported
- `AGENTS.md` and `.github/instructions/*.md` remain aligned when governance changes

## Directive Checks

Run after docs, instruction, agent, GitHub template, skill, or validation-command changes:

```powershell
python scripts/check-agent-instructions.py
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode directive -NoPrompt
```

## Connectivity Rule

- `devtest/ai_test.ps1` max two back-to-back attempts for one validation effort
- 120s hard timeout per attempt
- on second failure, stop and report

## Suggested Final Smoke

```powershell
python -m interfaces.cli.cli --help
python -m interfaces.cli.cli doctor --skip-connectivity
pytest -q tests/smoke/test_cli.py tests/smoke/test_presets.py
```

## Handoff Fields

- Summary of code/docs touched
- Validation commands run and outcomes
- Known residual risks or follow-ups

