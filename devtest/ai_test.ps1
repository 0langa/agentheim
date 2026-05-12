param(
    [switch]$AllowMismatchPurpose
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot

Push-Location $RepoRoot
try {
    @'
import json
import sys

from config.config import load_team_config
from core.model_registry import build_model_registry
from providers.base import ModelRequest


PURPOSE_BY_ROLE = {
    "planner": "plan bounded work orders",
    "executor": "apply bounded file changes",
    "verifier": "verify diffs and command evidence",
}


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def main() -> int:
    allow_mismatch = "--allow-mismatch-purpose" in sys.argv

    config = load_team_config()
    registry = build_model_registry(config)
    by_role = config.by_role()

    checks = [
        ("planner", "plan"),
        ("executor", "code_edit"),
        ("verifier", "verify"),
    ]

    failures: list[str] = []

    print("AI connectivity test started")
    for role, capability in checks:
        model = registry.resolve_model(role, capability)
        provider = registry.create_provider(model.config)
        expected_purpose = PURPOSE_BY_ROLE[role]
        prompt = (
            "Return one line exactly in this format:\n"
            "model=<model-name>;purpose=<short-purpose>\n"
            f"Use your real model name. Purpose must be: {expected_purpose}"
        )
        response = provider.invoke(
            ModelRequest(
                role=model.config.role,
                system_prompt="You are in connectivity self-test. Follow exact output format.",
                user_prompt=prompt,
                temperature=0.0,
                max_output_tokens=120,
            )
        )
        content = (response.content or "").strip().replace("\n", " ")
        print(f"[{role}] configured_model={model.config.model} provider={model.config.provider} provider_type={model.config.provider_type}")
        print(f"[{role}] response={content}")

        if "model=" not in content or "purpose=" not in content:
            failures.append(f"{role}: malformed response")
            continue

        purpose_part = content.split("purpose=", 1)[1].strip()
        if (not allow_mismatch) and normalize(expected_purpose) not in normalize(purpose_part):
            failures.append(f"{role}: purpose mismatch (expected contains '{expected_purpose}')")

    if failures:
        print("AI connectivity test failed:")
        for failure in failures:
            print(f"- {failure}")
        return 2

    print("AI connectivity test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'@ | python - @(
        if ($AllowMismatchPurpose) { "--allow-mismatch-purpose" }
    )

    if ($LASTEXITCODE -ne 0) {
        throw "ai_test failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
