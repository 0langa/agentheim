import pytest

from ai_team.errors import ExecutionError
from ai_team.state_machine import RuntimeState, RuntimeStateMachine


def test_state_machine_happy_path() -> None:
    machine = RuntimeStateMachine()
    machine.transition(RuntimeState.LOAD_CONFIG)
    machine.transition(RuntimeState.PREPARE_WORKSPACE)
    machine.transition(RuntimeState.SCAN_REPOSITORY)
    machine.transition(RuntimeState.BUILD_CONTEXT_PACK)
    machine.transition(RuntimeState.PLAN)
    machine.transition(RuntimeState.EXECUTE_TASK)
    machine.transition(RuntimeState.BASIC_VERIFY)
    machine.transition(RuntimeState.VERIFY_TASK)
    machine.transition(RuntimeState.FINAL_VERIFY)
    machine.transition(RuntimeState.FINAL_REPORT)
    machine.transition(RuntimeState.RESUME_AVAILABLE)
    machine.transition(RuntimeState.DONE)
    assert machine.current == RuntimeState.DONE


def test_state_machine_rejects_invalid_transition() -> None:
    machine = RuntimeStateMachine()
    with pytest.raises(ExecutionError):
        machine.transition(RuntimeState.PLAN)