"""Tests for SetContextVariableAction with callable values."""

from fractal.core.process.actions import SetContextVariableAction
from fractal.core.process.process import Process
from fractal.core.process.process_context import ProcessContext


def test_setcontext_with_simple_lambda():
    """Test SetContextVariableAction with simple lambda function."""
    action = SetContextVariableAction(doubled=lambda ctx: ctx["value"] * 2)

    ctx = ProcessContext({"value": 10})
    result = action.execute(ctx)

    assert result["doubled"] == 20
    assert result["value"] == 10  # Original value unchanged


def test_setcontext_with_conditional_lambda():
    """Test SetContextVariableAction with conditional lambda."""
    action = SetContextVariableAction(
        status=lambda ctx: "active" if ctx["enabled"] else "inactive"
    )

    # Test when enabled is True
    ctx1 = ProcessContext({"enabled": True})
    result1 = action.execute(ctx1)
    assert result1["status"] == "active"

    # Test when enabled is False
    ctx2 = ProcessContext({"enabled": False})
    result2 = action.execute(ctx2)
    assert result2["status"] == "inactive"


def test_setcontext_with_multiple_lambdas():
    """Test SetContextVariableAction with multiple lambda functions."""
    action = SetContextVariableAction(
        total=lambda ctx: ctx["price"] + ctx["tax"],
        discount_price=lambda ctx: ctx["price"] * 0.9,
        message=lambda ctx: f"Price: {ctx['price']}, Tax: {ctx['tax']}",
    )

    ctx = ProcessContext({"price": 100, "tax": 10})
    result = action.execute(ctx)

    assert result["total"] == 110
    assert result["discount_price"] == 90.0
    assert result["message"] == "Price: 100, Tax: 10"


def test_setcontext_mixed_static_and_callable():
    """Test SetContextVariableAction with both static and callable values."""
    action = SetContextVariableAction(
        static_value="hello",
        computed_value=lambda ctx: ctx["base"] * 3,
        another_static=42,
    )

    ctx = ProcessContext({"base": 5})
    result = action.execute(ctx)

    assert result["static_value"] == "hello"
    assert result["computed_value"] == 15
    assert result["another_static"] == 42


def test_setcontext_lambda_accessing_nested_context():
    """Test lambda function accessing nested context values."""
    action = SetContextVariableAction(
        full_address=lambda ctx: f"{ctx['user']['address']['street']}, {ctx['user']['address']['city']}"
    )

    ctx = ProcessContext(
        {"user": {"address": {"street": "123 Main St", "city": "Springfield"}}}
    )
    result = action.execute(ctx)

    assert result["full_address"] == "123 Main St, Springfield"


def test_setcontext_lambda_with_dot_notation_target():
    """Test lambda function with dot notation for target key."""
    action = SetContextVariableAction(
        **{"user.full_name": lambda ctx: f"{ctx['first_name']} {ctx['last_name']}"}
    )

    ctx = ProcessContext({"first_name": "John", "last_name": "Doe"})
    result = action.execute(ctx)

    assert result["user"]["full_name"] == "John Doe"


def test_setcontext_lambda_with_list_operations():
    """Test lambda function performing list operations."""
    action = SetContextVariableAction(
        item_count=lambda ctx: len(ctx["items"]),
        first_item=lambda ctx: ctx["items"][0] if ctx["items"] else None,
        total_price=lambda ctx: sum(item["price"] for item in ctx["items"]),
    )

    ctx = ProcessContext(
        {"items": [{"name": "apple", "price": 1.5}, {"name": "banana", "price": 0.8}]}
    )
    result = action.execute(ctx)

    assert result["item_count"] == 2
    assert result["first_item"] == {"name": "apple", "price": 1.5}
    assert result["total_price"] == 2.3


def test_setcontext_lambda_with_dict_operations():
    """Test lambda function performing dict operations."""
    action = SetContextVariableAction(
        key_count=lambda ctx: len(ctx["data"].keys()),
        has_name=lambda ctx: "name" in ctx["data"],
        all_values=lambda ctx: list(ctx["data"].values()),
    )

    ctx = ProcessContext({"data": {"name": "Alice", "age": 30, "city": "NYC"}})
    result = action.execute(ctx)

    assert result["key_count"] == 3
    assert result["has_name"] is True
    assert result["all_values"] == ["Alice", 30, "NYC"]


def test_setcontext_lambda_returning_complex_objects():
    """Test lambda function returning complex objects."""
    action = SetContextVariableAction(
        user_summary=lambda ctx: {
            "id": ctx["user_id"],
            "name": ctx["user_name"],
            "status": "active" if ctx["enabled"] else "inactive",
            "score": ctx["points"] * 10,
        }
    )

    ctx = ProcessContext(
        {"user_id": 123, "user_name": "Alice", "enabled": True, "points": 50}
    )
    result = action.execute(ctx)

    assert result["user_summary"] == {
        "id": 123,
        "name": "Alice",
        "status": "active",
        "score": 500,
    }


