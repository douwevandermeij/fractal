from typing import Callable

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


def _set_nested(ctx, field: str, value):
    """Set nested field value using dot notation.

    Args:
        ctx: ProcessContext or object to navigate
        field: Field name, can use dot notation for nested setting (e.g., "user.email")
        value: Value to set

    Raises:
        KeyError: If parent path cannot be navigated
        AttributeError: If final field cannot be set
    """
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


class SetContextVariableAction(Action):
    """Set context variables with support for dot notation and callable values.

    Supports both static values and callable functions that receive the context:
        # Static values
        SetContextVariableAction(user_name="Alice")
        # Results in: ctx["user_name"] = "Alice"

        # Dynamic values using lambda functions
        SetContextVariableAction(
            doubled_price=lambda ctx: ctx["price"] * 2,
            status=lambda ctx: "active" if ctx["enabled"] else "inactive"
        )

        # Dot notation for nested structures
        SetContextVariableAction(**{"fractal.context": app_context})
        # Results in: ctx["fractal"]["context"] = app_context

    Note: Use **{} syntax for dotted keys since Python doesn't allow dots in kwarg names.
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        # Resolve callable values (lambdas/functions that take ctx)
        resolved_kwargs = {}
        for key, value in self.kwargs.items():
            if callable(value):
                # Call the function with context to get the actual value
                resolved_kwargs[key] = value(ctx)
            else:
                resolved_kwargs[key] = value

        # Expand dotted keys into nested structure
        expanded = _expand_dotted_keys(resolved_kwargs)
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
        _set_nested(ctx, self.target, source_value)

        return ctx


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
    """Apply a function to a field value and store the result back.

    Supports dot notation for nested field access.

    Example:
        # Apply function to simple field
        ApplyToValueAction(ctx_var="count", function=lambda x: x * 2)

        # Apply function to nested field
        ApplyToValueAction(ctx_var="user.preferences", function=lambda prefs: {**prefs, "theme": "dark"})
    """

    def __init__(self, *, ctx_var: str, function: Callable):
        """
        Args:
            ctx_var: Context variable name (supports dot notation, e.g., "user.preferences")
            function: Function to apply to the field value
        """
        self.ctx_var = ctx_var
        self.function = function

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        # Read with dot notation support
        current_value = _get_nested_value(ctx, self.ctx_var)
        # Apply function
        new_value = self.function(current_value)
        # Write with dot notation support
        _set_nested(ctx, self.ctx_var, new_value)
        return ctx


class PublishEventAction(Action):
    """Instantiate and publish a domain event through the event publisher.

    This action allows events to be created and published within a Process workflow.
    The event is constructed using a factory function that receives the ProcessContext,
    allowing it to access command data, entities, and other context variables.

    Example:
        PublishEventAction(
            event_factory=lambda ctx: EntityAddedEvent(
                id=ctx.command.entity.id,
                account_id=ctx.command.entity.account_id,
                data=ctx.command.entity.asdict(),
                by=ctx.command.user_id,
                on=datetime.now(timezone.utc),
                entity=ctx.command.entity,
                specification=ctx.command.specification,
            )
        )
    """

    def __init__(self, event_factory: Callable):
        """
        Args:
            event_factory: Callable that takes ProcessContext and returns an Event.
                          Can access ctx.fractal.context for ApplicationContext.
        """
        self.event_factory = event_factory

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        """Execute the action by creating and publishing the event.

        Args:
            ctx: ProcessContext containing command, entity, and application context

        Returns:
            Updated ProcessContext (unchanged, as event publishing has side effects)
        """
        event = self.event_factory(ctx)
        ctx.fractal.context.event_publisher.publish_event(event)
        return ctx


class CreateSpecificationAction(Action):
    """Create a specification using a factory function and store it in context.

    This action allows specifications to be created dynamically at runtime based on
    context values. The specification is created using a factory function that receives
    the ProcessContext and returns a Specification object.

    Example:
        # Simple specification
        CreateSpecificationAction(
            specification_factory=lambda ctx: EqualsSpecification("id", ctx["user_id"]),
            ctx_var="user_spec"
        )

        # Complex specification using context values
        CreateSpecificationAction(
            specification_factory=lambda ctx: (
                EqualsSpecification("status", ctx["filter_status"]) &
                GreaterThanSpecification("price", ctx["min_price"])
            ),
            ctx_var="house_filter"
        )

        # Specification from command
        CreateSpecificationAction(
            specification_factory=lambda ctx: ctx.command.get_specification(),
            ctx_var="validation_spec"
        )

        # Using default ctx_var
        CreateSpecificationAction(
            specification_factory=lambda ctx: EqualsSpecification("id", 1)
            # Stores in "specification" by default
        )
    """

    def __init__(
        self,
        *,
        specification_factory: Callable[[ProcessContext], Specification],
        ctx_var: str = "specification",
    ):
        """
        Args:
            specification_factory: Callable that takes ProcessContext and returns a Specification
            ctx_var: Context variable name to store the specification (default: "specification")
        """
        self.specification_factory = specification_factory
        self.ctx_var = ctx_var

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        spec = self.specification_factory(ctx)
        _set_nested(ctx, self.ctx_var, spec)
        return ctx


class IncreaseValueAction(Action):
    """Increase a numeric field value by a given amount.

    Supports dot notation for nested field access.

    Example:
        # Increase simple field
        IncreaseValueAction(ctx_var="count", value=1)

        # Increase nested field
        IncreaseValueAction(ctx_var="stats.page_views", value=1)
    """

    def __init__(self, *, ctx_var: str, value):
        """
        Args:
            ctx_var: Context variable name (supports dot notation, e.g., "stats.count")
            value: Value to add to the field
        """
        self.ctx_var = ctx_var
        self.value = value

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        # Read with dot notation support
        current_value = _get_nested_value(ctx, self.ctx_var)
        # Add value
        new_value = current_value + self.value
        # Write with dot notation support
        _set_nested(ctx, self.ctx_var, new_value)
        return ctx


class RaiseExceptionAction(Action):
    """Raise an exception with a static or dynamic message.

    This action allows raising exceptions within a Process workflow, useful for
    validation failures, error conditions, or aborting workflows.

    Example:
        # Static message
        RaiseExceptionAction(
            exception_class=ValueError,
            message="Invalid input"
        )

        # Dynamic message from context
        RaiseExceptionAction(
            exception_class=ValidationError,
            message_factory=lambda ctx: f"User {ctx['user_id']} failed validation"
        )

        # Both message and message_factory (factory takes precedence)
        RaiseExceptionAction(
            exception_class=ValueError,
            message="Default error",
            message_factory=lambda ctx: f"Error: {ctx['error_details']}" if 'error_details' in ctx else None
        )

        # Default exception class (Exception)
        RaiseExceptionAction(message="Something went wrong")

        # No message
        RaiseExceptionAction(exception_class=StopIteration)
    """

    def __init__(
        self,
        *,
        exception_class: type = Exception,
        message: str = None,
        message_factory: Callable[[ProcessContext], str] = None,
    ):
        """
        Args:
            exception_class: The exception class to raise (default: Exception)
            message: Static error message (optional)
            message_factory: Function that takes ProcessContext and returns error message (optional)
                           If both message and message_factory are provided, message_factory takes precedence.
                           If message_factory returns None, falls back to message.
        """
        self.exception_class = exception_class
        self.message = message
        self.message_factory = message_factory

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        # Determine the message
        if self.message_factory:
            dynamic_message = self.message_factory(ctx)
            final_message = (
                dynamic_message if dynamic_message is not None else self.message
            )
        else:
            final_message = self.message

        # Raise the exception
        if final_message:
            raise self.exception_class(final_message)
        else:
            raise self.exception_class()


class PrintAction(Action):
    def __init__(self, *, text):
        self.text = text

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        print(self.text)
        return ctx


class PrintValueAction(Action):
    """Print a value from the context.

    Example:
        # Print simple field
        PrintValueAction(ctx_var="user_name")

        # Print nested field (requires _get_nested_value for dot notation support)
        PrintValueAction(ctx_var="user.email")
    """

    def __init__(self, *, ctx_var: str):
        """
        Args:
            ctx_var: Context variable name to print
        """
        self.ctx_var = ctx_var

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        print(ctx[self.ctx_var])
        return ctx


class AddEntityAction(Action):
    """Add an entity to a repository.

    Reads the entity from the specified context variable and adds it to the repository.
    Supports dot notation for reading nested entity values.

    Example:
        # Add entity from simple context variable
        AddEntityAction(repository_name="user_repository", ctx_var="user")

        # Add entity from nested context variable
        AddEntityAction(repository_name="user_repository", ctx_var="request.user")
    """

    def __init__(self, *, repository_name: str, ctx_var: str = "entity"):
        """
        Args:
            repository_name: Name of repository in ApplicationContext
            ctx_var: Context variable name to read entity from (supports dot notation, default: "entity")
        """
        self.repository_name = repository_name
        self.ctx_var = ctx_var

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        repository = getattr(ctx.fractal.context, self.repository_name)
        entity_value = _get_nested_value(ctx, self.ctx_var)
        repository.add(entity_value)
        return ctx


class UpdateEntityAction(Action):
    """Update an entity in a repository.

    Reads the entity from the specified context variable and updates it in the repository.
    Supports dot notation for reading nested entity values.

    Example:
        # Update entity from simple context variable
        UpdateEntityAction(repository_name="user_repository", ctx_var="user")

        # Update entity from nested context variable
        UpdateEntityAction(repository_name="user_repository", ctx_var="request.user", upsert=True)
    """

    def __init__(
        self, *, repository_name: str, ctx_var: str = "entity", upsert: bool = False
    ):
        """
        Args:
            repository_name: Name of repository in ApplicationContext
            ctx_var: Context variable name to read entity from (supports dot notation, default: "entity")
            upsert: If True, insert entity if it doesn't exist (default: False)
        """
        self.repository_name = repository_name
        self.ctx_var = ctx_var
        self.upsert = upsert

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        repository = getattr(ctx.fractal.context, self.repository_name)
        entity_value = _get_nested_value(ctx, self.ctx_var)
        repository.update(entity_value, upsert=self.upsert)
        return ctx


class FetchEntityAction(Action):
    """Fetch a single entity from a repository and store it in context.

    The specification parameter supports both:
    - Specification object (backward compatible, will be deprecated)
    - String context variable name (new pattern, recommended)

    Supports dot notation for both the specification and entity storage fields.

    Example:
        # New pattern (recommended) - using default "specification" variable
        Process([
            CreateSpecificationAction(
                specification_factory=lambda ctx: EqualsSpecification("id", ctx["user_id"])
            ),
            FetchEntityAction(repository_name="user_repository", ctx_var="user")
        ])

        # New pattern - using custom specification variable
        Process([
            CreateSpecificationAction(
                specification_factory=lambda ctx: EqualsSpecification("id", 1),
                ctx_var="user_spec"
            ),
            FetchEntityAction(
                repository_name="user_repository",
                specification="user_spec",
                ctx_var="user"
            )
        ])

        # Old pattern (still works, but deprecated)
        FetchEntityAction(
            repository_name="user_repository",
            specification=EqualsSpecification("id", 1),
            ctx_var="user"
        )
    """

    def __init__(
        self,
        *,
        repository_name: str,
        specification="specification",
        ctx_var: str = "entity",
    ):
        """
        Args:
            repository_name: Name of repository in ApplicationContext
            specification: Either a Specification object (deprecated) or context variable name (str)
                         (default: "specification")
            ctx_var: Context variable name to store entity (supports dot notation, default: "entity")
        """
        self.repository_name = repository_name
        self.specification = specification
        self.ctx_var = ctx_var

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        repository = getattr(ctx.fractal.context, self.repository_name)

        # Support both string (new) and Specification object (old, deprecated)
        if isinstance(self.specification, str):
            spec = _get_nested_value(ctx, self.specification)
        else:
            # Backward compatibility: direct Specification object
            spec = self.specification

        result = repository.find_one(spec)
        _set_nested(ctx, self.ctx_var, result)
        return ctx


class FindEntitiesAction(Action):
    """Find multiple entities from a repository and store them in context.

    The specification parameter supports both:
    - Specification object (backward compatible, will be deprecated)
    - String context variable name (new pattern, recommended)
    - None (finds all entities)

    Supports dot notation for both the specification and entities storage fields.

    Example:
        # Find all entities (no filter)
        FindEntitiesAction(repository_name="user_repository", ctx_var="users")

        # New pattern - using default "specification" variable
        Process([
            CreateSpecificationAction(
                specification_factory=lambda ctx: EqualsSpecification("status", "active")
            ),
            FindEntitiesAction(repository_name="user_repository", specification="specification", ctx_var="users")
        ])

        # New pattern - using custom specification variable
        Process([
            CreateSpecificationAction(
                specification_factory=lambda ctx: GreaterThanSpecification("age", 18),
                ctx_var="age_filter"
            ),
            FindEntitiesAction(
                repository_name="user_repository",
                specification="age_filter",
                ctx_var="users"
            )
        ])

        # Old pattern (still works, but deprecated)
        FindEntitiesAction(
            repository_name="user_repository",
            specification=EqualsSpecification("status", "active"),
            ctx_var="users"
        )
    """

    def __init__(
        self,
        *,
        repository_name: str,
        specification=None,
        ctx_var: str = "entities",
    ):
        """
        Args:
            repository_name: Name of repository in ApplicationContext
            specification: Either a Specification object (deprecated), context variable name (str),
                         or None (finds all). Default: None
            ctx_var: Context variable name to store entities list (supports dot notation, default: "entities")

        Note: If specification is None, finds all entities (no filter).
        """
        self.repository_name = repository_name
        self.specification = specification
        self.ctx_var = ctx_var

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        repository = getattr(ctx.fractal.context, self.repository_name)

        # Support both string (new), Specification object (old), and None
        if self.specification is None:
            spec = None
        elif isinstance(self.specification, str):
            spec = _get_nested_value(ctx, self.specification)
        else:
            # Backward compatibility: direct Specification object
            spec = self.specification

        result = repository.find(spec)
        _set_nested(ctx, self.ctx_var, result)
        return ctx


class DeleteEntityAction(Action):
    """Delete a single entity from a repository using a specification.

    The specification parameter supports both:
    - Specification object (backward compatible, will be deprecated)
    - String context variable name (new pattern, recommended)

    Supports dot notation for the specification field.

    Example:
        # New pattern - using default "specification" variable
        Process([
            CreateSpecificationAction(
                specification_factory=lambda ctx: EqualsSpecification("id", ctx["user_id"])
            ),
            DeleteEntityAction(repository_name="user_repository")
        ])

        # New pattern - using custom specification variable
        Process([
            CreateSpecificationAction(
                specification_factory=lambda ctx: EqualsSpecification("id", 1),
                ctx_var="delete_spec"
            ),
            DeleteEntityAction(
                repository_name="user_repository",
                specification="delete_spec"
            )
        ])

        # Old pattern (still works, but deprecated)
        DeleteEntityAction(
            repository_name="user_repository",
            specification=EqualsSpecification("id", 1)
        )
    """

    def __init__(self, *, repository_name: str, specification="specification"):
        """
        Args:
            repository_name: Name of repository in ApplicationContext
            specification: Either a Specification object (deprecated) or context variable name (str)
                         (default: "specification")
        """
        self.repository_name = repository_name
        self.specification = specification

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        repository = getattr(ctx.fractal.context, self.repository_name)

        # Support both string (new) and Specification object (old, deprecated)
        if isinstance(self.specification, str):
            spec = _get_nested_value(ctx, self.specification)
        else:
            # Backward compatibility: direct Specification object
            spec = self.specification

        repository.remove_one(spec)
        return ctx


class CommandAction(Action):
    """Execute a command through the command bus.

    Supports dot notation for the result storage field.

    Example:
        # Store result in default field
        CommandAction(lambda ctx: CreateUserCommand(name=ctx.user_name))

        # Store result in nested field
        CommandAction(
            lambda ctx: CreateUserCommand(name=ctx.user_name),
            ctx_var="command.result"
        )
    """

    def __init__(self, command_factory: Callable, ctx_var: str = "result"):
        """
        Args:
            command_factory: Callable that takes ProcessContext and returns Command.
                           Can access ctx.fractal.context for ApplicationContext.
            ctx_var: Context variable name to store command result (supports dot notation, default: "result")
        """
        self.command_factory = command_factory
        self.ctx_var = ctx_var

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        command = self.command_factory(ctx)
        result = ctx.fractal.context.command_bus.handle(command)
        _set_nested(ctx, self.ctx_var, result)
        return ctx


class QueryAction(Action):
    """Execute a query/function and store result in context.

    Supports dot notation for the result storage field.

    Example:
        # Store result in simple field
        QueryAction(lambda ctx: fetch_users(), "users")

        # Store result in nested field
        QueryAction(lambda ctx: fetch_users(), "data.users")
    """

    def __init__(self, query_func: Callable, ctx_var: str = "result"):
        """
        Args:
            query_func: Callable that takes ProcessContext and returns result
            ctx_var: Context variable name to store result (supports dot notation, default: "result")
        """
        self.query_func = query_func
        self.ctx_var = ctx_var

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        result = self.query_func(ctx)
        _set_nested(ctx, self.ctx_var, result)
        return ctx


# Async action variants - requires AsyncAction import
try:
    from fractal.core.process.action import AsyncAction

    class AsyncCommandAction(AsyncAction):
        """Execute a command asynchronously through the command bus.

        Requires command bus to have handle_async method.
        Supports dot notation for the result storage field.

        Example:
            # Store result in default field
            AsyncCommandAction(lambda ctx: CreateHouseCommand(
                name=ctx.house_name,
                address=ctx.house_address
            ))

            # Store result in nested field
            AsyncCommandAction(
                lambda ctx: CreateHouseCommand(name=ctx.house_name),
                ctx_var="command.result"
            )
        """

        def __init__(self, command_factory: Callable, ctx_var: str = "result"):
            """
            Args:
                command_factory: Callable that takes ProcessContext and returns Command
                ctx_var: Context variable name to store command result (supports dot notation, default: "result")
            """
            self.command_factory = command_factory
            self.ctx_var = ctx_var

        async def execute_async(self, ctx: ProcessContext) -> ProcessContext:
            command = self.command_factory(ctx)
            result = await ctx.fractal.context.command_bus.handle_async(command)
            _set_nested(ctx, self.ctx_var, result)
            return ctx

    class AsyncQueryAction(AsyncAction):
        """Execute an async query/function and store result in context.

        Supports dot notation for the result storage field.

        Example:
            # Store result in simple field
            AsyncQueryAction(
                lambda ctx: await_fetch_houses_async(ctx.filter_status),
                "houses"
            )

            # Store result in nested field
            AsyncQueryAction(
                lambda ctx: await_fetch_users_async(),
                "data.users"
            )
        """

        def __init__(self, query_func: Callable, ctx_var: str = "result"):
            """
            Args:
                query_func: Async callable that takes ProcessContext and returns result
                ctx_var: Context variable name to store result (supports dot notation, default: "result")
            """
            self.query_func = query_func
            self.ctx_var = ctx_var

        async def execute_async(self, ctx: ProcessContext) -> ProcessContext:
            result = await self.query_func(ctx)
            _set_nested(ctx, self.ctx_var, result)
            return ctx

except ImportError:
    # AsyncAction not available in older versions
    pass
