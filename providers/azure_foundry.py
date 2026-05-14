from __future__ import annotations

from providers.openai_v1 import OpenAIV1Provider


def normalize_azure_foundry_endpoint(endpoint: str) -> str:
    normalized = endpoint.strip().rstrip("/")
    if normalized.endswith("/openai/v1"):
        return normalized
    return f"{normalized}/openai/v1"


class AzureFoundryProvider(OpenAIV1Provider):
    def __init__(self, config):
        headers = dict(config.headers)
        if config.auth_mode == "api_key" and config.api_key != "-":
            headers.setdefault("api-key", config.api_key)
        normalized_config = config.model_copy(
            update={
                "endpoint": normalize_azure_foundry_endpoint(config.endpoint),
                "headers": headers,
            }
        )
        super().__init__(normalized_config)
        self.config = normalized_config
