"""Tests for ProcessContext safety features."""

import pytest

from fractal.core.process.process_context import ProcessContext


def test_context_raises_keyerror_for_missing_keys():
    """Test that __getitem__ raises KeyError for missing keys (standard dict behavior)."""
    ctx = ProcessContext({"name": "John"})

    # Should work for existing keys
    assert ctx["name"] == "John"

    # Should raise KeyError for missing keys
    with pytest.raises(KeyError):
        _ = ctx["missing_key"]


def test_context_get_returns_default_for_missing_keys():
    """Test that get() returns default for missing keys (safe access)."""
    ctx = ProcessContext({"name": "John"})

    # Should return None by default
    assert ctx.get("missing_key") is None

    # Should return custom default
    assert ctx.get("missing_key", "default") == "default"

    # Should return actual value for existing keys
    assert ctx.get("name") == "John"


def test_context_attribute_access_returns_none():
    """Test that attribute access returns None for missing keys (convenience)."""
    ctx = ProcessContext({"name": "John"})

    # Should work for existing keys
    assert ctx.name == "John"

    # Should return None for missing keys (not raise AttributeError)
    assert ctx.missing_attribute is None


def test_context_contains_operator():
    """Test that 'in' operator works correctly."""
    ctx = ProcessContext({"name": "John", "age": 30})

    assert "name" in ctx
    assert "age" in ctx
    assert "missing" not in ctx


def test_context_copy_creates_deep_copy():
    """Test that copy() creates a true deep copy."""
    original = ProcessContext(
        {"simple": "value", "nested": {"level1": {"level2": "deep"}}}
    )

    # Create a copy
    copied = original.copy()

    # Modify the copy's nested structure
    copied["nested"]["level1"]["level2"] = "modified"

    # Original should be unchanged
    assert original["nested"]["level1"]["level2"] == "deep"
    assert copied["nested"]["level1"]["level2"] == "modified"


def test_context_copy_with_list():
    """Test that copy() handles lists correctly."""
    original = ProcessContext({"items": [1, 2, 3]})
    copied = original.copy()

    # Modify the copy's list
    copied["items"].append(4)

    # Original should be unchanged
    assert original["items"] == [1, 2, 3]
    assert copied["items"] == [1, 2, 3, 4]


def test_context_freeze_prevents_modification():
    """Test that freeze() makes context immutable."""
    ctx = ProcessContext({"name": "John"})

    # Should work before freezing
    ctx["age"] = 30
    assert ctx["age"] == 30

    # Freeze the context
    ctx.freeze()

    # Should not allow modifications
    with pytest.raises(RuntimeError, match="Cannot modify frozen ProcessContext"):
        ctx["new_key"] = "value"

    with pytest.raises(RuntimeError, match="Cannot modify frozen ProcessContext"):
        ctx["name"] = "Jane"


def test_context_freeze_prevents_update():
    """Test that frozen context cannot be updated."""
    ctx1 = ProcessContext({"name": "John"})
    ctx2 = ProcessContext({"age": 30})

    ctx1.freeze()

    with pytest.raises(RuntimeError, match="Cannot modify frozen ProcessContext"):
        ctx1.update(ctx2)


def test_context_freeze_returns_self():
    """Test that freeze() returns self for chaining."""
    ctx = ProcessContext({"name": "John"})
    result = ctx.freeze()

    assert result is ctx
    assert ctx.is_frozen()


def test_context_is_frozen_check():
    """Test is_frozen() method."""
    ctx = ProcessContext({"name": "John"})

    assert not ctx.is_frozen()

    ctx.freeze()

    assert ctx.is_frozen()


def test_context_frozen_in_repr():
    """Test that frozen status appears in repr."""
    ctx = ProcessContext({"name": "John"})

    repr_unfrozen = repr(ctx)
    assert "(frozen)" not in repr_unfrozen

    ctx.freeze()
    repr_frozen = repr(ctx)
    assert "(frozen)" in repr_frozen


def test_context_keys_values_items():
    """Test dict-like methods keys(), values(), items()."""
    ctx = ProcessContext({"name": "John", "age": 30})

    assert set(ctx.keys()) == {"name", "age"}
    assert set(ctx.values()) == {"John", 30}
    assert set(ctx.items()) == {("name", "John"), ("age", 30)}


def test_context_update_merges_data():
    """Test that update() merges contexts correctly."""
    ctx1 = ProcessContext({"a": 1, "b": 2})
    ctx2 = ProcessContext({"b": 3, "c": 4})

    result = ctx1.update(ctx2)

    # Should merge and overwrite
    assert ctx1["a"] == 1
    assert ctx1["b"] == 3  # Overwritten
    assert ctx1["c"] == 4

    # Should return self for chaining
    assert result is ctx1


def test_context_initialization_copies_dict():
    """Test that initialization makes a copy of input dict."""
    original_dict = {"name": "John"}
    ctx = ProcessContext(original_dict)

    # Modify the original dict
    original_dict["name"] = "Jane"

    # Context should be unaffected
    assert ctx["name"] == "John"


def test_context_initialization_with_none():
    """Test initialization with None creates empty context."""
    ctx = ProcessContext(None)

    assert len(ctx.keys()) == 0


def test_context_initialization_with_no_args():
    """Test initialization with no arguments creates empty context."""
    ctx = ProcessContext()

    assert len(ctx.keys()) == 0


def test_context_repr_shows_data():
    """Test that repr shows the internal data."""
    ctx = ProcessContext({"name": "John", "age": 30})

    repr_str = repr(ctx)
    assert "ProcessContext" in repr_str
    assert "name" in repr_str
    assert "John" in repr_str


def test_parallel_execution_with_copy():
    """Test that copy() enables safe parallel execution."""
    original = ProcessContext({"counter": 0, "items": []})

    # Simulate parallel branches
    branch1 = original.copy()
    branch2 = original.copy()

    # Each branch modifies independently
    branch1["counter"] = 1
    branch1["items"].append("item1")

    branch2["counter"] = 2
    branch2["items"].append("item2")

    # Original should be unchanged
    assert original["counter"] == 0
    assert original["items"] == []

    # Branches should be independent
    assert branch1["counter"] == 1
    assert branch1["items"] == ["item1"]

    assert branch2["counter"] == 2
    assert branch2["items"] == ["item2"]


def test_context_setitem_modifies_internal_data():
    """Test that __setitem__ modifies the internal data correctly."""
    ctx = ProcessContext()

    ctx["name"] = "John"
    ctx["age"] = 30

    assert ctx["name"] == "John"
    assert ctx["age"] == 30
    assert "name" in ctx
    assert "age" in ctx
