from typing import Callable, Optional

from fractal_specifications.generic.specification import Specification

from fractal.core.process.action import Action
from fractal.core.process.process_context import ProcessContext, _expand_dotted_keys


def _get_nested_value(ctx, field: str):
    """Get nested field value using dot notation.

    Args:
        ctx: ProcessContext or object to navigate
        field: Field name, can use dot notation for nested access (e.g., "user.email")

    Returns:
        Field value

    Raises:
        KeyError: If field is not found or is None during navigation
    """
    value = ctx
    for part in field.split("."):
        if hasattr(value, "get"):
            value = value.get(part)
        elif hasattr(value, part):
            value = getattr(value, part)
        else:
            raise KeyError(f"Field '{field}' not found in context")
        if value is None:
            raise KeyError(f"Field '{field}' is None")
    return value


class SetContextVariableAction(Action):
    """Set context variables with support for dot notation.

    Supports both simple keys and dot notation for nested structures:
        SetContextVariableAction(user_name="Alice")
        # Results in: ctx["user_name"] = "Alice"

        SetContextVariableAction(**{"fractal.context": app_context})
        # Results in: ctx["fractal"]["context"] = app_context

    Note: Use **{} syntax for dotted keys since Python doesn't allow dots in kwarg names.
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        # Expand dotted keys into nested structure
        expanded = _expand_dotted_keys(self.kwargs)
        return ctx.update(ProcessContext(expanded))


class SetValueAction(Action):
    """Set a nested field in a context variable to a value from another context variable.

    Both target and source support dot notation.

    Example:
        # Set user.name from context variable user_name
        SetValueAction(target="user.name", source="user_name")

        # Set user.address.city from another nested field
        SetValueAction(target="user.address.city", source="company.location.city")
    """

    def __init__(self, *, target: str, source: str):
        """
        Args:
            target: Target field to set (supports dot notation, e.g., "user.name")
            source: Source context variable to read from (supports dot notation, e.g., "user_name")
        """
        self.target = target
        self.source = source

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        # Get the source value from context
        source_value = _get_nested_value(ctx, self.source)

        # Set the target field
        self._set_nested(ctx, self.target, source_value)

        return ctx

    @staticmethod
    def _set_nested(ctx, field: str, value):
        """Set nested field value using dot notation."""
        parts = field.split(".")

        if len(parts) == 1:
            # Simple field - set directly in context
            ctx[field] = value
            return

        # Navigate to the parent object
        parent = ctx
        path_so_far = []
        for part in parts[:-1]:
            path_so_far.append(part)
            if hasattr(parent, "get"):
                parent = parent.get(part)
            elif hasattr(parent, part):
                parent = getattr(parent, part)
            else:
                raise KeyError(f"Cannot navigate to '{'.'.join(path_so_far)}'")

            # Check if we got None during navigation
            if parent is None:
                raise KeyError(f"Field '{'.'.join(path_so_far)}' is None")

        # Set the final field
        final_field = parts[-1]
        if hasattr(parent, "__setitem__"):
            parent[final_field] = value
        elif hasattr(parent, final_field):
            setattr(parent, final_field, value)
        else:
            raise AttributeError(f"Cannot set field '{final_field}' on object")


class GetValueAction(Action):
    """Get a nested field from context and store it in a context variable.

    This is the inverse of SetValueAction - it extracts values from objects
    into top-level context variables.

    Example:
        # Extract user.email into context variable user_email
        GetValueAction(target="user_email", source="user.email")

        # Extract nested field
        GetValueAction(target="city", source="company.address.city")
    """

    def __init__(self, *, target: str, source: str):
        """
        Args:
            target: Context variable name to store the value (simple name, no dots)
            source: Source field to read from (supports dot notation, e.g., "user.email")
        """
        self.target = target
        self.source = source

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        # Get the source value (supports dot notation)
        source_value = _get_nested_value(ctx, self.source)

        # Set the target (simple context variable)
        ctx[self.target] = source_value

        return ctx


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
