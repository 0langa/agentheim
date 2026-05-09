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
Write-Host "Optional post-run actions:"
Write-Host "1) Clear pytest temp artifacts"
Write-Host "2) Clear local pytest cache in Agent-Team"
Write-Host "3) Re-run same suite"
Write-Host ""
Write-Host "Prompt format: [Y]es / [N]o / [A]ll"

$runAll = $false

function Ask-YNA {
    param([string]$Question)
    if ($runAll) { return "Y" }
    $reply = Read-Host "$Question [Y/N/A]"
    if (-not $reply) { return "N" }
    $value = $reply.Trim().ToUpperInvariant()
    if ($value -eq "A") {
        $script:runAll = $true
        return "Y"
    }
    if ($value -eq "Y" -or $value -eq "N") { return $value }
    return "N"
}

if ((Ask-YNA "Run action 1 now?") -eq "Y") {
    Remove-Item -LiteralPath "$env:TEMP\pytest-of-$env:USERNAME" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Action 1 done."
}

if ((Ask-YNA "Run action 2 now?") -eq "Y") {
    Remove-Item -LiteralPath (Join-Path $ProjectRoot ".pytest_cache") -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Action 2 done."
}

if ((Ask-YNA "Run action 3 now?") -eq "Y") {
    Write-Host "Re-running mode=$Mode"
    & powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "run-devtest.ps1") -Mode $Mode -K $K
}
