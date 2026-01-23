from typing import Callable, Optional

from fractal_specifications.generic.specification import Specification

from fractal.core.process.action import Action
from fractal.core.process.process_context import ProcessContext


class SetValueAction(Action):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        return ctx.update(ProcessContext(self.kwargs))


class ApplyToValueAction(Action):
    def __init__(self, *, field: str, function: Callable):
        self.field = field
        self.function = function

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        ctx[self.field] = self.function(ctx[self.field])
        return ctx


class IncreaseValueAction(Action):
    def __init__(self, *, field: str, value):
        self.field = field
        self.value = value

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        ctx[self.field] += self.value
        return ctx


class PrintAction(Action):
    def __init__(self, *, text):
        self.text = text

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        print(self.text)
        return ctx


class PrintValueAction(Action):
    def __init__(self, *, field: str):
        self.field = field

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        print(ctx[self.field])
        return ctx


class AddEntityAction(Action):
    def __init__(self, *, repository_name: str, entity: str = "entity"):
        self.repository_name = repository_name
        self.entity = entity

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        repository = getattr(ctx.fractal.context, self.repository_name)
        repository.add(getattr(ctx, self.entity))
        return ctx


class UpdateEntityAction(Action):
    def __init__(
        self, *, repository_name: str, entity: str = "entity", upsert: bool = False
    ):
        self.repository_name = repository_name
        self.entity = entity
        self.upsert = upsert

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        repository = getattr(ctx.fractal.context, self.repository_name)
        repository.update(getattr(ctx, self.entity), self.upsert)
        return ctx


class FetchEntityAction(Action):
    def __init__(
        self,
        *,
        repository_name: str,
        specification: Specification,
        entity: str = "entity",
    ):
        self.repository_name = repository_name
        self.specification = specification
        self.entity = entity

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        repository = getattr(ctx.fractal.context, self.repository_name)
        ctx[self.entity] = repository.find_one(self.specification)
        return ctx


class FindEntitiesAction(Action):
    def __init__(
        self,
        *,
        repository_name: str,
        specification: Optional[Specification] = None,
        entities: str = "entities",
    ):
        self.repository_name = repository_name
        self.specification = specification
        self.entities = entities

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        repository = getattr(ctx.fractal.context, self.repository_name)
        ctx[self.entities] = repository.find(self.specification)
        return ctx


class DeleteEntityAction(Action):
    def __init__(self, *, repository_name: str, specification: Specification):
        self.repository_name = repository_name
        self.specification = specification

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        repository = getattr(ctx.fractal.context, self.repository_name)
        repository.remove_one(self.specification)
        return ctx


class CommandAction(Action):
    """Execute a command through the command bus."""

    def __init__(self, command_factory: Callable):
        """
        Args:
            command_factory: Callable that takes ProcessContext and returns Command.
                           Can access ctx.fractal.context for ApplicationContext.
        """
        self.command_factory = command_factory

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        command = self.command_factory(ctx)
        result = ctx.fractal.context.command_bus.handle(command)
        ctx["last_command_result"] = result
        return ctx


class QueryAction(Action):
    """Execute a query/function and store result in context."""

    def __init__(self, query_func: Callable, result_field: str = "last_query_result"):
        """
        Args:
            query_func: Callable that takes ProcessContext and returns result
            result_field: Field name to store result in context (default: "last_query_result")
        """
        self.query_func = query_func
        self.result_field = result_field

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        result = self.query_func(ctx)
        ctx[self.result_field] = result
        return ctx


# Async action variants - requires AsyncAction import
try:
    from fractal.core.process.action import AsyncAction

    class AsyncCommandAction(AsyncAction):
        """Execute a command asynchronously through the command bus.

        Requires command bus to have handle_async method.

        Example:
            AsyncCommandAction(lambda ctx: CreateHouseCommand(
                name=ctx.house_name,
                address=ctx.house_address
            ))
        """

        def __init__(self, command_factory: Callable):
            """
            Args:
                command_factory: Callable that takes ProcessContext and returns Command
            """
            self.command_factory = command_factory

        async def execute_async(self, ctx: ProcessContext) -> ProcessContext:
            command = self.command_factory(ctx)
            result = await ctx.fractal.context.command_bus.handle_async(command)
            ctx["last_command_result"] = result
            return ctx

    class AsyncQueryAction(AsyncAction):
        """Execute an async query/function and store result in context.

        Example:
            AsyncQueryAction(
                lambda ctx: await_fetch_houses_async(ctx.filter_status),
                "houses"
            )
        """

        def __init__(
            self, query_func: Callable, result_field: str = "last_query_result"
        ):
            """
            Args:
                query_func: Async callable that takes ProcessContext and returns result
                result_field: Field name to store result in context
            """
            self.query_func = query_func
            self.result_field = result_field

        async def execute_async(self, ctx: ProcessContext) -> ProcessContext:
            result = await self.query_func(ctx)
            ctx[self.result_field] = result
            return ctx

except ImportError:
    # AsyncAction not available in older versions
    pass
