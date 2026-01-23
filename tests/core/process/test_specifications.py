"""Tests for process specification builders."""

from dataclasses import dataclass

from fractal.core.process.process_context import ProcessContext
from fractal.core.process.specifications import (
    field_contains,
    field_equals,
    field_gt,
    field_gte,
    field_in,
    field_lt,
    field_lte,
    has_field,
)


@dataclass
class House:
    """Test domain object."""

    status: str
    price: int
    address: str = None


def test_has_field_simple():
    """Test has_field with simple field."""
    spec = has_field("name")

    scope1 = ProcessContext({"name": "John"})
    scope2 = ProcessContext({"other": "value"})
    scope3 = ProcessContext({"name": None})

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is False
    assert spec.is_satisfied_by(scope3) is False


def test_has_field_nested():
    """Test has_field with nested dot notation."""
    house = House(status="active", price=100000, address="123 Main St")
    spec = has_field("house.address")

    scope1 = ProcessContext({"house": house})
    scope2 = ProcessContext({"house": House(status="active", price=100000)})
    scope3 = ProcessContext({"other": "value"})

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is False
    assert spec.is_satisfied_by(scope3) is False


def test_field_equals_simple():
    """Test field_equals with simple field."""
    spec = field_equals("status", "active")

    scope1 = ProcessContext({"status": "active"})
    scope2 = ProcessContext({"status": "inactive"})
    scope3 = ProcessContext({"other": "active"})

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is False
    assert spec.is_satisfied_by(scope3) is False


def test_field_equals_nested():
    """Test field_equals with nested dot notation."""
    house1 = House(status="active", price=100000)
    house2 = House(status="inactive", price=100000)
    spec = field_equals("house.status", "active")

    scope1 = ProcessContext({"house": house1})
    scope2 = ProcessContext({"house": house2})

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is False


def test_field_in():
    """Test field_in with list of values."""
    spec = field_in("status", ["active", "pending", "processing"])

    scope1 = ProcessContext({"status": "active"})
    scope2 = ProcessContext({"status": "pending"})
    scope3 = ProcessContext({"status": "rejected"})

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is True
    assert spec.is_satisfied_by(scope3) is False


def test_field_in_nested():
    """Test field_in with nested field."""
    house1 = House(status="active", price=100000)
    house2 = House(status="rejected", price=100000)
    spec = field_in("house.status", ["active", "pending"])

    scope1 = ProcessContext({"house": house1})
    scope2 = ProcessContext({"house": house2})

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is False


def test_field_gt():
    """Test field_gt for greater than comparison."""
    spec = field_gt("price", 100000)

    scope1 = ProcessContext({"price": 150000})
    scope2 = ProcessContext({"price": 100000})
    scope3 = ProcessContext({"price": 50000})

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is False
    assert spec.is_satisfied_by(scope3) is False


def test_field_lt():
    """Test field_lt for less than comparison."""
    spec = field_lt("price", 100000)

    scope1 = ProcessContext({"price": 50000})
    scope2 = ProcessContext({"price": 100000})
    scope3 = ProcessContext({"price": 150000})

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is False
    assert spec.is_satisfied_by(scope3) is False


def test_field_gte():
    """Test field_gte for greater than or equal comparison."""
    spec = field_gte("price", 100000)

    scope1 = ProcessContext({"price": 150000})
    scope2 = ProcessContext({"price": 100000})
    scope3 = ProcessContext({"price": 50000})

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is True
    assert spec.is_satisfied_by(scope3) is False


def test_field_lte():
    """Test field_lte for less than or equal comparison."""
    spec = field_lte("price", 100000)

    scope1 = ProcessContext({"price": 50000})
    scope2 = ProcessContext({"price": 100000})
    scope3 = ProcessContext({"price": 150000})

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is True
    assert spec.is_satisfied_by(scope3) is False


