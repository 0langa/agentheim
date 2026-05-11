"""OpenAI vision processor (GPT-4o, GPT-4V)."""

from __future__ import annotations

import os
from typing import Any

from multimodal.protocol import MultimodalProcessor


class OpenAIVisionProcessor(MultimodalProcessor):
    """Vision processor using OpenAI's GPT-4o / GPT-4V models."""

    def __init__(self, model: str = "gpt-4o", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OpenAI API key not configured. Set OPENAI_API_KEY.")

    def describe_image(self, image_b64: str) -> dict[str, Any]:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                    },
                ],
            }
        ]
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1000,
        )
        description = response.choices[0].message.content or ""
        return {
            "description": description,
            "model": self.model,
            "provider": "openai",
        }

    def extract_text_from_image(self, image_b64: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all text from this image. Return only the text."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                    },
                ],
            }
        ]
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=2000,
        )
        return response.choices[0].message.content or ""
