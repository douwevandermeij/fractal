from typing import Any, Callable

from fractal_specifications.generic.specification import Specification


class CallableSpecification(Specification):
    """Specification that wraps a callable/lambda for is_satisfied_by check.

    This allows creating specifications from simple lambda functions or callables.
    """

    def __init__(self, predicate: Callable[[Any], bool]):
        """
        Args:
            predicate: Callable that takes an object and returns a boolean
        """
        self.predicate = predicate

    def is_satisfied_by(self, obj: Any) -> bool:
        """Check if object satisfies the predicate.

        Args:
            obj: Object to check (typically a ProcessContext)

        Returns:
            True if predicate returns True for object
        """
        return self.predicate(obj)

    def to_collection(self):
        """Convert to collection format.

        Returns None for callable specifications as they can't be
        meaningfully converted to collection query format.
        """
        return None


def _get_nested(ctx, field: str):
    """Get nested field value using dot notation (e.g., 'house.status').

    Args:
        ctx: ProcessContext object
        field: Field name, can use dot notation for nested access

    Returns:
        Field value or None if not found
    """
    value = ctx
    for part in field.split("."):
        if hasattr(value, "get"):
            value = value.get(part)
        elif hasattr(value, part):
            value = getattr(value, part)
        else:
            return None
        if value is None:
            return None
    return value


def has_field(field: str) -> Specification:
    """Check if a field exists and is not None in ProcessContext.

    Supports nested fields with dot notation.

    Example:
        has_field('house')
        has_field('house.address')

    Args:
        field: Field name (supports dot notation for nested access)

    Returns:
        Specification that checks field existence
    """
    return CallableSpecification(lambda s: _get_nested(s, field) is not None)


def field_equals(field: str, value: Any) -> Specification:
    """Check if a field equals a specific value.

    Supports nested fields with dot notation.

    Example:
        field_equals('house.status', 'active')
        field_equals('count', 5)

    Args:
        field: Field name (supports dot notation for nested access)
        value: Expected value

    Returns:
        Specification that checks field equality
    """
    return CallableSpecification(lambda s: _get_nested(s, field) == value)


def field_in(field: str, values: list) -> Specification:
    """Check if a field value is in a list of values.

    Example:
        field_in('house.status', ['active', 'pending'])

    Args:
        field: Field name (supports dot notation for nested access)
        values: List of acceptable values

    Returns:
        Specification that checks field membership
    """
    return CallableSpecification(lambda s: _get_nested(s, field) in values)


def field_gt(field: str, value: Any) -> Specification:
    """Check if a field is greater than a value.

    Example:
        field_gt('count', 10)
        field_gt('house.price', 100000)

    Args:
        field: Field name (supports dot notation for nested access)
        value: Value to compare against

    Returns:
        Specification that checks field > value
    """

    def check(s):
        field_value = _get_nested(s, field)
        return field_value is not None and field_value > value

    return CallableSpecification(check)


def field_lt(field: str, value: Any) -> Specification:
    """Check if a field is less than a value.

    Example:
        field_lt('count', 10)
        field_lt('house.price', 100000)

    Args:
        field: Field name (supports dot notation for nested access)
        value: Value to compare against

    Returns:
        Specification that checks field < value
    """

    def check(s):
        field_value = _get_nested(s, field)
        return field_value is not None and field_value < value

    return CallableSpecification(check)


def field_gte(field: str, value: Any) -> Specification:
    """Check if a field is greater than or equal to a value.

    Example:
        field_gte('count', 10)

    Args:
        field: Field name (supports dot notation for nested access)
        value: Value to compare against

    Returns:
        Specification that checks field >= value
    """

    def check(s):
        field_value = _get_nested(s, field)
        return field_value is not None and field_value >= value

    return CallableSpecification(check)


def field_lte(field: str, value: Any) -> Specification:
    """Check if a field is less than or equal to a value.

    Example:
        field_lte('count', 10)

    Args:
        field: Field name (supports dot notation for nested access)
        value: Value to compare against

    Returns:
        Specification that checks field <= value
    """

    def check(s):
        field_value = _get_nested(s, field)
        return field_value is not None and field_value <= value

    return CallableSpecification(check)


def field_contains(field: str, substring: str) -> Specification:
    """Check if a field contains a substring.

    Example:
        field_contains('house.address', 'Main St')
        field_contains('status', 'active')

    Args:
        field: Field name (supports dot notation for nested access)
        substring: Substring to search for

    Returns:
        Specification that checks field contains substring
    """
    return CallableSpecification(
        lambda s: substring in str(_get_nested(s, field) or "")
    )


def on_field(field: str, specification: Specification) -> Specification:
    """Apply an entity specification to a field in the ProcessContext.

    This separates field selection from specification logic, allowing you to
    reuse entity specifications from your domain with ProcessContext.

    Example:
        # Define entity specification (reusable across your domain)
        from fractal_specifications.generic.specification import field_equals
        house_is_active = field_equals("status", "active")

        # Apply to context field
        IfElseAction(
            specification=on_field("house", house_is_active),
            actions_true=[...]
        )

        # Compose with other context checks
        on_field("house", house_is_active) & has_field("user")

    Args:
        field: Field name in ProcessContext (supports dot notation)
        specification: Entity specification to apply to the field value

    Returns:
        Specification that extracts field from context and applies entity spec
    """
    return CallableSpecification(
        lambda ctx: (
            (entity := _get_nested(ctx, field)) is not None
            and specification.is_satisfied_by(entity)
        )
    )
