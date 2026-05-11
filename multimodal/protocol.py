"""Multimodal processor protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MultimodalProcessor(ABC):
    """Protocol for processing multimodal inputs (image, audio, etc.)."""

    @abstractmethod
    def describe_image(self, image_b64: str) -> dict[str, Any]:
        """Generate a text description of an image."""
        raise NotImplementedError

    @abstractmethod
    def extract_text_from_image(self, image_b64: str) -> str:
        """Extract text from an image using OCR."""
        raise NotImplementedError
