import pytest

from ai_team.schemas import ImplementationPlan


def test_implementation_plan_requires_task_graph() -> None:
    with pytest.raises(Exception):
        ImplementationPlan.model_validate({
            "summary": "x",
            "assumptions": [],
            "non_goals": [],
            "detected_repo_type": "python",
            "risks": [],
            "verification_strategy": [],
            "estimated_commands": [],
            "files_likely_to_change": [],
            "stop_conditions": [],
        })