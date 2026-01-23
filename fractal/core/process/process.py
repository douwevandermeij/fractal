from typing import List, Optional

from fractal.core.process.action import Action, AsyncAction
from fractal.core.process.process_context import ProcessContext


class Process:
    def __init__(self, actions: List[Action]):
        self.actions = actions

    def run(self, ctx: Optional[ProcessContext] = None) -> ProcessContext:
        if not ctx:
            ctx = ProcessContext()
        for action in self.actions:
            ctx.update(action.execute(ctx))
        return ctx


class AsyncProcess:
    """Process that supports async action execution.

    AsyncProcess can execute both sync and async actions efficiently.
    When encountering AsyncAction, it uses native async execution.
    For regular Action instances, it falls back to sync execution.

    Example:
        process = AsyncProcess([
            AsyncQueryAction(...),
            CommandAction(...),  # sync action works fine
            AsyncCommandAction(...),
        ])
        result = await process.run_async()
    """

    def __init__(self, actions: List[Action]):
        """Initialize AsyncProcess with a list of actions.

        Args:
            actions: List of Action or AsyncAction instances
        """
        self.actions = actions

    async def run_async(self, ctx: Optional[ProcessContext] = None) -> ProcessContext:
        """Execute actions asynchronously.

        Args:
            ctx: Initial ProcessContext (optional, creates new if not provided)

        Returns:
            Final ProcessContext after all actions executed
        """
        if not ctx:
            ctx = ProcessContext()

        for action in self.actions:
            if isinstance(action, AsyncAction):
                ctx.update(await action.execute_async(ctx))
            else:
                ctx.update(action.execute(ctx))

        return ctx

    def run(self, ctx: Optional[ProcessContext] = None) -> ProcessContext:
        """Sync wrapper for async execution.

        Allows AsyncProcess to be used in sync contexts.

        Args:
            ctx: Initial ProcessContext (optional)

        Returns:
            Final ProcessContext after all actions executed
        """
        import asyncio

        return asyncio.run(self.run_async(ctx))
