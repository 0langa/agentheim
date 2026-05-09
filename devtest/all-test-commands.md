cd Agent-Team
pytest -q
pytest -q tests/test_config.py tests/test_model_registry.py tests/test_run_runtime.py
pytest -q tests/test_config.py tests/test_model_registry.py tests/test_planning_agent.py tests/test_run_runtime.py tests/test_providers.py tests/test_tools.py
pytest -q tests/test_config.py tests/test_model_registry.py tests/test_planning_agent.py tests/test_run_runtime.py tests/test_fix_loop.py tests/test_state_machine.py tests/test_resume_report.py tests/test_ledger_paths.py tests/test_patching.py tests/test_tools.py tests/test_policies.py tests/test_providers.py tests/test_verifier_schema.py tests/test_schemas.py tests/test_command_detect.py tests/test_json_repair.py tests/test_redaction.py
powershell -ExecutionPolicy Bypass -File ..\devtest\run-devtest.ps1 -Mode narrow
powershell -ExecutionPolicy Bypass -File ..\devtest\run-devtest.ps1 -Mode targeted
powershell -ExecutionPolicy Bypass -File ..\devtest\run-devtest.ps1 -Mode broad
powershell -ExecutionPolicy Bypass -File ..\devtest\run-devtest.ps1 -Mode full
powershell -ExecutionPolicy Bypass -File ..\devtest\run-devtest.ps1 -Mode targeted -K registry
powershell -ExecutionPolicy Bypass -File ..\devtest\run-devtest.ps1 -Mode full -K "not slow"
