from __future__ import annotations

from enum import StrEnum
import os
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ai_team.errors import ConfigError


class ModelRole(StrEnum):
    ORCHESTRATOR = "orchestrator"
    CODER = "coder"
    VERIFIER = "verifier"


ROLE_ENV_ALIASES: dict[ModelRole, tuple[str, ...]] = {
    ModelRole.ORCHESTRATOR: ("GROK_ORCHESTRATOR", "AZURE_GROK", "GROK_REASONER"),
    ModelRole.CODER: ("GROK_CODER",),
    ModelRole.VERIFIER: ("GROK_VERIFIER", "GROK_VERIFY"),
}


class AgentModelConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    role: ModelRole
    provider: str = Field(min_length=1)
    endpoint: str = Field(min_length=1)
    api_key: str = Field(min_length=1)
    model: str = Field(min_length=1)

    def redacted_dict(self) -> dict[str, Any]:
        return {
            "role": self.role.value,
            "provider": self.provider,
            "endpoint": self.endpoint,
            "api_key": redact_secret(self.api_key),
            "model": self.model,
        }


class TeamConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    orchestrator: AgentModelConfig
    coder: AgentModelConfig
    verifier: AgentModelConfig

    def by_role(self) -> dict[ModelRole, AgentModelConfig]:
        return {
            ModelRole.ORCHESTRATOR: self.orchestrator,
            ModelRole.CODER: self.coder,
            ModelRole.VERIFIER: self.verifier,
        }

    def dump(self, redacted: bool = True) -> dict[str, Any]:
        configs = self.by_role()
        if redacted:
            return {role.value: config.redacted_dict() for role, config in configs.items()}
        return {role.value: config.model_dump() for role, config in configs.items()}


def redact_secret(value: str) -> str:
    if len(value) <= 4:
        return "****"
    return f"{value[:2]}***{value[-2:]}"


def _env_name(role: ModelRole, suffix: str) -> str:
    return f"GROK_{role.value.upper()}_{suffix}"


def _candidate_env_names(role: ModelRole, suffix: str) -> tuple[str, ...]:
    names: list[str] = []
    preferred = _env_name(role, suffix)
    names.append(preferred)
    for prefix in ROLE_ENV_ALIASES[role]:
        candidate = f"{prefix}_{suffix}"
        if candidate not in names:
            names.append(candidate)
    return tuple(names)


def _get_env_value(role: ModelRole, suffix: str, default: str = "") -> str:
    for env_name in _candidate_env_names(role, suffix):
        value = os.getenv(env_name)
        if value is not None and value.strip():
            return value.strip()
    return default.strip()


def _default_model(role: ModelRole) -> str:
    defaults = {
        ModelRole.ORCHESTRATOR: "grok-4-20-reasoning",
        ModelRole.CODER: "grok-4-1-fast-reasoning",
        ModelRole.VERIFIER: "grok-4-20-non-reasoning",
    }
    return defaults[role]


def _load_role_config(role: ModelRole) -> AgentModelConfig:
    provider = _get_env_value(role, "PROVIDER", "azure_foundry")
    endpoint = _get_env_value(role, "ENDPOINT")
    api_key = _get_env_value(role, "KEY")
    model = _get_env_value(role, "MODEL", _default_model(role))

    missing = []
    if not endpoint:
        missing.append(" or ".join(_candidate_env_names(role, "ENDPOINT")))
    if not api_key:
        missing.append(" or ".join(_candidate_env_names(role, "KEY")))
    if not model:
        missing.append(" or ".join(_candidate_env_names(role, "MODEL")))

    if missing:
        joined = ", ".join(missing)
        raise ConfigError(f"Missing required environment variables for role '{role.value}': {joined}")

    return AgentModelConfig(
        role=role,
        provider=provider,
        endpoint=endpoint,
        api_key=api_key,
        model=model,
    )


def load_team_config() -> TeamConfig:
    return TeamConfig(
        orchestrator=_load_role_config(ModelRole.ORCHESTRATOR),
        coder=_load_role_config(ModelRole.CODER),
        verifier=_load_role_config(ModelRole.VERIFIER),
    )
