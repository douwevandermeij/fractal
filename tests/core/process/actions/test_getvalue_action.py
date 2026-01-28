"""Tests for GetValueAction (field value extractor)."""

from dataclasses import dataclass

import pytest

from fractal.core.process.actions import GetValueAction
from fractal.core.process.process_context import ProcessContext


@dataclass
class User:
    """Test domain object."""

    name: str
    email: str
    age: int


@dataclass
class Address:
    """Test nested domain object."""

    city: str
    country: str


@dataclass
class Company:
    """Test domain object with nested structure."""

    name: str
    address: Address


def test_getvalue_simple_field():
    """Test extracting a simple field into context."""
    user = User("Alice", "alice@example.com", 30)
    ctx = ProcessContext({"user": user})

    action = GetValueAction(ctx_var="user_email", source="user.email")
    result = action.execute(ctx)

    assert result["user_email"] == "alice@example.com"
    assert result["user"].email == "alice@example.com"  # Original unchanged


def test_getvalue_nested_field():
    """Test extracting a nested field."""
    company = Company(name="TechCorp", address=Address(city="New York", country="USA"))
    ctx = ProcessContext({"company": company})

    action = GetValueAction(ctx_var="city", source="company.address.city")
    result = action.execute(ctx)

    assert result["city"] == "New York"
    assert result["company"].address.city == "New York"  # Original unchanged


def test_getvalue_multiple_extractions():
    """Test chaining multiple GetValueAction calls."""
    from fractal.core.process.process import Process

    user = User("Alice", "alice@example.com", 30)
    ctx = ProcessContext({"user": user})

    process = Process(
        [
            GetValueAction(ctx_var="user_name", source="user.name"),
            GetValueAction(ctx_var="user_email", source="user.email"),
            GetValueAction(ctx_var="user_age", source="user.age"),
        ]
    )

    result = process.run(ctx)

    assert result["user_name"] == "Alice"
    assert result["user_email"] == "alice@example.com"
    assert result["user_age"] == 30


def test_getvalue_from_dict():
    """Test extracting from dict fields."""
    ctx = ProcessContext({"config": {"database": "postgres", "port": 5432}})

    action = GetValueAction(ctx_var="db_name", source="config.database")
    result = action.execute(ctx)

    assert result["db_name"] == "postgres"
    assert result["config"]["database"] == "postgres"  # Original unchanged


def test_getvalue_missing_source_raises():
    """Test that missing source field raises KeyError."""
    ctx = ProcessContext({"user": User("Alice", "alice@example.com", 30)})

    action = GetValueAction(ctx_var="phone", source="user.phone")

    with pytest.raises(KeyError, match="user.phone"):
        action.execute(ctx)


def test_getvalue_none_in_path_raises():
    """Test that None in path raises KeyError."""
    ctx = ProcessContext({"user": None})

    action = GetValueAction(ctx_var="user_name", source="user.name")

    with pytest.raises(KeyError, match="user"):
        action.execute(ctx)


def test_getvalue_with_setvalue_round_trip():
    """Test GetValueAction followed by SetValueAction creates a copy."""
    from fractal.core.process.actions import SetValueAction
    from fractal.core.process.process import Process

    user1 = User("Alice", "alice@example.com", 30)
    user2 = User("Bob", "bob@example.com", 25)
    ctx = ProcessContext({"user1": user1, "user2": user2})

    # Extract user1's name and assign it to user2's name
    process = Process(
        [
            GetValueAction(ctx_var="temp_name", source="user1.name"),
            SetValueAction(target="user2.name", ctx_var="temp_name"),
        ]
    )

    result = process.run(ctx)

    assert result["user1"].name == "Alice"
    assert result["user2"].name == "Alice"  # Copied from user1
    assert result["temp_name"] == "Alice"


def test_getvalue_deeply_nested():
    """Test extracting deeply nested values."""

    @dataclass
    class Level3:
        value: str

    @dataclass
    class Level2:
        level3: Level3

    @dataclass
    class Level1:
        level2: Level2

    nested = Level1(level2=Level2(level3=Level3(value="deep")))
    ctx = ProcessContext({"nested": nested})

    action = GetValueAction(ctx_var="deep_value", source="nested.level2.level3.value")
    result = action.execute(ctx)

    assert result["deep_value"] == "deep"


def test_getvalue_semantic_clarity():
    """Test that GetValueAction makes intent clear vs SetValueAction."""
    from fractal.core.process.actions import SetValueAction

    user = User("Alice", "alice@example.com", 30)
    ctx = ProcessContext({"user": user})

    # GetValueAction: "I'm extracting a value into context"
    get_action = GetValueAction(ctx_var="user_email", source="user.email")
    result1 = get_action.execute(ctx.copy())
    assert result1["user_email"] == "alice@example.com"

    # SetValueAction with simple target: technically the same operation
    # but SetValueAction implies "I'm setting/modifying something"
    set_action = SetValueAction(target="user_email_copy", ctx_var="user.email")
    result2 = set_action.execute(ctx.copy())
    assert result2["user_email_copy"] == "alice@example.com"

    # Both work the same, but GetValueAction expresses intent better


def test_getvalue_context_variable_to_context_variable():
    """Test that GetValueAction can also extract simple context variables."""
    ctx = ProcessContext({"source_var": "value"})

    action = GetValueAction(ctx_var="target_var", source="source_var")
    result = action.execute(ctx)

    assert result["target_var"] == "value"
    assert result["source_var"] == "value"  # Original still there
