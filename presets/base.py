from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.capability_registry import register_preset


@dataclass
class Question:
    key: str
    type: str
    text: str
    options: list[str] = field(default_factory=list)
    default: Any = None


class PresetInputError(ValueError):
    """Raised when preset inputs are incomplete or invalid."""

    def __init__(self, preset_id: str, missing_inputs: list[str]) -> None:
        self.preset_id = preset_id
        self.missing_inputs = missing_inputs
        missing = ", ".join(missing_inputs)
        super().__init__(f"Missing required input(s) for preset '{preset_id}': {missing}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": "missing_required_inputs",
            "message": str(self),
            "preset_id": self.preset_id,
            "missing_inputs": self.missing_inputs,
        }


@dataclass
class Preset:
    preset_id: str
    workflow_id: str
    name: str
    description: str
    guided_questions: list[Question] = field(default_factory=list)
    default_config: dict[str, Any] = field(default_factory=dict)
    support_state: str = "experimental"
    required_capabilities: list[str] = field(default_factory=list)

    def validate_inputs(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        """Merge defaults and validate required guided inputs."""
        validated: dict[str, Any] = dict(self.default_config)
        validated.update(inputs or {})

        missing: list[str] = []
        for question in self.guided_questions:
            value = validated.get(question.key)
            if value in (None, ""):
                if question.default is None:
                    missing.append(question.key)
                else:
                    validated[question.key] = question.default

        if missing:
            raise PresetInputError(self.preset_id, missing)
        return validated

    def run(self, inputs: dict[str, Any]) -> Any:
        raise NotImplementedError


class PresetRegistry:
    def __init__(self) -> None:
        self._presets: dict[str, Preset] = {}

    def register(self, preset: Preset) -> None:
        if preset.preset_id in self._presets:
            raise ValueError(f"Preset '{preset.preset_id}' already registered")
        self._presets[preset.preset_id] = preset
        register_preset(
            preset.preset_id,
            lambda inputs: preset.run(inputs),
            metadata={
                "workflow_id": preset.workflow_id,
                "name": preset.name,
                "description": preset.description,
                "support_state": preset.support_state,
                "required_capabilities": preset.required_capabilities,
            },
        )

    def list(self) -> list[Preset]:
        return list(self._presets.values())

    def get(self, preset_id: str) -> Preset:
        if preset_id not in self._presets:
            raise KeyError(f"Preset '{preset_id}' not found")
        return self._presets[preset_id]

    def ids(self) -> list[str]:
        return list(self._presets.keys())


PRESET_REGISTRY = PresetRegistry()
