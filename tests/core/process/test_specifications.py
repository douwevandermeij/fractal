"""Tests for process specification builders."""

from dataclasses import dataclass

from fractal.core.process.process_context import ProcessContext
from fractal.core.process.specifications import (
    CallableSpecification,
    field_contains,
    field_equals,
    field_gt,
    field_gte,
    field_in,
    field_lt,
    field_lte,
    has_field,
    on_field,
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
    from fractal.core.process.actions import (
        CreateSpecificationAction,
        SetContextVariableAction,
    )
    from fractal.core.process.actions.control_flow import IfElseAction
    from fractal.core.process.process import Process

    spec = has_field("house") & field_equals("house.status", "active")

    process = Process(
        [
            CreateSpecificationAction(spec_factory=lambda ctx: spec, ctx_var="check"),
            IfElseAction(
                specification="check",
                actions_true=[SetContextVariableAction(result="house is active")],
                actions_false=[SetContextVariableAction(result="house not active")],
            ),
        ]
    )

    house1 = House(status="active", price=100000)
    house2 = House(status="inactive", price=100000)

    scope1 = ProcessContext({"house": house1})
    scope2 = ProcessContext({"house": house2})
    scope3 = ProcessContext({})

    result1 = process.run(scope1)
    result2 = process.run(scope2)
    result3 = process.run(scope3)

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


def test_on_field_with_entity_spec():
    """Test on_field applies entity specification to context field."""
    # Define entity specification (checks entity directly, not context)
    entity_spec = CallableSpecification(lambda house: house.status == "active")

    # Apply to context field
    context_spec = on_field("house", entity_spec)

    house1 = House(status="active", price=100000)
    house2 = House(status="inactive", price=100000)

    ctx1 = ProcessContext({"house": house1})
    ctx2 = ProcessContext({"house": house2})
    ctx3 = ProcessContext({"other": "value"})

    assert context_spec.is_satisfied_by(ctx1) is True
    assert context_spec.is_satisfied_by(ctx2) is False
    assert context_spec.is_satisfied_by(ctx3) is False  # Missing field


def test_on_field_with_fractal_specifications():
    """Test on_field works with fractal-specifications."""
    from fractal_specifications.generic.specification import Specification

    # Entity spec using fractal-specifications (domain-level)
    class HouseIsActiveSpec(Specification):
        def is_satisfied_by(self, house):
            return house.status == "active"

        def to_collection(self):
            return {"status": "active"}

    # Apply to context field
    context_spec = on_field("house", HouseIsActiveSpec())

    house1 = House(status="active", price=100000)
    house2 = House(status="inactive", price=100000)

    ctx1 = ProcessContext({"house": house1})
    ctx2 = ProcessContext({"house": house2})

    assert context_spec.is_satisfied_by(ctx1) is True
    assert context_spec.is_satisfied_by(ctx2) is False


def test_on_field_composition():
    """Test on_field composes with other context specifications."""
    entity_spec = CallableSpecification(lambda house: house.price > 50000)

    composed_spec = on_field("house", entity_spec) & has_field("user")

    house = House(status="active", price=100000)

    ctx1 = ProcessContext({"house": house, "user": "Alice"})
    ctx2 = ProcessContext({"house": house})  # Missing user
    ctx3 = ProcessContext({"user": "Alice"})  # Missing house

    assert composed_spec.is_satisfied_by(ctx1) is True
    assert composed_spec.is_satisfied_by(ctx2) is False
    assert composed_spec.is_satisfied_by(ctx3) is False


def test_on_field_nested_field():
    """Test on_field with nested field paths."""
    entity_spec = CallableSpecification(lambda addr: "Main" in addr)

    spec = on_field("house.address", entity_spec)

    house = House(status="active", price=100000, address="123 Main St")
    ctx1 = ProcessContext({"house": house})
    ctx2 = ProcessContext(
        {"house": House(status="active", price=100000, address="Oak Ave")}
    )

    assert spec.is_satisfied_by(ctx1) is True
    assert spec.is_satisfied_by(ctx2) is False


def test_on_field_vs_field_equals():
    """Test difference between on_field and field_equals approaches."""
    house = House(status="active", price=100000)
    ctx = ProcessContext({"house": house})

    # Approach 1: field_equals (checks context with field path)
    context_spec = field_equals("house.status", "active")
    assert context_spec.is_satisfied_by(ctx) is True

    # Approach 2: on_field (applies entity spec to field)
    entity_spec = CallableSpecification(lambda h: h.status == "active")
    separated_spec = on_field("house", entity_spec)
    assert separated_spec.is_satisfied_by(ctx) is True

    # Both work, but on_field separates concerns and allows reusing entity specs


def test_on_field_with_context_spec_string():
    """Test on_field with specification from context (string parameter)."""
    from fractal.core.process.actions import CreateSpecificationAction

    # Entity spec using fractal-specifications
    entity_spec = CallableSpecification(lambda house: house.status == "active")

    # Store specification in context
    ctx = ProcessContext({})
    create_action = CreateSpecificationAction(
        spec_factory=lambda _: entity_spec, ctx_var="house_is_active"
    )
    ctx = create_action.execute(ctx)

    # Use on_field with string (context var name)
    context_spec = on_field("house", "house_is_active")

    house1 = House(status="active", price=100000)
    house2 = House(status="inactive", price=100000)

    ctx1 = ProcessContext({"house": house1, "house_is_active": entity_spec})
    ctx2 = ProcessContext({"house": house2, "house_is_active": entity_spec})

    assert context_spec.is_satisfied_by(ctx1) is True
    assert context_spec.is_satisfied_by(ctx2) is False


def test_on_field_with_context_spec_dot_notation():
    """Test on_field with nested specification in context."""
    entity_spec = CallableSpecification(lambda house: house.price > 50000)

    # Store specification in nested structure
    ctx = ProcessContext({"specs": {"expensive_house": entity_spec}})

    # Use on_field with dot notation for specification
    context_spec = on_field("house", "specs.expensive_house")

    house1 = House(status="active", price=100000)
    house2 = House(status="active", price=30000)

    ctx1 = ProcessContext({"house": house1, "specs": {"expensive_house": entity_spec}})
    ctx2 = ProcessContext({"house": house2, "specs": {"expensive_house": entity_spec}})

    assert context_spec.is_satisfied_by(ctx1) is True
    assert context_spec.is_satisfied_by(ctx2) is False


def test_on_field_in_workflow_with_context_spec():
    """Test on_field with context-based specification in complete workflow."""
    from fractal.core.process.actions import (
        CreateSpecificationAction,
        SetContextVariableAction,
    )
    from fractal.core.process.actions.control_flow import IfElseAction
    from fractal.core.process.process import Process

    # Entity specification (for house object)
    entity_spec = CallableSpecification(
        lambda house: house.status == "active" and house.price > 50000
    )

    house1 = House(status="active", price=100000)
    house2 = House(status="inactive", price=100000)

    # Workflow with context-based specification
    process = Process(
        [
            SetContextVariableAction(house=house1),
            CreateSpecificationAction(
                spec_factory=lambda _: entity_spec, ctx_var="premium_house_spec"
            ),
            IfElseAction(
                specification=on_field("house", "premium_house_spec"),
                actions_true=[SetContextVariableAction(result="premium")],
                actions_false=[SetContextVariableAction(result="basic")],
            ),
        ]
    )

    result = process.run(ProcessContext({}))
    assert result["result"] == "premium"

    # Test with inactive house
    process2 = Process(
        [
            SetContextVariableAction(house=house2),
            CreateSpecificationAction(
                spec_factory=lambda _: entity_spec, ctx_var="premium_house_spec"
            ),
            IfElseAction(
                specification=on_field("house", "premium_house_spec"),
                actions_true=[SetContextVariableAction(result="premium")],
                actions_false=[SetContextVariableAction(result="basic")],
            ),
        ]
    )

    result2 = process2.run(ProcessContext({}))
    assert result2["result"] == "basic"


def test_on_field_backward_compatibility():
    """Test that on_field still works with direct Specification objects."""
    # This test ensures backward compatibility with old code

    # Old pattern - direct specification object
    entity_spec = CallableSpecification(lambda house: house.status == "active")
    context_spec = on_field("house", entity_spec)

    house1 = House(status="active", price=100000)
    house2 = House(status="inactive", price=100000)

    ctx1 = ProcessContext({"house": house1})
    ctx2 = ProcessContext({"house": house2})

    assert context_spec.is_satisfied_by(ctx1) is True
    assert context_spec.is_satisfied_by(ctx2) is False


def test_on_field_mixed_patterns():
    """Test mixing old (direct spec) and new (context spec) patterns."""
    from fractal.core.process.actions import (
        CreateSpecificationAction,
        SetContextVariableAction,
    )
    from fractal.core.process.actions.control_flow import IfElseAction
    from fractal.core.process.process import Process

    house = House(status="active", price=100000)

    # Old pattern - direct specification
    direct_spec = CallableSpecification(lambda h: h.status == "active")

    # New pattern - context-based specification
    price_spec = CallableSpecification(lambda h: h.price > 50000)

    process = Process(
        [
            SetContextVariableAction(house=house),
            # Old pattern in first check
            IfElseAction(
                specification=on_field("house", direct_spec),
                actions_true=[
                    # New pattern in second check
                    CreateSpecificationAction(
                        spec_factory=lambda _: price_spec, ctx_var="price_check"
                    ),
                    IfElseAction(
                        specification=on_field("house", "price_check"),
                        actions_true=[
                            SetContextVariableAction(result="premium_active")
                        ],
                        actions_false=[SetContextVariableAction(result="basic_active")],
                    ),
                ],
                actions_false=[SetContextVariableAction(result="inactive")],
            ),
        ]
    )

    result = process.run(ProcessContext({}))
    assert result["result"] == "premium_active"
