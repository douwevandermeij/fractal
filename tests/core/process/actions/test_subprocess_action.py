"""Tests for SubProcessAction."""

import pytest

from fractal.core.process.actions import (
    CreateSpecificationAction,
    SetContextVariableAction,
)
from fractal.core.process.actions.control_flow import IfElseAction, SubProcessAction
from fractal.core.process.process import Process
from fractal.core.process.process_context import ProcessContext
from fractal.core.process.specifications import field_equals


def test_subprocess_executes_process():
    """Test SubProcessAction executes a sub-process."""
    sub_process = Process([SetContextVariableAction(sub_result="from_subprocess")])

    action = SubProcessAction(sub_process)
    ctx = ProcessContext({"initial": "data"})
    result = action.execute(ctx)

    assert result["initial"] == "data"
    assert result["sub_result"] == "from_subprocess"


def test_subprocess_shares_context():
    """Test sub-process shares context with parent."""
    sub_process = Process(
        [
            SetContextVariableAction(modified=True),
        ]
    )

    action = SubProcessAction(sub_process)
    ctx = ProcessContext({"shared": "value"})
    result = action.execute(ctx)

    # Sub-process should see and modify shared context
    assert result["shared"] == "value"
    assert result["modified"] is True


def test_subprocess_composition():
    """Test composing multiple sub-processes."""
    validate_user = Process([SetContextVariableAction(user_validated=True)])

    fetch_permissions = Process(
        [SetContextVariableAction(permissions=["read", "write"])]
    )

    main_process = Process(
        [
            SetContextVariableAction(user_id="123"),
            SubProcessAction(validate_user),
            SubProcessAction(fetch_permissions),
            SetContextVariableAction(ready=True),
        ]
    )

    result = main_process.run()

    assert result["user_id"] == "123"
    assert result["user_validated"] is True
    assert result["permissions"] == ["read", "write"]
    assert result["ready"] is True


def test_subprocess_with_conditional():
    """Test sub-process used in conditional logic."""
    expensive_validation = Process(
        [
            SetContextVariableAction(validation_performed=True),
            SetContextVariableAction(is_valid=True),
        ]
    )

    main_process = Process(
        [
            SetContextVariableAction(needs_validation=True),
            CreateSpecificationAction(
                specification_factory=lambda ctx: field_equals(
                    "needs_validation", True
                ),
                ctx_var="validation_check",
            ),
            IfElseAction(
                specification="validation_check",
                actions_true=[SubProcessAction(expensive_validation)],
            ),
        ]
    )

    result = main_process.run()

    assert result["validation_performed"] is True
    assert result["is_valid"] is True


def test_nested_subprocesses():
    """Test nested sub-processes (sub-process calling sub-process)."""
    innermost = Process([SetContextVariableAction(level="innermost")])

    middle = Process(
        [SetContextVariableAction(level="middle"), SubProcessAction(innermost)]
    )

    outer = Process([SetContextVariableAction(level="outer"), SubProcessAction(middle)])

    result = outer.run()

    # Innermost wins (last to set)
    assert result["level"] == "innermost"


def test_subprocess_reusability():
    """Test that sub-process can be reused in multiple places."""
    validate = Process([SetContextVariableAction(validated=True)])

    # Use same sub-process twice
    main = Process(
        [
            SetContextVariableAction(validated=False),
            SubProcessAction(validate),
            SetContextVariableAction(first_validation_done=True),
            SetContextVariableAction(validated=False),  # Reset
            SubProcessAction(validate),  # Validate again
            SetContextVariableAction(second_validation_done=True),
        ]
    )

    result = main.run()

    assert result["validated"] is True
    assert result["first_validation_done"] is True
    assert result["second_validation_done"] is True


def test_subprocess_with_error_propagation():
    """Test that errors in sub-process propagate to parent."""

    class FailingAction:
        def execute(self, ctx):
            raise ValueError("Sub-process error")

    failing_subprocess = Process([FailingAction()])

    main = Process(
        [
            SetContextVariableAction(started=True),
            SubProcessAction(failing_subprocess),
            SetContextVariableAction(completed=True),  # Should not reach
        ]
    )

    ctx = ProcessContext()

    with pytest.raises(ValueError, match="Sub-process error"):
        main.run(ctx)

    # Only first action should have executed
    assert ctx["started"] is True
    assert "completed" not in ctx


def test_subprocess_as_reusable_workflow():
    """Test sub-process as a reusable workflow pattern."""
    # Reusable workflow: Fetch entity and validate
    fetch_and_validate = Process(
        [
            SetContextVariableAction(fetched=True),
            SetContextVariableAction(validated=True),
        ]
    )

    # Use in multiple parent workflows
    workflow_a = Process(
        [SetContextVariableAction(workflow="A"), SubProcessAction(fetch_and_validate)]
    )

    workflow_b = Process(
        [SetContextVariableAction(workflow="B"), SubProcessAction(fetch_and_validate)]
    )

    result_a = workflow_a.run()
    result_b = workflow_b.run()

    assert result_a["workflow"] == "A"
    assert result_a["fetched"] is True
    assert result_a["validated"] is True

    assert result_b["workflow"] == "B"
    assert result_b["fetched"] is True
    assert result_b["validated"] is True


def test_subprocess_factory_pattern():
    """Test creating sub-processes dynamically."""

    def create_validation_process(strict: bool) -> Process:
        if strict:
            return Process(
                [
                    SetContextVariableAction(strict_mode=True),
                    SetContextVariableAction(validated=True),
                ]
            )
        else:
            return Process(
                [
                    SetContextVariableAction(strict_mode=False),
                    SetContextVariableAction(validated=True),
                ]
            )

    main = Process(
        [
            SetContextVariableAction(use_strict=True),
            SubProcessAction(create_validation_process(strict=True)),
        ]
    )

    result = main.run()

    assert result["strict_mode"] is True
    assert result["validated"] is True
