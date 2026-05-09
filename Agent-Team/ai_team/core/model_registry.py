from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module

from ai_team.config import AgentModelConfig, TeamConfig
from ai_team.providers.base import ModelProvider


@dataclass(frozen=True)
class ProviderDescriptor:
    id: str
    import_path: str


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
            "openai_compatible": ProviderDescriptor(id="openai_compatible", import_path="ai_team.providers.openai_v1:OpenAIV1Provider"),
            "openai_v1": ProviderDescriptor(id="openai_v1", import_path="ai_team.providers.openai_v1:OpenAIV1Provider"),
            "azure_foundry": ProviderDescriptor(id="azure_foundry", import_path="ai_team.providers.azure_foundry:AzureFoundryProvider"),
            "oci_genai": ProviderDescriptor(id="oci_genai", import_path="ai_team.providers.oci_genai:OCIGenAIProvider"),
            "aws_bedrock": ProviderDescriptor(id="aws_bedrock", import_path="ai_team.providers.aws_bedrock:AWSBedrockProvider"),
        }
        models = {}
        for model in config.models.values():
            models[model.id] = ModelDescriptor(
                id=model.id,
                role=model.role.value,
                capabilities=frozenset(model.capabilities),
                config=config.resolve_role(model.role),
            )
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
        module_name, class_name = descriptor.import_path.split(":", 1)
        module = import_module(module_name)
        provider_type = getattr(module, class_name)
        return provider_type(config)
