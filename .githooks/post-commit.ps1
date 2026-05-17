$ErrorActionPreference = 'Stop'

try {
    $repoRoot = git rev-parse --show-toplevel
    if (-not $repoRoot) {
        exit 0
    }
    Set-Location $repoRoot.Trim()
    python scripts/refresh_kimi_memory.py *> $null
}
catch {
    Write-Warning "[agentheim] failed to refresh .kimi/memory.jsonl after commit"
}

exit 0
