"""Tests for RaiseExceptionAction."""

import pytest

from fractal.core.process.actions import (
    CreateSpecificationAction,
    RaiseExceptionAction,
    SetContextVariableAction,
)
from fractal.core.process.actions.control_flow import IfElseAction
from fractal.core.process.process import Process
from fractal.core.process.process_context import ProcessContext
from fractal.core.process.specifications import field_equals


class CustomValidationError(Exception):
    """Custom exception for testing."""


class TestRaiseExceptionAction:
    """Test RaiseExceptionAction basic functionality."""

    def test_raise_with_static_message(self):
        """Test raising exception with static message."""
        action = RaiseExceptionAction(message="Test error")

        with pytest.raises(Exception, match="Test error"):
            action.execute(ProcessContext({}))

    def test_raise_with_custom_exception_class(self):
        """Test raising custom exception class."""
        action = RaiseExceptionAction(
            exception_class=ValueError, message="Invalid value"
        )

        with pytest.raises(ValueError, match="Invalid value"):
            action.execute(ProcessContext({}))

    def test_raise_with_dynamic_message(self):
        """Test raising exception with message from context."""
        action = RaiseExceptionAction(
            exception_class=ValueError,
            message_factory=lambda ctx: f"User {ctx['user_id']} failed validation",
        )

        ctx = ProcessContext({"user_id": "123"})

        with pytest.raises(ValueError, match="User 123 failed validation"):
            action.execute(ctx)

    def test_raise_without_message(self):
        """Test raising exception without message."""
        action = RaiseExceptionAction(exception_class=StopIteration)

        with pytest.raises(StopIteration):
            action.execute(ProcessContext({}))

    def test_message_factory_takes_precedence(self):
        """Test that message_factory takes precedence over message."""
        action = RaiseExceptionAction(
            exception_class=ValueError,
            message="Default error",
            message_factory=lambda ctx: "Dynamic error",
        )

        with pytest.raises(ValueError, match="Dynamic error"):
            action.execute(ProcessContext({}))

    def test_message_factory_fallback_to_static(self):
        """Test fallback to static message when message_factory returns None."""
        action = RaiseExceptionAction(
            exception_class=ValueError,
            message="Fallback error",
            message_factory=lambda ctx: ctx.get("error_message"),
        )

        ctx = ProcessContext({})  # No error_message in context

        with pytest.raises(ValueError, match="Fallback error"):
            action.execute(ctx)

    def test_message_factory_with_conditional_logic(self):
        """Test message_factory with conditional logic."""
        action = RaiseExceptionAction(
            exception_class=ValueError,
            message="Default error",
            message_factory=lambda ctx: (
                f"Custom error: {ctx['details']}" if "details" in ctx else None
            ),
        )

        # Test with details in context
        ctx_with_details = ProcessContext({"details": "Something went wrong"})
        with pytest.raises(ValueError, match="Custom error: Something went wrong"):
            action.execute(ctx_with_details)

        # Test without details (falls back to static message)
        ctx_without_details = ProcessContext({})
        with pytest.raises(ValueError, match="Default error"):
            action.execute(ctx_without_details)

    def test_custom_exception_with_dynamic_message(self):
        """Test custom exception class with dynamic message."""
        action = RaiseExceptionAction(
            exception_class=CustomValidationError,
            message_factory=lambda ctx: f"Validation failed: {ctx['reason']}",
        )

        ctx = ProcessContext({"reason": "Invalid email format"})

        with pytest.raises(
            CustomValidationError, match="Validation failed: Invalid email format"
        ):
            action.execute(ctx)

    def test_message_factory_accessing_nested_context(self):
        """Test message_factory accessing nested context values."""
        action = RaiseExceptionAction(
            exception_class=ValueError,
            message_factory=lambda ctx: (
                f"User {ctx['user']['name']} (ID: {ctx['user']['id']}) is not authorized"
            ),
        )

        ctx = ProcessContext({"user": {"id": "123", "name": "Alice"}})

        with pytest.raises(
            ValueError, match="User Alice \\(ID: 123\\) is not authorized"
        ):
            action.execute(ctx)


