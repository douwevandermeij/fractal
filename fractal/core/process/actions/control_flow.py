from typing import Iterable, List, Optional

from fractal_specifications.generic.specification import Specification

from fractal.core.process.action import Action
from fractal.core.process.process import Process
from fractal.core.process.process_context import ProcessContext


class IfElseAction(Action):
    def __init__(
        self,
        specification: Specification,
        actions_true: List[Action],
        actions_false: Optional[List[Action]] = None,
    ):
        self.specification = specification
        self.process_true = Process(actions_true)
        self.process_false = Process(actions_false) if actions_false else None

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        if self.specification.is_satisfied_by(ctx):
            ctx.update(self.process_true.run(ctx))
        elif self.process_false:
            ctx.update(self.process_false.run(ctx))
        return ctx


class WhileAction(Action):
    def __init__(self, specification: Specification, actions: List[Action]):
        self.specification = specification
        self.process = Process(actions)

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        while self.specification.is_satisfied_by(ctx):
            ctx.update(self.process.run(ctx))
        return ctx


class ForEachAction(Action):
    def __init__(self, iterable: Iterable, actions: List[Action]):
        self.iterable = iterable
        self.process = Process(actions)

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        for item in self.iterable:
            ctx["item"] = item
            ctx.update(self.process.run(ctx))
        return ctx


class TryExceptAction(Action):
    """Execute actions with error handling."""

    def __init__(
        self,
        actions: List[Action],
        except_actions: Optional[List[Action]] = None,
        finally_actions: Optional[List[Action]] = None,
    ):
        """
        Args:
            actions: Actions to try executing
            except_actions: Actions to run if exception occurs (optional)
            finally_actions: Actions to always run after try/except (optional)
        """
        self.process = Process(actions)
        self.except_process = Process(except_actions) if except_actions else None
        self.finally_process = Process(finally_actions) if finally_actions else None

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        try:
            ctx.update(self.process.run(ctx))
        except Exception as e:
            ctx["last_error"] = e
            ctx["last_error_type"] = type(e).__name__
            ctx["last_error_message"] = str(e)
            if self.except_process:
                ctx.update(self.except_process.run(ctx))
        finally:
            if self.finally_process:
                ctx.update(self.finally_process.run(ctx))
        return ctx


class ParallelAction(Action):
    """Execute multiple actions concurrently using asyncio.

    Each action runs in its own context copy to avoid conflicts. Results are merged
    back into the main context. Exceptions are collected in the 'parallel_errors' list
    rather than raised immediately.

    Example:
        ParallelAction([
            QueryAction(lambda ctx: ctx.fractal.context.house_repository.get(id1), "house1"),
            QueryAction(lambda ctx: ctx.fractal.context.house_repository.get(id2), "house2"),
            QueryAction(lambda ctx: ctx.fractal.context.house_repository.get(id3), "house3"),
        ])
    """

    def __init__(self, actions: List[Action]):
        """
        Args:
            actions: List of actions to execute in parallel
        """
        self.actions = actions

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        import asyncio

        async def run_parallel():
            # Execute each action in a separate context copy to avoid conflicts
            tasks = []
            for action in self.actions:
                # Create a deep copy of the context for each action
                local_ctx = ctx.copy()
                tasks.append(self._run_action_async(action, local_ctx))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Merge results back into main context
            for result in results:
                if isinstance(result, Exception):
                    # Store exception but don't raise
                    if "parallel_errors" not in ctx:
                        ctx["parallel_errors"] = []
                    ctx["parallel_errors"].append(result)
                elif isinstance(result, ProcessContext):
                    ctx.update(result)

            return ctx

        return asyncio.run(run_parallel())

    async def _run_action_async(self, action, ctx):
        """Execute action asynchronously, handling both sync and async actions."""
        import asyncio

        try:
            # Run in thread pool for sync actions
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, action.execute, ctx)
        except Exception as e:
            return e
