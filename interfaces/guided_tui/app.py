from __future__ import annotations

from typing import Any

from rich.console import Console

from presets import PRESET_REGISTRY
from presets.base import Question
from interfaces.guided_tui.picker import pick_preset
from interfaces.guided_tui.questionnaire import run_questionnaire
from interfaces.guided_tui.render import (
    build_summary_table,
    print_error,
    print_header,
    print_info,
    print_success,
)

console = Console()


def _questions_to_dicts(questions: list[Question]) -> list[dict[str, Any]]:
    """Convert Preset Question dataclasses to questionnaire dicts."""
    result: list[dict[str, Any]] = []
    for q in questions:
        qtype = "choice" if q.options else "text"
        if q.type == "confirm":
            qtype = "boolean"
        d: dict[str, Any] = {
            "id": q.key,
            "text": q.text,
            "type": qtype,
            "default": q.default,
            "help": "",
            "required": True,
        }
        if q.options:
            d["choices"] = q.options
        result.append(d)
    return result


def run_guided_tui() -> None:
    print_header(console, "Local Agent Orchestra")
    print_info(console, "Select a preset to get started.")

    presets = PRESET_REGISTRY.list()
    selected = pick_preset(console, presets)
    if selected is None:
        print_info(console, "Goodbye!")
        return

    # selected is a Preset object from PRESET_REGISTRY.list()
    # but pick_preset expects RegistryEntry; we adapt here
    preset = selected

    console.print()
    print_success(console, f"Selected: {preset.name}")
    print_info(console, preset.description)
    console.print()

    inputs: dict[str, Any] = dict(preset.default_config)

    if preset.guided_questions:
        questionnaire = _questions_to_dicts(preset.guided_questions)
        answers = run_questionnaire(console, questionnaire)
        for qid, value in answers.items():
            inputs[qid] = value

        console.print(build_summary_table(answers))

    console.print()
    print_success(console, f"Running {preset.name}...")
    try:
        result = preset.run(inputs)
        console.print()
        print_success(console, "Done.")
        console.print(result)
    except Exception as exc:
        console.print()
        print_error(console, f"Error: {exc}")
        raise