def test_field_contains():
    """Test field_contains for substring search."""
    spec = field_contains("address", "Main St")

    scope1 = ProcessContext({"address": "123 Main St"})
    scope2 = ProcessContext({"address": "456 Oak Ave"})
    scope3 = ProcessContext({"address": None})

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is False
    assert spec.is_satisfied_by(scope3) is False


def test_field_contains_nested():
    """Test field_contains with nested field."""
    house1 = House(status="active", price=100000, address="123 Main St")
    house2 = House(status="active", price=100000, address="456 Oak Ave")
    spec = field_contains("house.address", "Main")

    scope1 = ProcessContext({"house": house1})
    scope2 = ProcessContext({"house": house2})

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is False


def test_specification_composition_and():
    """Test composing specifications with AND operator."""
    spec = has_field("house") & field_equals("house.status", "active")

    house1 = House(status="active", price=100000)
    house2 = House(status="inactive", price=100000)

    scope1 = ProcessContext({"house": house1})
    scope2 = ProcessContext({"house": house2})
    scope3 = ProcessContext({"other": "value"})

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is False
    assert spec.is_satisfied_by(scope3) is False


def test_specification_composition_or():
    """Test composing specifications with OR operator."""
    spec = field_equals("status", "active") | field_equals("status", "pending")

    scope1 = ProcessContext({"status": "active"})
    scope2 = ProcessContext({"status": "pending"})
    scope3 = ProcessContext({"status": "rejected"})

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is True
    assert spec.is_satisfied_by(scope3) is False


def test_specification_composition_complex():
    """Test complex specification composition."""
    # (status is active AND price > 100000) OR (status is pending AND price < 50000)
    spec = (field_equals("status", "active") & field_gt("price", 100000)) | (
        field_equals("status", "pending") & field_lt("price", 50000)
    )

    scope1 = ProcessContext({"status": "active", "price": 150000})  # True
    scope2 = ProcessContext({"status": "active", "price": 50000})  # False
    scope3 = ProcessContext({"status": "pending", "price": 30000})  # True
    scope4 = ProcessContext({"status": "pending", "price": 100000})  # False

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is False
    assert spec.is_satisfied_by(scope3) is True
    assert spec.is_satisfied_by(scope4) is False


def test_specification_with_ifelse_action():
    """Test using specifications with IfElseAction."""
    from fractal.core.process.actions import SetValueAction
    from fractal.core.process.actions.control_flow import IfElseAction

    spec = has_field("house") & field_equals("house.status", "active")
    action = IfElseAction(
        specification=spec,
        actions_true=[SetValueAction(result="house is active")],
        actions_false=[SetValueAction(result="house not active")],
    )

    house1 = House(status="active", price=100000)
    house2 = House(status="inactive", price=100000)

    scope1 = ProcessContext({"house": house1})
    scope2 = ProcessContext({"house": house2})
    scope3 = ProcessContext({})

    result1 = action.execute(scope1)
    result2 = action.execute(scope2)
    result3 = action.execute(scope3)

    assert result1["result"] == "house is active"
    assert result2["result"] == "house not active"
    assert result3["result"] == "house not active"


def test_nested_field_access_with_dict():
    """Test nested field access with dictionaries."""
    spec = field_equals("config.database.host", "localhost")

    scope1 = ProcessContext(
        {"config": {"database": {"host": "localhost", "port": 5432}}}
    )

    scope2 = ProcessContext({"config": {"database": {"host": "remote", "port": 5432}}})

    assert spec.is_satisfied_by(scope1) is True
    assert spec.is_satisfied_by(scope2) is False


def test_missing_nested_field_returns_none():
    """Test that missing nested fields return None and don't raise errors."""
    spec = field_equals("a.b.c.d", "value")

    scope1 = ProcessContext({"a": {"b": None}})
    scope2 = ProcessContext({"x": "y"})
    scope3 = ProcessContext({})

    assert spec.is_satisfied_by(scope1) is False
    assert spec.is_satisfied_by(scope2) is False
    assert spec.is_satisfied_by(scope3) is False
