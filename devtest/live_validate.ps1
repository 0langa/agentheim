param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ScriptPath = Join-Path $RepoRoot "scripts\live_validate.py"

Push-Location $RepoRoot
try {
    & python $ScriptPath @Args
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