def test_setcontext_lambda_with_default_values():
    """Test lambda function with default/fallback values."""
    action = SetContextVariableAction(
        safe_value=lambda ctx: ctx.get("optional_field", "default"),
        computed=lambda ctx: ctx.get("value", 0) * 2,
    )

    # Test with missing keys
    ctx1 = ProcessContext({})
    result1 = action.execute(ctx1)
    assert result1["safe_value"] == "default"
    assert result1["computed"] == 0

    # Test with present keys
    ctx2 = ProcessContext({"optional_field": "custom", "value": 10})
    result2 = action.execute(ctx2)
    assert result2["safe_value"] == "custom"
    assert result2["computed"] == 20


def test_setcontext_in_workflow():
    """Test SetContextVariableAction with lambdas in complete workflow."""
    process = Process(
        [
            # Set initial values
            SetContextVariableAction(base_price=100, tax_rate=0.2),
            # Compute derived values
            SetContextVariableAction(
                tax=lambda ctx: ctx["base_price"] * ctx["tax_rate"],
            ),
            # Compute final total
            SetContextVariableAction(
                total=lambda ctx: ctx["base_price"] + ctx["tax"],
                discount_total=lambda ctx: (ctx["base_price"] + ctx["tax"]) * 0.9,
            ),
        ]
    )

    result = process.run(ProcessContext({}))

    assert result["base_price"] == 100
    assert result["tax_rate"] == 0.2
    assert result["tax"] == 20.0
    assert result["total"] == 120.0
    assert result["discount_total"] == 108.0


def test_setcontext_lambda_chaining():
    """Test chaining multiple SetContextVariableAction with lambdas."""
    process = Process(
        [
            SetContextVariableAction(x=10),
            SetContextVariableAction(y=lambda ctx: ctx["x"] * 2),
            SetContextVariableAction(z=lambda ctx: ctx["y"] + ctx["x"]),
            SetContextVariableAction(result=lambda ctx: ctx["z"] ** 2),
        ]
    )

    result = process.run(ProcessContext({}))

    assert result["x"] == 10
    assert result["y"] == 20
    assert result["z"] == 30
    assert result["result"] == 900


def test_setcontext_lambda_error_handling():
    """Test that lambda exceptions propagate correctly."""
    import pytest

    action = SetContextVariableAction(value=lambda ctx: ctx["missing_key"])

    ctx = ProcessContext({"other": "data"})

    # Should raise KeyError when lambda tries to access missing key
    with pytest.raises(KeyError):
        action.execute(ctx)


def test_setcontext_callable_function_not_just_lambda():
    """Test that any callable works, not just lambdas."""

    def compute_value(ctx):
        """Regular function that computes a value."""
        return ctx["a"] + ctx["b"] * ctx["c"]

    action = SetContextVariableAction(result=compute_value)

    ctx = ProcessContext({"a": 10, "b": 5, "c": 3})
    result = action.execute(ctx)

    assert result["result"] == 25  # 10 + 5 * 3


def test_setcontext_nested_callable_values():
    """Test SetContextVariableAction with nested structures and callables."""
    action = SetContextVariableAction(
        **{
            "user.full_name": lambda ctx: f"{ctx['first']} {ctx['last']}",
            "user.age": lambda ctx: ctx["birth_year"] and (2024 - ctx["birth_year"]),
            "user.status": "active",  # Static value in nested structure
        }
    )

    ctx = ProcessContext({"first": "Jane", "last": "Doe", "birth_year": 1990})
    result = action.execute(ctx)

    assert result["user"]["full_name"] == "Jane Doe"
    assert result["user"]["age"] == 34
    assert result["user"]["status"] == "active"


def test_setcontext_lambda_accessing_previous_computed_values():
    """Test lambda accessing values set earlier in the same action."""
    # Note: All lambdas execute against the SAME original context
    # They don't see each other's computed values within the same action
    action = SetContextVariableAction(
        a=lambda ctx: 10,
        b=lambda ctx: 20,
    )

    result = action.execute(ProcessContext({}))
    assert result["a"] == 10
    assert result["b"] == 20

    # To use computed values, you need separate actions
    process = Process(
        [
            SetContextVariableAction(a=lambda ctx: 10),
            SetContextVariableAction(b=lambda ctx: ctx["a"] * 2),  # Can access a
        ]
    )

    result2 = process.run(ProcessContext({}))
    assert result2["a"] == 10
    assert result2["b"] == 20
