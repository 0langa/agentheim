from __future__ import annotations

from ai_team.providers.base import ModelProvider, ModelRequest, ModelResponse


class OCIGenAIProvider(ModelProvider):
    def invoke(self, request: ModelRequest) -> ModelResponse:
        raise NotImplementedError("OCI GenAI provider is not implemented yet.")
