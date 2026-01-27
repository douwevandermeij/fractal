import copy as copy_module
from typing import Dict, Optional


def _expand_dotted_keys(flat_dict: dict) -> dict:
    """Convert flat dict with dot-notation keys into nested dict.

    This allows initialization to use dot notation:
        {"fractal.context": value} → {"fractal": {"context": value}}

    Args:
        flat_dict: Dict with potentially dotted keys

    Returns:
        Dict with nested structure

    Raises:
        ValueError: If there are conflicts in the nested structure
    """
    result = {}
    for key, value in flat_dict.items():
        if "." not in key:
            # Simple key, no nesting
            result[key] = value
        else:
            # Dotted key, create nested structure
            parts = key.split(".")
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    # Conflict: trying to create nested structure where value exists
                    raise ValueError(
                        f"Cannot create nested key '{key}': '{part}' already has a non-dict value"
                    )
                current = current[part]

            # Set the final value
            final_key = parts[-1]
            if final_key in current and isinstance(current[final_key], dict):
                # Conflict: trying to set value where dict exists
                raise ValueError(
                    f"Cannot set '{key}': '{final_key}' already has nested keys"
                )
            current[final_key] = value

    return result


def _deep_merge(target: dict, source: dict) -> dict:
    """Deep merge source dict into target dict.

    Recursively merges nested dicts. Non-dict values in source overwrite target.

    Args:
        target: Dict to merge into (will be modified)
        source: Dict to merge from

    Returns:
        The modified target dict
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            # Both are dicts, merge recursively
            _deep_merge(target[key], value)
        else:
            # Overwrite with source value
            target[key] = value
    return target


class ProcessContext:
    """Process execution context with safe state management.

    Provides a dict-like interface for passing state between actions in a Process.
    Supports deep copying for parallel execution and optional freezing for immutability.
    Supports dot notation in initialization for nested structures.
    """

    def __init__(self, data: Optional[Dict] = None):
        """Initialize context with optional data.

        Supports dot notation for creating nested structures:
            ProcessContext({"fractal.context": app_context})
            # Creates: {"fractal": {"context": app_context}}

        Args:
            data: Initial data dict (will be shallow copied and expanded for dot notation)
        """
        if data:
            # Expand any dotted keys into nested structure
            expanded = _expand_dotted_keys(data)
            self._data = dict(expanded)
        else:
            self._data = {}
        self._locked = False

    def __getattr__(self, item):
        """Allow attribute-style access for convenience: ctx.field_name

        Returns None if key doesn't exist (safe for optional access).
        """
        if item.startswith("_"):
            # Avoid infinite recursion for private attributes
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{item}'"
            )
        return self._data.get(item)

    def __getitem__(self, item):
        """Get item with dict-like access: ctx["key"]

        Raises KeyError if key doesn't exist (standard dict behavior).
        Use .get() for optional access with defaults.
        """
        return self._data[item]

    def __setitem__(self, key, value):
        """Set item: ctx["key"] = value

        Raises RuntimeError if context is frozen.
        """
        if self._locked:
            raise RuntimeError("Cannot modify frozen ProcessContext")
        self._data[key] = value

    def __contains__(self, key):
        """Check if key exists: "key" in ctx"""
        return key in self._data

    def __repr__(self):
        """String representation showing internal data."""
        frozen_marker = " (frozen)" if self._locked else ""
        return f"ProcessContext({self._data!r}){frozen_marker}"

    def get(self, key, default=None):
        """Get value with optional default.

        Args:
            key: Key to lookup
            default: Value to return if key doesn't exist

        Returns:
            Value for key, or default if key not found
        """
        return self._data.get(key, default)

    def update(self, ctx: "ProcessContext") -> "ProcessContext":
        """Merge another context into this one with deep merging.

        Recursively merges nested dicts from ctx into this context.
        Non-dict values from ctx overwrite values in this context.

        Args:
            ctx: Context to merge from

        Returns:
            Self for chaining

        Raises:
            RuntimeError: If context is frozen
        """
        if self._locked:
            raise RuntimeError("Cannot modify frozen ProcessContext")
        _deep_merge(self._data, ctx._data)
        return self

    def copy(self) -> "ProcessContext":
        """Create a deep copy of this context.

        Useful for parallel execution where each branch needs isolated state.

        Returns:
            New ProcessContext with deep-copied data
        """
        return ProcessContext(copy_module.deepcopy(self._data))

    def freeze(self) -> "ProcessContext":
        """Make this context immutable.

        After freezing, any attempt to modify will raise RuntimeError.
        Useful for passing read-only context to parallel branches.

        Returns:
            Self for chaining
        """
        self._locked = True
        return self

    def is_frozen(self) -> bool:
        """Check if context is frozen.

        Returns:
            True if context is immutable
        """
        return self._locked

    def keys(self):
        """Get all keys in context."""
        return self._data.keys()

    def values(self):
        """Get all values in context."""
        return self._data.values()

    def items(self):
        """Get all key-value pairs in context."""
        return self._data.items()
