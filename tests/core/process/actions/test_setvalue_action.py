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

    action = SetValueAction(target="user.name", source="new_name")
    result = action.execute(ctx)

    assert result["user"].name == "Bob"
    assert result["user"].email == "alice@example.com"


def test_setvalue_nested_field():
    """Test setting a nested field."""
    company = Company(name="TechCorp", address=Address(city="New York", country="USA"))
    ctx = ProcessContext({"company": company, "new_city": "San Francisco"})

    action = SetValueAction(target="company.address.city", source="new_city")
    result = action.execute(ctx)

    assert result["company"].address.city == "San Francisco"
    assert result["company"].address.country == "USA"


def test_setvalue_from_nested_source():
    """Test reading from a nested source field."""
    user = User("Alice", "alice@example.com", 30)
    company = Company(name="TechCorp", address=Address(city="New York", country="USA"))
    ctx = ProcessContext({"user": user, "company": company})

    action = SetValueAction(target="user.email", source="company.address.city")
    result = action.execute(ctx)

    # Set user.email to the value of company.address.city
    assert result["user"].email == "New York"


def test_setvalue_context_variable_to_context_variable():
    """Test setting one context variable to another."""
    ctx = ProcessContext({"name": "Alice", "backup_name": "Bob"})

    action = SetValueAction(target="name", source="backup_name")
    result = action.execute(ctx)

    assert result["name"] == "Bob"
    assert result["backup_name"] == "Bob"


def test_setvalue_dict_field():
    """Test setting a field in a dict."""
    ctx = ProcessContext(
        {"config": {"database": "postgres", "port": 5432}, "new_db": "mysql"}
    )

    action = SetValueAction(target="config.database", source="new_db")
    result = action.execute(ctx)

    assert result["config"]["database"] == "mysql"
    assert result["config"]["port"] == 5432


def test_setvalue_missing_source_raises():
    """Test that missing source field raises KeyError."""
    ctx = ProcessContext({"user": User("Alice", "alice@example.com", 30)})

    action = SetValueAction(target="user.name", source="missing_field")

    with pytest.raises(KeyError, match="missing_field"):
        action.execute(ctx)


def test_setvalue_missing_target_path_raises():
    """Test that invalid target path raises KeyError."""
    ctx = ProcessContext({"name": "Alice", "missing": None})

    action = SetValueAction(target="missing.field", source="name")

    with pytest.raises(KeyError, match="missing"):
        action.execute(ctx)


def test_setvalue_none_in_path_raises():
    """Test that None in path raises KeyError."""
    ctx = ProcessContext({"user": None, "name": "Alice"})

    action = SetValueAction(target="user.name", source="name")

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
            SetValueAction(target="user.name", source="new_name"),
            SetValueAction(target="user.email", source="new_email"),
            SetValueAction(target="user.age", source="new_age"),
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

    action = SetValueAction(target="person.last_name", source="surname")
    result = action.execute(ctx)

    assert result["person"].last_name == "Jones"
    assert result["person"].first_name == "Alice"


def test_setvalue_copy_between_objects():
    """Test copying value from one object to another."""
    user = User("Alice", "alice@example.com", 30)
    company = Company(name="TechCorp", address=Address(city="New York", country="USA"))
    ctx = ProcessContext({"user": user, "company": company})

    action = SetValueAction(target="user.name", source="company.name")
    result = action.execute(ctx)

    assert result["user"].name == "TechCorp"
