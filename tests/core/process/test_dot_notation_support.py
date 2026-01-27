"""Tests for dot notation support in ProcessContext and SetContextVariableAction."""

import pytest

from fractal.core.process.actions import SetContextVariableAction
from fractal.core.process.process import Process
from fractal.core.process.process_context import ProcessContext


def test_processcontext_init_with_dot_notation():
    """Test ProcessContext initialization with dot notation creates nested structure."""
    ctx = ProcessContext({"fractal.context": "app_context", "user.name": "Alice"})

    # Should create nested structure
    assert ctx["fractal"]["context"] == "app_context"
    assert ctx["user"]["name"] == "Alice"


def test_processcontext_init_with_mixed_keys():
    """Test mixing dotted and simple keys."""
    ctx = ProcessContext(
        {
            "fractal.context": "app_context",
            "simple_key": "simple_value",
            "nested.deep.value": "deep",
        }
    )

    assert ctx["fractal"]["context"] == "app_context"
    assert ctx["simple_key"] == "simple_value"
    assert ctx["nested"]["deep"]["value"] == "deep"


def test_processcontext_init_attribute_access():
    """Test that nested dicts from dot notation support attribute access."""
    ctx = ProcessContext({"fractal.context": "app_context"})

    # ctx.fractal returns a dict, so attribute access won't work on it
    # This is expected behavior - nested dicts are plain dicts
    assert ctx.fractal == {"context": "app_context"}
    assert ctx["fractal"]["context"] == "app_context"


def test_processcontext_init_conflict_detection():
    """Test that conflicts in nested structure are detected."""
    # Try to set both a value and nested keys at the same path
    with pytest.raises(ValueError, match="already has nested keys"):
        ProcessContext(
            {
                "fractal.context.value": "nested",
                "fractal.context": "flat",  # Conflict!
            }
        )


def test_processcontext_init_conflict_detection_reverse():
    """Test conflict detection works in reverse order too."""
    with pytest.raises(ValueError, match="already has a non-dict value"):
        ProcessContext(
            {
                "fractal": "flat",
                "fractal.context": "nested",  # Conflict!
            }
        )


def test_setcontextvariable_with_dot_notation():
    """Test SetContextVariableAction with dot notation."""
    ctx = ProcessContext()

    action = SetContextVariableAction(**{"fractal.context": "app_context"})
    result = action.execute(ctx)

    assert result["fractal"]["context"] == "app_context"


def test_setcontextvariable_with_multiple_dotted_keys():
    """Test SetContextVariableAction with multiple dotted keys."""
    ctx = ProcessContext()

    action = SetContextVariableAction(
        **{
            "fractal.context": "app_context",
            "config.database": "postgres",
            "config.port": 5432,
        }
    )
    result = action.execute(ctx)

    assert result["fractal"]["context"] == "app_context"
    assert result["config"]["database"] == "postgres"
    assert result["config"]["port"] == 5432


def test_setcontextvariable_mixed_keys():
    """Test SetContextVariableAction with mixed simple and dotted keys."""
    ctx = ProcessContext()

    action = SetContextVariableAction(simple="value", **{"nested.key": "nested_value"})
    result = action.execute(ctx)

    assert result["simple"] == "value"
    assert result["nested"]["key"] == "nested_value"


def test_complete_workflow_with_dot_notation():
    """Test a complete workflow using dot notation throughout."""

    # Mock application context
    class MockAppContext:
        def __init__(self):
            self.value = "initialized"

    app_ctx = MockAppContext()

    # Initialize with dot notation
    ctx = ProcessContext(
        {
            "fractal.context": app_ctx,
            "user.name": "Alice",
            "user.email": "alice@example.com",
        }
    )

    # Use SetContextVariableAction with dot notation
    process = Process(
        [
            SetContextVariableAction(**{"config.debug": True}),
            SetContextVariableAction(**{"config.log_level": "INFO"}),
        ]
    )

    result = process.run(ctx)

    # Verify nested structures
    assert result["fractal"]["context"].value == "initialized"
    assert result["user"]["name"] == "Alice"
    assert result["user"]["email"] == "alice@example.com"
    assert result["config"]["debug"] is True
    assert result["config"]["log_level"] == "INFO"


def test_deeply_nested_dot_notation():
    """Test deeply nested dot notation."""
    ctx = ProcessContext({"a.b.c.d.e": "deep"})

    assert ctx["a"]["b"]["c"]["d"]["e"] == "deep"


def test_overwrite_nested_value():
    """Test that setting a nested value twice overwrites correctly."""
    ctx = ProcessContext({"config.value": "first"})

    action = SetContextVariableAction(**{"config.value": "second"})
    result = action.execute(ctx)

    assert result["config"]["value"] == "second"


def test_extend_existing_nested_structure():
    """Test extending an existing nested structure."""
    ctx = ProcessContext({"config.a": "value_a"})

    action = SetContextVariableAction(**{"config.b": "value_b"})
    result = action.execute(ctx)

    assert result["config"]["a"] == "value_a"
    assert result["config"]["b"] == "value_b"


def test_real_world_fractal_context():
    """Test the real-world use case that prompted this feature."""

    class MockApplicationContext:
        def __init__(self):
            self.command_bus = "command_bus_instance"
            self.user_repository = "user_repo_instance"

    app_context = MockApplicationContext()

    # This is what the user wanted to do
    ctx = ProcessContext(
        {
            "fractal.context": app_context,
            "command": "some_command",
            "entity": "some_entity",
        }
    )

    # Should work now
    assert ctx["fractal"]["context"].command_bus == "command_bus_instance"
    assert ctx["fractal"]["context"].user_repository == "user_repo_instance"
    assert ctx["command"] == "some_command"
    assert ctx["entity"] == "some_entity"