class TestRaiseExceptionInWorkflows:
    """Test RaiseExceptionAction in complete workflows."""

    def test_conditional_exception_raising(self):
        """Test raising exception conditionally based on context."""
        process = Process(
            [
                SetContextVariableAction(age=15),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_equals("age", 15),
                    ctx_var="underage_check",
                ),
                IfElseAction(
                    specification="underage_check",
                    actions_true=[
                        RaiseExceptionAction(
                            exception_class=ValueError,
                            message="User must be 18 or older",
                        )
                    ],
                ),
            ]
        )

        with pytest.raises(ValueError, match="User must be 18 or older"):
            process.run(ProcessContext({}))

    def test_validation_workflow_with_dynamic_errors(self):
        """Test validation workflow with dynamic error messages."""
        from fractal.core.process.specifications import field_equals

        # Simple validation: if email equals "invalid-email", raise exception
        process = Process(
            [
                SetContextVariableAction(email="invalid-email"),
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_equals(
                        "email", "invalid-email"
                    ),
                    ctx_var="invalid_email",
                ),
                IfElseAction(
                    specification="invalid_email",
                    actions_true=[
                        RaiseExceptionAction(
                            exception_class=ValueError,
                            message_factory=lambda ctx: (
                                f"Invalid email format: '{ctx['email']}'"
                            ),
                        )
                    ],
                ),
            ]
        )

        with pytest.raises(ValueError, match="Invalid email format: 'invalid-email'"):
            process.run(ProcessContext({}))

    def test_exception_with_error_details_from_context(self):
        """Test exception with detailed error information from context."""
        process = Process(
            [
                SetContextVariableAction(
                    field_name="username",
                    field_value="ab",
                    min_length=3,
                ),
                RaiseExceptionAction(
                    exception_class=ValueError,
                    message_factory=lambda ctx: (
                        f"Field '{ctx['field_name']}' must be at least "
                        f"{ctx['min_length']} characters (got {len(ctx['field_value'])})"
                    ),
                ),
            ]
        )

        with pytest.raises(
            ValueError,
            match="Field 'username' must be at least 3 characters \\(got 2\\)",
        ):
            process.run(ProcessContext({}))

    def test_multiple_validation_steps(self):
        """Test multiple validation steps with different exceptions."""
        from fractal.core.process.specifications import field_equals

        process = Process(
            [
                SetContextVariableAction(username="", email="invalid"),
                # Check username
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_equals("username", ""),
                    ctx_var="empty_username",
                ),
                IfElseAction(
                    specification="empty_username",
                    actions_true=[
                        RaiseExceptionAction(
                            exception_class=ValueError,
                            message="Username cannot be empty",
                        )
                    ],
                ),
                # Check email (won't be reached if username is empty)
                CreateSpecificationAction(
                    specification_factory=lambda ctx: field_equals("email", "invalid"),
                    ctx_var="invalid_email",
                ),
                IfElseAction(
                    specification="invalid_email",
                    actions_true=[
                        RaiseExceptionAction(
                            exception_class=ValueError,
                            message="Email must contain @",
                        )
                    ],
                ),
            ]
        )

        # First validation should fail
        with pytest.raises(ValueError, match="Username cannot be empty"):
            process.run(ProcessContext({}))

    def test_exception_in_try_except_workflow(self):
        """Test RaiseExceptionAction with TryExceptAction."""
        from fractal.core.process.actions.control_flow import TryExceptAction

        process = Process(
            [
                TryExceptAction(
                    actions=[
                        SetContextVariableAction(value=10),
                        CreateSpecificationAction(
                            specification_factory=lambda ctx: field_equals("value", 10),
                            ctx_var="check",
                        ),
                        IfElseAction(
                            specification="check",
                            actions_true=[
                                RaiseExceptionAction(
                                    exception_class=ValueError,
                                    message="Value cannot be 10",
                                )
                            ],
                        ),
                    ],
                    except_actions=[
                        SetContextVariableAction(error_caught=True),
                    ],
                )
            ]
        )

        result = process.run(ProcessContext({}))

        # Exception should be caught
        assert result["error_caught"] is True
        assert result["last_error_type"] == "ValueError"
        assert result["last_error_message"] == "Value cannot be 10"


class TestRaiseExceptionEdgeCases:
    """Test edge cases for RaiseExceptionAction."""

    def test_default_exception_class(self):
        """Test that default exception class is Exception."""
        action = RaiseExceptionAction(message="Error")

        with pytest.raises(Exception, match="Error"):
            action.execute(ProcessContext({}))

    def test_empty_string_message(self):
        """Test raising exception with empty string message."""
        action = RaiseExceptionAction(
            exception_class=ValueError,
            message="",
        )

        # Empty string is truthy for exception message
        with pytest.raises(ValueError):
            action.execute(ProcessContext({}))

    def test_message_factory_complex_formatting(self):
        """Test message_factory with complex string formatting."""
        action = RaiseExceptionAction(
            exception_class=ValueError,
            message_factory=lambda ctx: (
                f"Validation errors:\n"
                f"- Username: {ctx.get('username_error', 'OK')}\n"
                f"- Email: {ctx.get('email_error', 'OK')}\n"
                f"- Age: {ctx.get('age_error', 'OK')}"
            ),
        )

        ctx = ProcessContext(
            {
                "username_error": "Too short",
                "email_error": "Invalid format",
            }
        )

        with pytest.raises(ValueError) as exc_info:
            action.execute(ctx)

        error_message = str(exc_info.value)
        assert "Username: Too short" in error_message
        assert "Email: Invalid format" in error_message
        assert "Age: OK" in error_message

    def test_message_factory_with_exception(self):
        """Test message_factory that raises an exception."""

        def faulty_factory(ctx):
            return ctx["nonexistent_key"]  # This will raise KeyError

        action = RaiseExceptionAction(
            exception_class=ValueError,
            message_factory=faulty_factory,
        )

        # The KeyError from message_factory should propagate
        with pytest.raises(KeyError):
            action.execute(ProcessContext({}))
