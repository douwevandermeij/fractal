from abc import ABC, abstractmethod

from fractal.core.process.process_context import ProcessContext


class Action(ABC):
    def execute(self, ctx: ProcessContext) -> ProcessContext:
        """Execute the action"""


class AsyncAction(Action, ABC):
    """Base class for asynchronous actions.

    AsyncAction provides async execution support while maintaining backward
    compatibility with sync execution through the execute() method.

    Subclasses should implement execute_async() for async execution logic.
    The sync execute() method is automatically provided as a wrapper.
    """

    @abstractmethod
    async def execute_async(self, ctx: ProcessContext) -> ProcessContext:
        """Execute the action asynchronously.

        Args:
            ctx: ProcessContext to execute action with

        Returns:
            Updated ProcessContext after action execution
        """

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        """Sync wrapper that runs async execution.

        This allows AsyncAction to be used in regular Process workflows
        that expect sync execution.

        Args:
            ctx: ProcessContext to execute action with

        Returns:
            Updated ProcessContext after action execution
        """
        import asyncio

        return asyncio.run(self.execute_async(ctx))
