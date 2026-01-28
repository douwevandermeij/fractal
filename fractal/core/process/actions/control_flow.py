from typing import Callable, Iterable, List, Optional, Union

from fractal.core.process.action import Action
from fractal.core.process.process import Process
from fractal.core.process.process_context import ProcessContext


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


class IfElseAction(Action):
    """Execute actions conditionally based on a specification.

    The specification parameter supports both:
    - Specification object (backward compatible, will be deprecated)
    - String context variable name (new pattern, recommended)

    Example:
        # New pattern - using default "specification" variable
        Process([
            CreateSpecificationAction(
                spec_factory=lambda ctx: EqualsSpecification("status", "active")
            ),
            IfElseAction(
                actions_true=[...],
                actions_false=[...]
            )
        ])

        # New pattern - using custom specification variable
        Process([
            CreateSpecificationAction(
                spec_factory=lambda ctx: GreaterThanSpecification("count", 10),
                ctx_var="count_check"
            ),
            IfElseAction(
                actions_true=[...],
                actions_false=[...],
                specification="count_check"
            )
        ])

        # Old pattern (still works, but deprecated)
        IfElseAction(
            specification=EqualsSpecification("status", "active"),
            actions_true=[...],
            actions_false=[...]
        )
    """

    def __init__(
        self,
        actions_true: List[Action],
        actions_false: Optional[List[Action]] = None,
        specification="specification",
    ):
        """
        Args:
            actions_true: Actions to execute if specification is satisfied
            actions_false: Actions to execute if specification is not satisfied (optional)
            specification: Either a Specification object (deprecated) or context variable name (str)
                         (default: "specification")
        """
        self.specification = specification
        self.process_true = Process(actions_true)
        self.process_false = Process(actions_false) if actions_false else None

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        # Support both string (new) and Specification object (old, deprecated)
        if isinstance(self.specification, str):
            spec = _get_nested_value(ctx, self.specification)
        else:
            # Backward compatibility: direct Specification object
            spec = self.specification

        if spec.is_satisfied_by(ctx):
            if self.process_true:
                ctx.update(self.process_true.run(ctx))
        elif self.process_false:
            ctx.update(self.process_false.run(ctx))
        return ctx


class WhileAction(Action):
    """Execute actions repeatedly while a specification is satisfied.

    The specification parameter supports both:
    - Specification object (backward compatible, will be deprecated)
    - String context variable name (new pattern, recommended)

    Example:
        # New pattern - using default "specification" variable
        Process([
            SetContextVariableAction(count=0),
            CreateSpecificationAction(
                spec_factory=lambda ctx: LessThanSpecification("count", 5)
            ),
            WhileAction(
                actions=[
                    IncreaseValueAction(ctx_var="count", value=1),
                    PrintValueAction(ctx_var="count")
                ]
            )
        ])

        # New pattern - using custom specification variable
        Process([
            CreateSpecificationAction(
                spec_factory=lambda ctx: GreaterThanSpecification("items_left", 0),
                ctx_var="has_items"
            ),
            WhileAction(
                actions=[...],
                specification="has_items"
            )
        ])

        # Old pattern (still works, but deprecated)
        WhileAction(
            specification=LessThanSpecification("count", 5),
            actions=[...]
        )
    """

    def __init__(self, actions: List[Action], specification="specification"):
        """
        Args:
            actions: Actions to execute while specification is satisfied
            specification: Either a Specification object (deprecated) or context variable name (str)
                         (default: "specification")
        """
        self.specification = specification
        self.process = Process(actions)

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        # Support both string (new) and Specification object (old, deprecated)
        if isinstance(self.specification, str):
            spec = _get_nested_value(ctx, self.specification)
        else:
            # Backward compatibility: direct Specification object
            spec = self.specification

        while spec.is_satisfied_by(ctx):
            ctx.update(self.process.run(ctx))
        return ctx


class ForEachAction(Action):
    """Execute actions for each item in an iterable.

    Supports both static iterables and dynamic lookup from context.

    Examples:
        # Static iterable
        ForEachAction([1, 2, 3], [PrintValueAction(ctx_var="item")])

        # Dynamic lookup from context field
        ForEachAction("entities", [ProcessEntityAction()])

        # Dynamic callable
        ForEachAction(
            lambda ctx: ctx.fractal.context.user_repository.find_all(),
            [NotifyUserAction()]
        )
    """

    def __init__(
        self,
        iterable: Union[Iterable, str, Callable[[ProcessContext], Iterable]],
        actions: List[Action],
        ctx_var: str = "item",
    ):
        """Initialize ForEachAction.

        Args:
            iterable: Can be:
                - Static iterable (list, tuple, etc.)
                - String field name to lookup in context
                - Callable that takes context and returns iterable
            actions: Actions to execute for each item
            ctx_var: Context variable name to store current item (default: "item")
        """
        self.iterable = iterable
        self.process = Process(actions)
        self.ctx_var = ctx_var

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        # Resolve iterable based on type
        if isinstance(self.iterable, str):
            # Lookup from context field
            items = ctx[self.iterable]
        elif callable(self.iterable):
            # Call function to get iterable
            items = self.iterable(ctx)
        else:
            # Use as-is (static iterable)
            items = self.iterable

        # Execute actions for each item
        for item in items:
            ctx[self.ctx_var] = item
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


class SubProcessAction(Action):
    """Execute a sub-process as an action.

    Allows composing processes by calling one process from within another.
    The sub-process shares the same context as the parent.

    Example:
        # Define reusable sub-processes
        validate_user = Process([
            QueryAction(lambda ctx: ctx.fractal.context.user_repository.get(ctx["user_id"]), "user"),
            IfElseAction(
                specification=has_field("user"),
                actions_true=[SetContextVariableAction(user_valid=True)],
                actions_false=[SetContextVariableAction(user_valid=False)]
            )
        ])

        # Use in parent process
        Process([
            SetContextVariableAction(user_id="123"),
            SubProcessAction(validate_user),
            IfElseAction(
                specification=field_equals("user_valid", True),
                actions_true=[...]
            )
        ])
    """

    def __init__(self, process: "Process"):
        """Initialize SubProcessAction.

        Args:
            process: Process to execute as a sub-process
        """
        self.process = process

    def execute(self, ctx: ProcessContext) -> ProcessContext:
        """Execute the sub-process.

        Args:
            ctx: ProcessContext from parent process

        Returns:
            Updated ProcessContext after sub-process execution
        """
        return self.process.run(ctx)


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
