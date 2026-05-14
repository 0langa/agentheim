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
