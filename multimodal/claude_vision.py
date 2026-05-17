"""Claude vision processor (Claude 3 Opus/Sonnet/Haiku)."""

from __future__ import annotations

import os
from typing import Any

from multimodal.protocol import MultimodalProcessor


class ClaudeVisionProcessor(MultimodalProcessor):
    """Vision processor using Anthropic's Claude 3 models."""

    def __init__(self, model: str = "claude-3-sonnet-20240229", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise RuntimeError("Anthropic API key not configured. Set ANTHROPIC_API_KEY.")

    def _call(self, image_b64: str, prompt: str, max_tokens: int = 1000) -> str:
        import requests

        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_b64,
                                },
                            },
                        ],
                    }
                ],
            },
            timeout=60,
            allow_redirects=False,
        )
        resp.raise_for_status()
        data = resp.json()
        content_blocks = data.get("content", [])
        texts = [b.get("text", "") for b in content_blocks if b.get("type") == "text"]
        return "\n".join(texts)

    def describe_image(self, image_b64: str) -> dict[str, Any]:
        description = self._call(image_b64, "Describe this image in detail.", max_tokens=1000)
        return {
            "description": description,
            "model": self.model,
            "provider": "anthropic",
        }

    def extract_text_from_image(self, image_b64: str) -> str:
        return self._call(image_b64, "Extract all text from this image. Return only the text.", max_tokens=2000)
