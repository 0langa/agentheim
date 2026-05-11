"""Image processing tool (stubs for future vision model integration)."""

from __future__ import annotations

from typing import Any

from core.tool_protocol import BaseTool, ParamSchema, ReturnSchema, RiskLevel, ToolContext, ToolResult, ToolSchema
from multimodal.protocol import MultimodalProcessor


class StubMultimodalProcessor(MultimodalProcessor):
    """Stub implementation returning placeholder results."""

    def describe_image(self, image_b64: str) -> dict[str, Any]:
        return {"description": "[Vision model not configured]", "confidence": 0.0}

    def extract_text_from_image(self, image_b64: str) -> str:
        return "[OCR not configured]"


class ImageTool(BaseTool):
    """Image analysis tool with stub backend."""

    def __init__(self) -> None:
        schema = ToolSchema(
            description="Analyze images (stub — vision model integration deferred).",
            parameters={
                "operation": ParamSchema(
                    type="string",
                    description="Operation: describe, ocr",
                    enum=["describe", "ocr"],
                    required=True,
                ),
                "image_b64": ParamSchema(type="string", description="Base64-encoded image", required=True),
            },
            returns=ReturnSchema(type="object", description="Analysis result"),
        )
        super().__init__("multimodal.image", schema, RiskLevel.LOW)
        self._processor: MultimodalProcessor = StubMultimodalProcessor()

    def invoke(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        valid, err = self.validate_params(params)
        if not valid:
            return ToolResult(success=False, error=err)

        operation = params.get("operation")
        image_b64 = params.get("image_b64", "")

        if operation == "describe":
            result = self._processor.describe_image(image_b64)
            return ToolResult(success=True, data=result)
        if operation == "ocr":
            text = self._processor.extract_text_from_image(image_b64)
            return ToolResult(success=True, data={"text": text})

        return ToolResult(success=False, error=f"Unknown operation: {operation}")
