from __future__ import annotations

from typing import Any

from agentheim.vendor.aictx.llm.base import ChatRequest, ChatResponse, ModelProvider as AictxModelProvider
from providers.base import ModelProvider as AgentheimModelProvider, ModelRequest, ModelResponse


class AgentheimToAictxAdapter(AictxModelProvider):
    """Wrap an Agentheim ModelProvider so it satisfies AICtx's interface."""

    def __init__(self, provider: AgentheimModelProvider) -> None:
        self._provider = provider

    def chat(self, request: ChatRequest) -> ChatResponse:
        """Convert ChatRequest → ModelRequest, invoke, convert response back."""
        system_prompt = request.system_prompt or None
        user_prompt = ""
        if request.messages:
            for msg in reversed(request.messages):
                if msg.get("role") == "user":
                    user_prompt = msg.get("content", "")
                    break
            if not user_prompt:
                user_prompt = request.messages[-1].get("content", "")

        model_request = ModelRequest(
            role=self._provider.config.role,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=request.temperature,
            max_output_tokens=request.max_output_tokens,
        )
        model_response: ModelResponse = self._provider.invoke(model_request)
        raw = model_response.raw or {}
        return ChatResponse(
            content=model_response.content,
            finish_reason="stop",
            input_tokens=raw.get("input_tokens", 0),
            output_tokens=raw.get("output_tokens", 0),
        )

    def count_tokens(self, text: str) -> int:
        """Best-effort token count. Fallback to len(text)//4."""
        if hasattr(self._provider, "count_tokens"):
            result = self._provider.count_tokens(text)
            if result is not None:
                return result
        return len(text) // 4

    def metadata(self) -> dict[str, Any]:
        """Delegate to wrapped provider if possible."""
        if hasattr(self._provider, "metadata"):
            return self._provider.metadata()
        return {"provider": "agentheim_adapter"}
