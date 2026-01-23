import copy as copy_module
from typing import Dict, Optional


class ProcessContext:
    """Process execution context with safe state management.

    Provides a dict-like interface for passing state between actions in a Process.
    Supports deep copying for parallel execution and optional freezing for immutability.
    """

    def __init__(self, data: Optional[Dict] = None):
        """Initialize context with optional data.

        Args:
            data: Initial data dict (will be shallow copied for safety)
        """
        self._data = dict(data) if data else {}
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
        """Merge another context into this one.

        Args:
            ctx: Context to merge from

        Returns:
            Self for chaining

        Raises:
            RuntimeError: If context is frozen
        """
        if self._locked:
            raise RuntimeError("Cannot modify frozen ProcessContext")
        self._data.update(ctx._data)
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
