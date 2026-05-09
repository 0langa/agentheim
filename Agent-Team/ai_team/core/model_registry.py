from __future__ import annotations

from dataclasses import dataclass

from ai_team.config import AgentModelConfig, TeamConfig
from ai_team.providers.aws_bedrock import AWSBedrockProvider
from ai_team.providers.azure_foundry import AzureFoundryProvider
from ai_team.providers.base import ModelProvider
from ai_team.providers.oci_genai import OCIGenAIProvider
from ai_team.providers.openai_v1 import OpenAIV1Provider


@dataclass(frozen=True)
class ProviderDescriptor:
    id: str
    provider_type: type[ModelProvider]


@dataclass(frozen=True)
class ModelDescriptor:
    id: str
    role: str
    capabilities: frozenset[str]
    config: AgentModelConfig


class ModelRegistry:
    def __init__(self, providers: dict[str, ProviderDescriptor], models: dict[str, ModelDescriptor]) -> None:
        self._providers = providers
        self._models = models

    @classmethod
    def from_team_config(cls, config: TeamConfig) -> "ModelRegistry":
        providers = {
            "openai_compatible": ProviderDescriptor(id="openai_compatible", provider_type=OpenAIV1Provider),
            "openai_v1": ProviderDescriptor(id="openai_v1", provider_type=OpenAIV1Provider),
            "azure_foundry": ProviderDescriptor(id="azure_foundry", provider_type=AzureFoundryProvider),
            "oci_genai": ProviderDescriptor(id="oci_genai", provider_type=OCIGenAIProvider),
            "aws_bedrock": ProviderDescriptor(id="aws_bedrock", provider_type=AWSBedrockProvider),
        }
        model_cfgs = config.by_role()
        model_defs = {m.id: m for m in config.models.values()}
        models = {
            "planner": ModelDescriptor(
                id="planner",
                role="planner",
                capabilities=frozenset(model_defs["planner"].capabilities),
                config=model_cfgs[model_defs["planner"].role],
            ),
            "executor": ModelDescriptor(
                id="executor",
                role="executor",
                capabilities=frozenset(model_defs["executor"].capabilities),
                config=model_cfgs[model_defs["executor"].role],
            ),
            "verifier": ModelDescriptor(
                id="verifier",
                role="verifier",
                capabilities=frozenset(model_defs["verifier"].capabilities),
                config=model_cfgs[model_defs["verifier"].role],
            ),
        }
        return cls(providers=providers, models=models)

    def resolve_model(self, role: str, required_capability: str) -> ModelDescriptor:
        candidates = [model for model in self._models.values() if model.role == role and required_capability in model.capabilities]
        if not candidates:
            raise ValueError(f"No model for role='{role}' with capability='{required_capability}'.")
        return candidates[0]

    def create_provider(self, config: AgentModelConfig) -> ModelProvider:
        descriptor = self._providers.get(config.provider_type)
        if descriptor is None:
            supported = ", ".join(sorted(self._providers))
            raise ValueError(f"Unsupported provider type '{config.provider_type}'. Supported provider types: {supported}")
        return descriptor.provider_type(config)
