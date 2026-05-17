from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from presets.base import PRESET_REGISTRY, Preset, Question


class QuestionSchema(BaseModel):
    key: str
    type: str
    text: str
    options: list[str] = Field(default_factory=list)
    default: Any = None

    @classmethod
    def from_question(cls, question: Question) -> "QuestionSchema":
        return cls(
            key=question.key,
            type=question.type,
            text=question.text,
            options=question.options,
            default=question.default,
        )


class PresetCatalogItem(BaseModel):
    preset_id: str
    workflow_id: str
    name: str
    description: str
    support_state: str = "experimental"
    product_tier: str = "advanced"
    recommended_for: list[str] = Field(default_factory=list)
    requires_integrations: list[str] = Field(default_factory=list)
    estimated_time: str = ""
    output_kind: str = ""
    example_inputs: dict[str, Any] = Field(default_factory=dict)
    required_capabilities: list[str] = Field(default_factory=list)
    questions: list[QuestionSchema] = Field(default_factory=list)
    default_config: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_preset(cls, preset: Preset) -> "PresetCatalogItem":
        return cls(
            preset_id=preset.preset_id,
            workflow_id=preset.workflow_id,
            name=preset.name,
            description=preset.description,
            support_state=preset.support_state,
            product_tier=preset.product_tier,
            recommended_for=preset.recommended_for,
            requires_integrations=preset.requires_integrations,
            estimated_time=preset.estimated_time,
            output_kind=preset.output_kind,
            example_inputs=preset.example_inputs,
            required_capabilities=preset.required_capabilities,
            questions=[QuestionSchema.from_question(q) for q in preset.guided_questions],
            default_config=preset.default_config,
        )


class PresetCatalog:
    def __init__(self) -> None:
        self._registry = PRESET_REGISTRY

    def list(self) -> list[PresetCatalogItem]:
        """Return all presets as catalog items, ordered recommended first."""
        items = [PresetCatalogItem.from_preset(p) for p in self._registry.list()]
        tier_order = {"recommended": 0, "advanced": 1, "hidden": 2}
        items.sort(key=lambda item: (tier_order.get(item.product_tier, 99), item.name))
        return items

    def get(self, preset_id: str) -> PresetCatalogItem:
        preset = self._registry.get(preset_id)
        return PresetCatalogItem.from_preset(preset)

    def list_by_tier(self, tier: str) -> list[PresetCatalogItem]:
        return [item for item in self.list() if item.product_tier == tier]

    def recommended(self) -> list[PresetCatalogItem]:
        return self.list_by_tier("recommended")

    def advanced(self) -> list[PresetCatalogItem]:
        return self.list_by_tier("advanced")

    def ids(self) -> list[str]:
        return self._registry.ids()


CATALOG = PresetCatalog()
