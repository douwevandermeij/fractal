"""Tests for SetValueAction (field value setter)."""

from dataclasses import dataclass

import pytest

from fractal.core.process.actions import SetValueAction
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


def test_setvalue_simple_field():
    """Test setting a simple field from context variable."""
    ctx = ProcessContext(
        {"user": User("Alice", "alice@example.com", 30), "new_name": "Bob"}
    )

    action = SetValueAction(target="user.name", ctx_var="new_name")
    result = action.execute(ctx)

    assert result["user"].name == "Bob"
    assert result["user"].email == "alice@example.com"


def test_setvalue_nested_field():
    """Test setting a nested field."""
    company = Company(name="TechCorp", address=Address(city="New York", country="USA"))
    ctx = ProcessContext({"company": company, "new_city": "San Francisco"})

    action = SetValueAction(target="company.address.city", ctx_var="new_city")
    result = action.execute(ctx)

    assert result["company"].address.city == "San Francisco"
    assert result["company"].address.country == "USA"


def test_setvalue_from_nested_source():
    """Test reading from a nested source field."""
    user = User("Alice", "alice@example.com", 30)
    company = Company(name="TechCorp", address=Address(city="New York", country="USA"))
    ctx = ProcessContext({"user": user, "company": company})

    action = SetValueAction(target="user.email", ctx_var="company.address.city")
    result = action.execute(ctx)

    # Set user.email to the value of company.address.city
    assert result["user"].email == "New York"


def test_setvalue_context_variable_to_context_variable():
    """Test setting one context variable to another."""
    ctx = ProcessContext({"name": "Alice", "backup_name": "Bob"})

    action = SetValueAction(target="name", ctx_var="backup_name")
    result = action.execute(ctx)

    assert result["name"] == "Bob"
    assert result["backup_name"] == "Bob"


def test_setvalue_dict_field():
    """Test setting a field in a dict."""
    ctx = ProcessContext(
        {"config": {"database": "postgres", "port": 5432}, "new_db": "mysql"}
    )

    action = SetValueAction(target="config.database", ctx_var="new_db")
    result = action.execute(ctx)

    assert result["config"]["database"] == "mysql"
    assert result["config"]["port"] == 5432


def test_setvalue_missing_source_raises():
    """Test that missing source field raises KeyError."""
    ctx = ProcessContext({"user": User("Alice", "alice@example.com", 30)})

    action = SetValueAction(target="user.name", ctx_var="missing_field")

    with pytest.raises(KeyError, match="missing_field"):
        action.execute(ctx)


def test_setvalue_missing_target_path_raises():
    """Test that invalid target path raises KeyError."""
    ctx = ProcessContext({"name": "Alice", "missing": None})

    action = SetValueAction(target="missing.field", ctx_var="name")

    with pytest.raises(KeyError, match="missing"):
        action.execute(ctx)


def test_setvalue_none_in_path_raises():
    """Test that None in path raises KeyError."""
    ctx = ProcessContext({"user": None, "name": "Alice"})

    action = SetValueAction(target="user.name", ctx_var="name")

    with pytest.raises(KeyError, match="user"):
        action.execute(ctx)


def test_setvalue_chain_multiple_actions():
    """Test chaining multiple SetValueAction calls."""
    from fractal.core.process.process import Process

    user = User("Alice", "alice@example.com", 30)
    ctx = ProcessContext(
        {"user": user, "new_name": "Bob", "new_email": "bob@example.com", "new_age": 35}
    )

    process = Process(
        [
            SetValueAction(target="user.name", ctx_var="new_name"),
            SetValueAction(target="user.email", ctx_var="new_email"),
            SetValueAction(target="user.age", ctx_var="new_age"),
        ]
    )

    result = process.run(ctx)

    assert result["user"].name == "Bob"
    assert result["user"].email == "bob@example.com"
    assert result["user"].age == 35


def test_setvalue_with_dataclass():
    """Test setting fields on dataclass objects."""

    @dataclass
    class Person:
        first_name: str
        last_name: str

    person = Person(first_name="Alice", last_name="Smith")
    ctx = ProcessContext({"person": person, "surname": "Jones"})

    action = SetValueAction(target="person.last_name", ctx_var="surname")
    result = action.execute(ctx)

    assert result["person"].last_name == "Jones"
    assert result["person"].first_name == "Alice"


def test_setvalue_copy_between_objects():
    """Test copying value from one object to another."""
    user = User("Alice", "alice@example.com", 30)
    company = Company(name="TechCorp", address=Address(city="New York", country="USA"))
    ctx = ProcessContext({"user": user, "company": company})

    action = SetValueAction(target="user.name", ctx_var="company.name")
    result = action.execute(ctx)

    assert result["user"].name == "TechCorp"


