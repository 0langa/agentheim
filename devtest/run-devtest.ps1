param(
    [ValidateSet("narrow", "targeted", "broad", "full")]
    [string]$Mode = "targeted",
    [string]$K = ""
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ProjectRoot = Join-Path $RepoRoot "Agent-Team"

if (-not (Test-Path $ProjectRoot)) {
    throw "Agent-Team folder not found at: $ProjectRoot"
}

function Invoke-TestSet {
    param(
        [string]$Label,
        [string[]]$PytestArgs
    )
    Write-Host "==> $Label"
    Write-Host "pytest $($PytestArgs -join ' ')"
    Push-Location $ProjectRoot
    try {
        & pytest @PytestArgs
        if ($LASTEXITCODE -ne 0) {
            throw "pytest failed in '$Label' with exit code $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }
}

$baseArgs = @("-q")
if ($K.Trim()) {
    $baseArgs += @("-k", $K.Trim())
}

switch ($Mode) {
    "narrow" {
        Invoke-TestSet -Label "narrow (critical config/registry/runtime guards)" -PytestArgs ($baseArgs + @(
            "tests/test_config.py",
            "tests/test_model_registry.py",
            "tests/test_run_runtime.py"
        ))
    }
    "targeted" {
        Invoke-TestSet -Label "targeted (core flow + providers + planning path)" -PytestArgs ($baseArgs + @(
            "tests/test_config.py",
            "tests/test_model_registry.py",
            "tests/test_planning_agent.py",
            "tests/test_run_runtime.py",
            "tests/test_providers.py",
            "tests/test_tools.py"
        ))
    }
    "broad" {
        Invoke-TestSet -Label "broad (high-signal full functional set)" -PytestArgs ($baseArgs + @(
            "tests/test_config.py",
            "tests/test_model_registry.py",
            "tests/test_planning_agent.py",
            "tests/test_run_runtime.py",
            "tests/test_fix_loop.py",
            "tests/test_state_machine.py",
            "tests/test_resume_report.py",
            "tests/test_ledger_paths.py",
            "tests/test_patching.py",
            "tests/test_tools.py",
            "tests/test_policies.py",
            "tests/test_providers.py",
            "tests/test_verifier_schema.py",
            "tests/test_schemas.py",
            "tests/test_command_detect.py",
            "tests/test_json_repair.py",
            "tests/test_redaction.py"
        ))
    }
    "full" {
        Invoke-TestSet -Label "full (entire project test suite)" -PytestArgs $baseArgs
    }
}

Write-Host "Done: mode=$Mode"
Write-Host ""
Write-Host "Quick cleanup actions (optional):"
Write-Host "1) Clear pytest temp artifacts (Windows):"
Write-Host "   Remove-Item -LiteralPath `"$env:TEMP\\pytest-of-$env:USERNAME`" -Recurse -Force -ErrorAction SilentlyContinue"
Write-Host "2) If cleanup denied, close tools locking temp files, then rerun command above."
Write-Host "3) Re-run same suite:"
Write-Host "   powershell -ExecutionPolicy Bypass -File .\\devtest\\run-devtest.ps1 -Mode $Mode"
