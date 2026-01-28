"""Tests for control flow actions with context-based specifications."""

import pytest

from fractal.core.process.actions import (
    CreateSpecificationAction,
    IncreaseValueAction,
    SetContextVariableAction,
)
from fractal.core.process.actions.control_flow import IfElseAction, WhileAction
from fractal.core.process.process import Process
from fractal.core.process.process_context import ProcessContext
from fractal.core.process.specifications import field_equals, field_gt, field_lt


class TestIfElseActionWithContextSpec:
    """Test IfElseAction with context-based specifications."""

    def test_ifelse_with_default_specification_var(self):
        """Test IfElseAction using default 'specification' context variable."""
        process = Process(
            [
                SetContextVariableAction(status="active"),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_equals("status", "active")
                ),
                IfElseAction(
                    actions_true=[SetContextVariableAction(result="status is active")],
                    actions_false=[
                        SetContextVariableAction(result="status is not active")
                    ],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["result"] == "status is active"

    def test_ifelse_with_custom_specification_var(self):
        """Test IfElseAction using custom specification context variable."""
        process = Process(
            [
                SetContextVariableAction(count=10),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_gt("count", 5),
                    ctx_var="count_check",
                ),
                IfElseAction(
                    specification="count_check",
                    actions_true=[SetContextVariableAction(result="count is high")],
                    actions_false=[SetContextVariableAction(result="count is low")],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["result"] == "count is high"

    def test_ifelse_false_branch(self):
        """Test IfElseAction taking the false branch."""
        process = Process(
            [
                SetContextVariableAction(count=3),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_gt("count", 5),
                    ctx_var="count_check",
                ),
                IfElseAction(
                    specification="count_check",
                    actions_true=[SetContextVariableAction(result="count is high")],
                    actions_false=[SetContextVariableAction(result="count is low")],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["result"] == "count is low"

    def test_ifelse_no_false_branch(self):
        """Test IfElseAction with no false branch."""
        process = Process(
            [
                SetContextVariableAction(count=3),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_gt("count", 5),
                    ctx_var="check",
                ),
                IfElseAction(
                    specification="check",
                    actions_true=[SetContextVariableAction(result="executed")],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert "result" not in result

    def test_ifelse_with_dot_notation_specification(self):
        """Test IfElseAction with specification from nested context."""
        process = Process(
            [
                SetContextVariableAction(value=100),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_gt("value", 50),
                    ctx_var="checks.value_check",
                ),
                IfElseAction(
                    specification="checks.value_check",
                    actions_true=[SetContextVariableAction(result="high value")],
                    actions_false=[SetContextVariableAction(result="low value")],
                ),
            ]
        )

        result = process.run(ProcessContext({"checks": {}}))
        assert result["result"] == "high value"

    def test_ifelse_raises_error_when_specification_not_found(self):
        """Test that IfElseAction raises error when specification not in context."""
        action = IfElseAction(
            specification="missing_spec",
            actions_true=[SetContextVariableAction(result="true")],
        )

        with pytest.raises(KeyError, match="missing_spec"):
            action.execute(ProcessContext({}))

    def test_ifelse_with_dynamic_specification(self):
        """Test IfElseAction with specification created from runtime values."""
        process = Process(
            [
                SetContextVariableAction(threshold=50, value=75),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_gt(
                        "value", ctx["threshold"]
                    ),
                    ctx_var="dynamic_check",
                ),
                IfElseAction(
                    specification="dynamic_check",
                    actions_true=[SetContextVariableAction(result="above threshold")],
                    actions_false=[SetContextVariableAction(result="below threshold")],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["result"] == "above threshold"

    def test_ifelse_complex_actions(self):
        """Test IfElseAction with complex actions in both branches."""
        process = Process(
            [
                SetContextVariableAction(count=0),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_equals("count", 0),
                    ctx_var="zero_check",
                ),
                IfElseAction(
                    specification="zero_check",
                    actions_true=[
                        IncreaseValueAction(ctx_var="count", value=10),
                        SetContextVariableAction(message="initialized"),
                    ],
                    actions_false=[
                        IncreaseValueAction(ctx_var="count", value=1),
                        SetContextVariableAction(message="incremented"),
                    ],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["count"] == 10
        assert result["message"] == "initialized"


class TestWhileActionWithContextSpec:
    """Test WhileAction with context-based specifications."""

    def test_while_with_default_specification_var(self):
        """Test WhileAction using default 'specification' context variable."""
        process = Process(
            [
                SetContextVariableAction(count=0),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_lt("count", 5)
                ),
                WhileAction(
                    actions=[IncreaseValueAction(ctx_var="count", value=1)],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["count"] == 5

    def test_while_with_custom_specification_var(self):
        """Test WhileAction using custom specification context variable."""
        process = Process(
            [
                SetContextVariableAction(counter=0),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_lt("counter", 3),
                    ctx_var="loop_condition",
                ),
                WhileAction(
                    specification="loop_condition",
                    actions=[IncreaseValueAction(ctx_var="counter", value=1)],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["counter"] == 3

    def test_while_zero_iterations(self):
        """Test WhileAction that executes zero times."""
        process = Process(
            [
                SetContextVariableAction(count=10),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_lt("count", 5),
                    ctx_var="check",
                ),
                WhileAction(
                    specification="check",
                    actions=[
                        IncreaseValueAction(ctx_var="count", value=1),
                        SetContextVariableAction(executed=True),
                    ],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["count"] == 10
        assert "executed" not in result

    def test_while_with_multiple_actions(self):
        """Test WhileAction with multiple actions in loop."""
        process = Process(
            [
                SetContextVariableAction(count=0, sum=0),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_lt("count", 5),
                    ctx_var="check",
                ),
                WhileAction(
                    specification="check",
                    actions=[
                        IncreaseValueAction(ctx_var="count", value=1),
                        IncreaseValueAction(ctx_var="sum", value=10),
                    ],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["count"] == 5
        assert result["sum"] == 50

    def test_while_with_dot_notation_specification(self):
        """Test WhileAction with specification from nested context."""
        process = Process(
            [
                SetContextVariableAction(iteration=0),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_lt("iteration", 3),
                    ctx_var="loop.condition",
                ),
                WhileAction(
                    specification="loop.condition",
                    actions=[IncreaseValueAction(ctx_var="iteration", value=1)],
                ),
            ]
        )

        result = process.run(ProcessContext({"loop": {}}))
        assert result["iteration"] == 3

    def test_while_raises_error_when_specification_not_found(self):
        """Test that WhileAction raises error when specification not in context."""
        action = WhileAction(
            specification="missing_spec",
            actions=[SetContextVariableAction(result="executed")],
        )

        with pytest.raises(KeyError, match="missing_spec"):
            action.execute(ProcessContext({}))

    def test_while_with_dynamic_specification(self):
        """Test WhileAction with specification created from runtime values."""
        process = Process(
            [
                SetContextVariableAction(max_iterations=4, current=0),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_lt(
                        "current", ctx["max_iterations"]
                    ),
                    ctx_var="loop_check",
                ),
                WhileAction(
                    specification="loop_check",
                    actions=[IncreaseValueAction(ctx_var="current", value=1)],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["current"] == 4

    def test_while_nested_in_ifelse(self):
        """Test WhileAction nested inside IfElseAction."""
        process = Process(
            [
                SetContextVariableAction(should_loop=True, count=0),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_equals("should_loop", True),
                    ctx_var="if_check",
                ),
                IfElseAction(
                    specification="if_check",
                    actions_true=[
                        CreateSpecificationAction(
                            specification_factory=lambda ctx: field_lt("count", 3),
                            ctx_var="while_check",
                        ),
                        WhileAction(
                            specification="while_check",
                            actions=[IncreaseValueAction(ctx_var="count", value=1)],
                        ),
                    ],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["count"] == 3


class TestCompleteWorkflowsWithControlFlow:
    """Test complete workflows using control flow actions with context-based specifications."""

    def test_nested_ifelse_actions(self):
        """Test nested IfElseAction with different specifications."""
        process = Process(
            [
                SetContextVariableAction(level=2),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_gt("level", 0),
                    ctx_var="level_check",
                ),
                IfElseAction(
                    specification="level_check",
                    actions_true=[
                        CreateSpecificationAction(
                            specification_factory=lambda ctx: field_gt("level", 1),
                            ctx_var="high_check",
                        ),
                        IfElseAction(
                            specification="high_check",
                            actions_true=[
                                SetContextVariableAction(result="high level")
                            ],
                            actions_false=[
                                SetContextVariableAction(result="medium level")
                            ],
                        ),
                    ],
                    actions_false=[SetContextVariableAction(result="no level")],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["result"] == "high level"

    def test_ifelse_with_while_loop(self):
        """Test IfElseAction containing WhileAction."""
        process = Process(
            [
                SetContextVariableAction(process_items=True, items_processed=0),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_equals(
                        "process_items", True
                    ),
                    ctx_var="should_process",
                ),
                IfElseAction(
                    specification="should_process",
                    actions_true=[
                        CreateSpecificationAction(
                            specification_factory=lambda ctx: field_lt(
                                "items_processed", 5
                            ),
                            ctx_var="has_items",
                        ),
                        WhileAction(
                            specification="has_items",
                            actions=[
                                IncreaseValueAction(ctx_var="items_processed", value=1)
                            ],
                        ),
                    ],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["items_processed"] == 5

    def test_multiple_specifications_reused(self):
        """Test creating multiple specifications and reusing them."""
        process = Process(
            [
                SetContextVariableAction(count=5),
                # Create multiple specifications
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_gt("count", 0),
                    ctx_var="positive_check",
                ),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_lt("count", 10),
                    ctx_var="small_check",
                ),
                # Use first specification
                IfElseAction(
                    specification="positive_check",
                    actions_true=[
                        # Use second specification
                        IfElseAction(
                            specification="small_check",
                            actions_true=[
                                SetContextVariableAction(result="positive and small")
                            ],
                            actions_false=[
                                SetContextVariableAction(result="positive and large")
                            ],
                        )
                    ],
                    actions_false=[SetContextVariableAction(result="not positive")],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["result"] == "positive and small"

    def test_complex_counting_workflow(self):
        """Test complex workflow with both IfElse and While actions."""
        process = Process(
            [
                SetContextVariableAction(mode="count", counter=0, target=0),
                # Check mode
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_equals("mode", "count"),
                    ctx_var="mode_check",
                ),
                IfElseAction(
                    specification="mode_check",
                    actions_true=[
                        # Set target
                        SetContextVariableAction(target=10),
                        # Create while condition
                        CreateSpecificationAction(
                            specification_factory=lambda ctx: field_lt(
                                "counter", ctx["target"]
                            ),
                            ctx_var="count_condition",
                        ),
                        # Count loop
                        WhileAction(
                            specification="count_condition",
                            actions=[
                                IncreaseValueAction(ctx_var="counter", value=2),
                            ],
                        ),
                        # Set completion flag
                        SetContextVariableAction(completed=True),
                    ],
                    actions_false=[SetContextVariableAction(completed=False)],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["counter"] == 10
        assert result["completed"] is True
