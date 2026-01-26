"""Tests for ParallelAction."""

import time

from fractal.core.process.actions import QueryAction, SetContextVariableAction
from fractal.core.process.actions.control_flow import ParallelAction
from fractal.core.process.process_context import ProcessContext


def test_parallel_action_executes_multiple_actions():
    """Test that ParallelAction executes multiple actions concurrently."""

    # Define query actions that simulate I/O operations
    def slow_query_1(scope):
        time.sleep(0.1)
        return "result_1"

    def slow_query_2(scope):
        time.sleep(0.1)
        return "result_2"

    def slow_query_3(scope):
        time.sleep(0.1)
        return "result_3"

    action = ParallelAction(
        [
            QueryAction(slow_query_1, "result1"),
            QueryAction(slow_query_2, "result2"),
            QueryAction(slow_query_3, "result3"),
        ]
    )

    scope = ProcessContext()
    start_time = time.time()
    result = action.execute(scope)
    elapsed_time = time.time() - start_time

    # Verify results are present
    assert result["result1"] == "result_1"
    assert result["result2"] == "result_2"
    assert result["result3"] == "result_3"

    # Verify execution was concurrent (should be ~0.1s, not ~0.3s)
    assert elapsed_time < 0.25, f"Expected concurrent execution, took {elapsed_time}s"


def test_parallel_action_merges_scopes():
    """Test that results from parallel actions are merged into main scope."""
    action = ParallelAction(
        [
            SetContextVariableAction(key1="value1"),
            SetContextVariableAction(key2="value2"),
            SetContextVariableAction(key3="value3"),
        ]
    )

    scope = ProcessContext({"initial": "data"})
    result = action.execute(scope)

    # All values should be present
    assert result["initial"] == "data"
    assert result["key1"] == "value1"
    assert result["key2"] == "value2"
    assert result["key3"] == "value3"


def test_parallel_action_handles_exceptions():
    """Test that exceptions in parallel actions are collected, not raised."""

    def failing_query(scope):
        raise ValueError("Test error")

    def successful_query(scope):
        return "success"

    action = ParallelAction(
        [
            QueryAction(failing_query, "fail_result"),
            QueryAction(successful_query, "success_result"),
        ]
    )

    scope = ProcessContext()
    result = action.execute(scope)

    # Successful action should complete
    assert result["success_result"] == "success"

    # Exception should be stored in parallel_errors
    assert "parallel_errors" in result
    assert len(result["parallel_errors"]) == 1
    assert isinstance(result["parallel_errors"][0], ValueError)
    assert str(result["parallel_errors"][0]) == "Test error"


def test_parallel_action_with_empty_list():
    """Test ParallelAction with no actions."""
    action = ParallelAction([])

    scope = ProcessContext({"initial": "data"})
    result = action.execute(scope)

    # Scope should be unchanged
    assert result["initial"] == "data"
    assert "parallel_errors" not in result


def test_parallel_action_preserves_original_scope():
    """Test that original scope values are preserved."""
    action = ParallelAction(
        [
            SetContextVariableAction(new_key="new_value"),
            QueryAction(lambda s: s["original"] + "_modified", "modified"),
        ]
    )

    scope = ProcessContext({"original": "value"})
    result = action.execute(scope)

    # Original and new values should both be present
    assert result["original"] == "value"
    assert result["new_key"] == "new_value"
    assert result["modified"] == "value_modified"


def test_parallel_action_multiple_exceptions():
    """Test that multiple exceptions are all collected."""

    def error_1(scope):
        raise ValueError("Error 1")

    def error_2(scope):
        raise TypeError("Error 2")

    def error_3(scope):
        raise RuntimeError("Error 3")

    action = ParallelAction(
        [
            QueryAction(error_1, "result1"),
            QueryAction(error_2, "result2"),
            QueryAction(error_3, "result3"),
        ]
    )

    scope = ProcessContext()
    result = action.execute(scope)

    # All exceptions should be collected
    assert "parallel_errors" in result
    assert len(result["parallel_errors"]) == 3

    error_types = [type(e).__name__ for e in result["parallel_errors"]]
    assert "ValueError" in error_types
    assert "TypeError" in error_types
    assert "RuntimeError" in error_types


def test_parallel_action_with_nested_scope_access():
    """Test ParallelAction with actions that access nested scope values."""
    action = ParallelAction(
        [
            QueryAction(lambda s: s["count"] * 2, "doubled"),
            QueryAction(lambda s: s["count"] * 3, "tripled"),
            QueryAction(lambda s: s["count"] * 4, "quadrupled"),
        ]
    )

    scope = ProcessContext({"count": 5})
    result = action.execute(scope)

    assert result["doubled"] == 10
    assert result["tripled"] == 15
    assert result["quadrupled"] == 20
    assert result["count"] == 5  # Original value preserved
