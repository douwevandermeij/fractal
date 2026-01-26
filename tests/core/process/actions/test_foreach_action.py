"""Tests for ForEachAction with dynamic iterables."""

import pytest

from fractal.core.process.actions import SetContextVariableAction
from fractal.core.process.actions.control_flow import ForEachAction
from fractal.core.process.process_context import ProcessContext


def test_foreach_static_iterable():
    """Test ForEachAction with static list."""
    results = []

    class CollectAction:
        def execute(self, ctx):
            results.append(ctx["item"])
            return ctx

    action = ForEachAction([1, 2, 3], [CollectAction()])
    ctx = ProcessContext()
    action.execute(ctx)

    assert results == [1, 2, 3]


def test_foreach_context_field_lookup():
    """Test ForEachAction with field name lookup from context."""
    action = ForEachAction(
        "entities", [SetContextVariableAction(processed=True)]  # Lookup from context
    )

    ctx = ProcessContext({"entities": ["user1", "user2", "user3"]})

    result = action.execute(ctx)

    # Item should be set to last item
    assert result["item"] == "user3"
    assert result["processed"] is True


def test_foreach_callable():
    """Test ForEachAction with callable that returns iterable."""
    action = ForEachAction(
        lambda ctx: range(ctx["count"]), [SetContextVariableAction(seen=True)]
    )

    ctx = ProcessContext({"count": 5})
    result = action.execute(ctx)

    # Should have iterated 5 times
    assert result["item"] == 4  # Last item (0-4)
    assert result["seen"] is True


def test_foreach_custom_item_field():
    """Test ForEachAction with custom item field name."""
    results = []

    class CollectAction:
        def execute(self, ctx):
            results.append(ctx["user"])
            return ctx

    action = ForEachAction(
        ["alice", "bob", "charlie"],
        [CollectAction()],
        item_field="user",  # Custom field name
    )

    ctx = ProcessContext()
    result = action.execute(ctx)

    assert results == ["alice", "bob", "charlie"]
    assert result["user"] == "charlie"  # Last user


def test_foreach_with_context_mutation():
    """Test that context mutations persist across iterations."""

    class IncrementAction:
        def execute(self, ctx):
            ctx["counter"] = ctx.get("counter", 0) + 1
            return ctx

    action = ForEachAction([1, 2, 3, 4, 5], [IncrementAction()])

    ctx = ProcessContext()
    result = action.execute(ctx)

    # Counter should have been incremented 5 times
    assert result["counter"] == 5


def test_foreach_empty_iterable():
    """Test ForEachAction with empty iterable."""
    executed = []

    class TrackAction:
        def execute(self, ctx):
            executed.append(True)
            return ctx

    action = ForEachAction([], [TrackAction()])
    ctx = ProcessContext()
    action.execute(ctx)

    # Should not execute at all
    assert executed == []


def test_foreach_missing_context_field_raises():
    """Test that missing context field raises KeyError."""
    action = ForEachAction("missing_field", [SetContextVariableAction(x=1)])
    ctx = ProcessContext()

    with pytest.raises(KeyError, match="missing_field"):
        action.execute(ctx)


def test_foreach_callable_with_repository():
    """Test ForEachAction with callable fetching from repository."""

    # Mock repository
    class MockRepository:
        def find_all(self):
            return ["entity1", "entity2", "entity3"]

    class MockContext:
        def __init__(self):
            self.entity_repository = MockRepository()

    results = []

    class ProcessEntityAction:
        def execute(self, ctx):
            results.append(ctx["entity"])
            return ctx

    action = ForEachAction(
        lambda ctx: ctx.fractal["context"].entity_repository.find_all(),
        [ProcessEntityAction()],
        item_field="entity",
    )

    ctx = ProcessContext({"fractal": {"context": MockContext()}})

    action.execute(ctx)

    assert results == ["entity1", "entity2", "entity3"]


def test_foreach_nested_loops():
    """Test nested ForEachAction (loop in a loop)."""
    results = []

    class CollectPairAction:
        def execute(self, ctx):
            results.append((ctx["outer"], ctx["inner"]))
            return ctx

    inner_loop = ForEachAction("inner_items", [CollectPairAction()], item_field="inner")

    outer_loop = ForEachAction(
        ["A", "B"],
        [SetContextVariableAction(inner_items=[1, 2]), inner_loop],
        item_field="outer",
    )

    ctx = ProcessContext()
    outer_loop.execute(ctx)

    # Should produce all combinations
    assert results == [("A", 1), ("A", 2), ("B", 1), ("B", 2)]
