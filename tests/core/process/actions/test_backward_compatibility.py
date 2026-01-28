"""Tests for backward compatibility with direct Specification objects."""

from unittest.mock import Mock

from fractal_specifications.generic.operators import EqualsSpecification

from fractal.core.process.actions import (
    CreateSpecificationAction,
    DeleteEntityAction,
    FetchEntityAction,
    FindEntitiesAction,
    IncreaseValueAction,
    SetContextVariableAction,
)
from fractal.core.process.actions.control_flow import IfElseAction, WhileAction
from fractal.core.process.process import Process
from fractal.core.process.process_context import ProcessContext
from fractal.core.process.specifications import field_lt


class TestEntityActionsBackwardCompatibility:
    """Test that entity actions still work with direct Specification objects."""

    def test_fetch_entity_with_direct_specification(self):
        """Test FetchEntityAction with direct Specification object (old pattern)."""
        mock_repo = Mock()
        mock_repo.find_one.return_value = {"id": 1, "name": "Test"}

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal})

        # Old pattern - direct Specification object
        spec = EqualsSpecification("id", 1)
        action = FetchEntityAction(
            repository_name="user_repository", specification=spec, ctx_var="user"
        )
        result = action.execute(ctx)

        assert result["user"]["id"] == 1
        assert result["user"]["name"] == "Test"
        mock_repo.find_one.assert_called_once_with(spec)

    def test_find_entities_with_direct_specification(self):
        """Test FindEntitiesAction with direct Specification object (old pattern)."""
        mock_repo = Mock()
        mock_repo.find.return_value = [{"id": 1}, {"id": 2}]

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal})

        # Old pattern - direct Specification object
        spec = EqualsSpecification("status", "active")
        action = FindEntitiesAction(
            repository_name="user_repository", specification=spec, ctx_var="users"
        )
        result = action.execute(ctx)

        assert len(result["users"]) == 2
        mock_repo.find.assert_called_once_with(spec)

    def test_delete_entity_with_direct_specification(self):
        """Test DeleteEntityAction with direct Specification object (old pattern)."""
        mock_repo = Mock()

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal})

        # Old pattern - direct Specification object
        spec = EqualsSpecification("id", 1)
        action = DeleteEntityAction(
            repository_name="user_repository", specification=spec
        )
        action.execute(ctx)

        mock_repo.remove_one.assert_called_once_with(spec)


class TestControlFlowBackwardCompatibility:
    """Test that control flow actions still work with direct Specification objects."""

    def test_ifelse_with_direct_specification(self):
        """Test IfElseAction with direct Specification object (old pattern)."""
        from fractal.core.process.specifications import field_equals

        # Old pattern - direct Specification object
        spec = field_equals("status", "active")
        process = Process(
            [
                SetContextVariableAction(status="active"),
                IfElseAction(
                    specification=spec,
                    actions_true=[SetContextVariableAction(result="active")],
                    actions_false=[SetContextVariableAction(result="inactive")],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["result"] == "active"

    def test_while_with_direct_specification(self):
        """Test WhileAction with direct Specification object (old pattern)."""
        # Old pattern - direct Specification object
        spec = field_lt("count", 3)
        process = Process(
            [
                SetContextVariableAction(count=0),
                WhileAction(
                    specification=spec,
                    actions=[IncreaseValueAction(ctx_var="count", value=1)],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["count"] == 3


class TestMixedPatterns:
    """Test that old and new patterns can be used together."""

    def test_old_and_new_patterns_together(self):
        """Test using both old (direct spec) and new (context spec) patterns in same workflow."""
        mock_repo = Mock()
        mock_repo.find.return_value = [{"id": 1}, {"id": 2}]
        mock_repo.find_one.return_value = {"id": 1, "name": "Test"}

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        process = Process(
            [
                # Old pattern - direct specification
                FindEntitiesAction(
                    repository_name="user_repository",
                    specification=EqualsSpecification("status", "active"),
                    ctx_var="all_users",
                ),
                # New pattern - context-based specification
                CreateSpecificationAction(
                    specification_factory=lambda ctx: EqualsSpecification("id", 1),
                    ctx_var="user_spec",
                ),
                FetchEntityAction(
                    repository_name="user_repository",
                    specification="user_spec",
                    ctx_var="specific_user",
                ),
            ]
        )

        result = process.run(ProcessContext({"fractal": mock_fractal}))

        assert len(result["all_users"]) == 2
        assert result["specific_user"]["id"] == 1

    def test_control_flow_mixed_patterns(self):
        """Test control flow with both old and new patterns."""
        from fractal.core.process.specifications import field_equals

        process = Process(
            [
                SetContextVariableAction(status="active", count=0),
                # Old pattern in IfElse
                IfElseAction(
                    specification=field_equals("status", "active"),
                    actions_true=[
                        # New pattern in While
                        CreateSpecificationAction(
                            specification_factory=lambda ctx: field_lt("count", 3),
                            ctx_var="loop_check",
                        ),
                        WhileAction(
                            specification="loop_check",
                            actions=[IncreaseValueAction(ctx_var="count", value=1)],
                        ),
                    ],
                ),
            ]
        )

        result = process.run(ProcessContext({}))
        assert result["count"] == 3
