"""Tests for AsyncProcess and async actions."""

import asyncio

import pytest

from fractal.core.process.action import AsyncAction
from fractal.core.process.actions import (
    AsyncCommandAction,
    AsyncQueryAction,
    SetContextVariableAction,
)
from fractal.core.process.process import AsyncProcess
from fractal.core.process.process_context import ProcessContext


class CustomAsyncAction(AsyncAction):
    """Custom async action for testing."""

    def __init__(self, value: str, delay: float = 0.1):
        self.value = value
        self.delay = delay

    async def execute_async(self, scope: ProcessContext) -> ProcessContext:
        await asyncio.sleep(self.delay)
        scope["async_result"] = self.value
        return scope


@pytest.mark.asyncio
async def test_async_process_with_async_actions():
    """Test AsyncProcess executes async actions."""
    process = AsyncProcess(
        [
            CustomAsyncAction("test_value"),
        ]
    )

    scope = await process.run_async()
    assert scope["async_result"] == "test_value"


@pytest.mark.asyncio
async def test_async_process_with_mixed_actions():
    """Test AsyncProcess with both sync and async actions."""
    process = AsyncProcess(
        [
            SetContextVariableAction(sync_value="sync"),
            CustomAsyncAction("async"),
        ]
    )

    scope = await process.run_async()
    assert scope["sync_value"] == "sync"
    assert scope["async_result"] == "async"


@pytest.mark.asyncio
async def test_async_process_preserves_order():
    """Test that actions execute in order."""
    process = AsyncProcess(
        [
            SetContextVariableAction(step="1"),
            CustomAsyncAction("2", delay=0.05),
            SetContextVariableAction(step="3"),
            CustomAsyncAction("4", delay=0.05),
        ]
    )

    scope = await process.run_async()
    # Each action should see previous results
    assert scope["step"] == "3"  # Last SetContextVariableAction overwrites
    assert scope["async_result"] == "4"  # Last async action result


@pytest.mark.asyncio
async def test_async_query_action():
    """Test AsyncQueryAction execution."""

    async def async_query(scope):
        await asyncio.sleep(0.05)
        return scope["input_value"] * 2

    action = AsyncQueryAction(async_query, "output_value")
    scope = ProcessContext({"input_value": 5})

    result = await action.execute_async(scope)
    assert result["output_value"] == 10


@pytest.mark.asyncio
async def test_async_command_action():
    """Test AsyncCommandAction execution (requires mock command bus)."""
    from dataclasses import dataclass

    from fractal.core.command_bus.command import Command

    @dataclass
    class TestCommand(Command):
        value: str

    # Mock command bus with async support
    class MockCommandBus:
        async def handle_async(self, command):
            await asyncio.sleep(0.05)
            return f"handled_{command.value}"

    # Mock application context
    class MockContext:
        def __init__(self):
            self.command_bus = MockCommandBus()

    class MockFractal:
        def __init__(self):
            self.context = MockContext()

    action = AsyncCommandAction(lambda s: TestCommand(value=s["input"]))
    scope = ProcessContext({"input": "test"})
    scope["fractal"] = MockFractal()

    result = await action.execute_async(scope)
    assert result["last_command_result"] == "handled_test"


def test_async_action_sync_wrapper():
    """Test that AsyncAction.execute() provides sync wrapper."""
    action = CustomAsyncAction("test_value")
    scope = ProcessContext()

    result = action.execute(scope)
    assert result["async_result"] == "test_value"


def test_async_process_sync_wrapper():
    """Test that AsyncProcess.run() provides sync wrapper."""
    process = AsyncProcess(
        [
            CustomAsyncAction("test_value"),
            SetContextVariableAction(sync_value="sync"),
        ]
    )

    result = process.run()
    assert result["async_result"] == "test_value"
    assert result["sync_value"] == "sync"


@pytest.mark.asyncio
async def test_async_process_with_initial_scope():
    """Test AsyncProcess with initial scope data."""
    process = AsyncProcess(
        [
            CustomAsyncAction("new_value"),
        ]
    )

    initial_scope = ProcessContext({"existing": "data"})
    result = await process.run_async(initial_scope)

    assert result["existing"] == "data"
    assert result["async_result"] == "new_value"


@pytest.mark.asyncio
async def test_async_process_error_handling():
    """Test error handling in async process."""

    class FailingAsyncAction(AsyncAction):
        async def execute_async(self, scope: ProcessContext) -> ProcessContext:
            raise ValueError("Async error")

    process = AsyncProcess(
        [
            SetContextVariableAction(step="1"),
            FailingAsyncAction(),
            SetContextVariableAction(step="3"),  # Should not execute
        ]
    )

    with pytest.raises(ValueError, match="Async error"):
        await process.run_async()


@pytest.mark.asyncio
async def test_multiple_async_actions_sequential():
    """Test multiple async actions execute sequentially, not in parallel."""
    import time

    class TimedAsyncAction(AsyncAction):
        def __init__(self, key: str, delay: float = 0.1):
            self.key = key
            self.delay = delay

        async def execute_async(self, scope: ProcessContext) -> ProcessContext:
            await asyncio.sleep(self.delay)
            if "timestamps" not in scope:
                scope["timestamps"] = []
            scope["timestamps"].append((self.key, time.time()))
            return scope

    process = AsyncProcess(
        [
            TimedAsyncAction("action1", 0.1),
            TimedAsyncAction("action2", 0.1),
            TimedAsyncAction("action3", 0.1),
        ]
    )

    start_time = time.time()
    result = await process.run_async()
    elapsed = time.time() - start_time

    # Should take ~0.3s (sequential), not ~0.1s (parallel)
    assert elapsed >= 0.25
    assert len(result["timestamps"]) == 3

    # Verify order
    timestamps = result["timestamps"]
    assert timestamps[0][0] == "action1"
    assert timestamps[1][0] == "action2"
    assert timestamps[2][0] == "action3"

    # Verify they executed sequentially
    assert timestamps[1][1] > timestamps[0][1]
    assert timestamps[2][1] > timestamps[1][1]


@pytest.mark.asyncio
async def test_async_query_action_with_exception():
    """Test AsyncQueryAction error handling."""

    async def failing_query(scope):
        raise RuntimeError("Query failed")

    action = AsyncQueryAction(failing_query, "result")
    scope = ProcessContext()

    with pytest.raises(RuntimeError, match="Query failed"):
        await action.execute_async(scope)


def test_async_process_empty_actions():
    """Test AsyncProcess with no actions."""
    process = AsyncProcess([])
    result = process.run()

    assert len(result.keys()) == 0


def test_async_actions_in_regular_process():
    """Test that AsyncAction can be used in regular Process."""
    from fractal.core.process.process import Process

    process = Process(
        [
            SetContextVariableAction(value="sync"),
            CustomAsyncAction("async"),
        ]
    )

    result = process.run()
    assert result["value"] == "sync"
    assert result["async_result"] == "async"