# Tests for direct value setting


def test_setvalue_direct_value_string():
    """Test setting a field to a direct string value."""
    user = User("Alice", "alice@example.com", 30)
    ctx = ProcessContext({"user": user})

    action = SetValueAction(target="user.name", value="Bob")
    result = action.execute(ctx)

    assert result["user"].name == "Bob"
    assert result["user"].email == "alice@example.com"


def test_setvalue_direct_value_int():
    """Test setting a field to a direct integer value."""
    user = User("Alice", "alice@example.com", 30)
    ctx = ProcessContext({"user": user})

    action = SetValueAction(target="user.age", value=35)
    result = action.execute(ctx)

    assert result["user"].age == 35


def test_setvalue_direct_value_bool():
    """Test setting a field to a direct boolean value."""
    ctx = ProcessContext({"config": {"enabled": False, "debug": True}})

    action = SetValueAction(target="config.enabled", value=True)
    result = action.execute(ctx)

    assert result["config"]["enabled"] is True


def test_setvalue_direct_value_list():
    """Test setting a field to a direct list value."""
    ctx = ProcessContext({"user": {"name": "Alice", "roles": []}})

    action = SetValueAction(target="user.roles", value=["admin", "user"])
    result = action.execute(ctx)

    assert result["user"]["roles"] == ["admin", "user"]


def test_setvalue_direct_value_dict():
    """Test setting a field to a direct dict value."""
    ctx = ProcessContext({"config": {}})

    action = SetValueAction(
        target="config", value={"database": "postgres", "port": 5432}
    )
    result = action.execute(ctx)

    assert result["config"] == {"database": "postgres", "port": 5432}


def test_setvalue_direct_value_none():
    """Test setting a field to None."""
    user = User("Alice", "alice@example.com", 30)
    ctx = ProcessContext({"user": user})

    action = SetValueAction(target="user.email", value=None)
    result = action.execute(ctx)

    assert result["user"].email is None


def test_setvalue_direct_value_enum():
    """Test setting a field to an enum value."""
    from enum import Enum

    class Status(Enum):
        ACTIVE = "active"
        CANCELED = "canceled"

    @dataclass
    class Order:
        id: int
        status: Status

    order = Order(id=1, status=Status.ACTIVE)
    ctx = ProcessContext({"order": order})

    action = SetValueAction(target="order.status", value=Status.CANCELED)
    result = action.execute(ctx)

    assert result["order"].status == Status.CANCELED


def test_setvalue_direct_value_nested_target():
    """Test setting a nested field to a direct value."""
    company = Company(name="TechCorp", address=Address(city="New York", country="USA"))
    ctx = ProcessContext({"company": company})

    action = SetValueAction(target="company.address.city", value="San Francisco")
    result = action.execute(ctx)

    assert result["company"].address.city == "San Francisco"
    assert result["company"].address.country == "USA"


def test_setvalue_direct_value_context_variable():
    """Test setting a top-level context variable to a direct value."""
    ctx = ProcessContext({"count": 0})

    action = SetValueAction(target="count", value=42)
    result = action.execute(ctx)

    assert result["count"] == 42


def test_setvalue_requires_ctx_var_or_value():
    """Test that exactly one of ctx_var or value must be provided."""
    # Neither provided
    with pytest.raises(
        ValueError, match="Exactly one of 'ctx_var' or 'value' must be provided"
    ):
        SetValueAction(target="user.name")

    # Both provided
    with pytest.raises(
        ValueError, match="Exactly one of 'ctx_var' or 'value' must be provided"
    ):
        SetValueAction(target="user.name", ctx_var="new_name", value="Bob")


def test_setvalue_chain_ctx_var_and_direct_value():
    """Test chaining SetValueAction with both ctx_var and direct values."""
    from fractal.core.process.process import Process

    user = User("Alice", "alice@example.com", 30)
    ctx = ProcessContext({"user": user, "new_name": "Bob"})

    process = Process(
        [
            SetValueAction(target="user.name", ctx_var="new_name"),  # From context
            SetValueAction(target="user.age", value=35),  # Direct value
            SetValueAction(
                target="user.email", value="bob@example.com"
            ),  # Direct value
        ]
    )

    result = process.run(ctx)

    assert result["user"].name == "Bob"
    assert result["user"].email == "bob@example.com"
    assert result["user"].age == 35
