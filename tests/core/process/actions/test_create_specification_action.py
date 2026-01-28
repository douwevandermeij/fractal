"""Tests for CreateSpecificationAction and context-based specifications."""

from unittest.mock import Mock

import pytest
from fractal_specifications.generic.operators import (
    EqualsSpecification,
    GreaterThanSpecification,
    LessThanSpecification,
)

from fractal.core.process.actions import (
    CreateSpecificationAction,
    DeleteEntityAction,
    FetchEntityAction,
    FindEntitiesAction,
)
from fractal.core.process.process import Process
from fractal.core.process.process_context import ProcessContext


class TestCreateSpecificationAction:
    """Test CreateSpecificationAction basic functionality."""

    def test_create_simple_specification(self):
        """Test creating a simple specification and storing in context."""
        ctx = ProcessContext({})

        action = CreateSpecificationAction(
            specification_factory=lambda ctx: EqualsSpecification("id", 1),
            ctx_var="user_spec",
        )
        result = action.execute(ctx)

        assert "user_spec" in result
        spec = result["user_spec"]
        assert isinstance(spec, EqualsSpecification)

    def test_create_specification_with_default_ctx_var(self):
        """Test creating specification with default ctx_var='specification'."""
        ctx = ProcessContext({})

        action = CreateSpecificationAction(
            specification_factory=lambda ctx: EqualsSpecification("status", "active")
        )
        result = action.execute(ctx)

        assert "specification" in result
        spec = result["specification"]
        assert isinstance(spec, EqualsSpecification)

    def test_create_specification_using_context_values(self):
        """Test creating specification that accesses context values."""
        ctx = ProcessContext({"user_id": 123, "status": "active"})

        action = CreateSpecificationAction(
            specification_factory=lambda ctx: EqualsSpecification("id", ctx["user_id"]),
            ctx_var="user_spec",
        )
        result = action.execute(ctx)

        spec = result["user_spec"]
        assert isinstance(spec, EqualsSpecification)

    def test_create_complex_specification_with_composition(self):
        """Test creating complex specification using composition."""
        ctx = ProcessContext({"min_price": 100, "max_price": 500, "status": "active"})

        action = CreateSpecificationAction(
            specification_factory=lambda ctx: (
                EqualsSpecification("status", ctx["status"])
                & GreaterThanSpecification("price", ctx["min_price"])
                & LessThanSpecification("price", ctx["max_price"])
            ),
            ctx_var="filter_spec",
        )
        result = action.execute(ctx)

        spec = result["filter_spec"]
        # Verify it's a composed specification (created via & operator)
        assert spec is not None
        assert hasattr(spec, "is_satisfied_by")

    def test_create_specification_with_dot_notation(self):
        """Test storing specification in nested context variable."""
        ctx = ProcessContext({"filters": {}})

        action = CreateSpecificationAction(
            specification_factory=lambda ctx: EqualsSpecification("id", 1),
            ctx_var="filters.user_spec",
        )
        result = action.execute(ctx)

        assert "filters" in result
        assert "user_spec" in result["filters"]
        spec = result["filters"]["user_spec"]
        assert isinstance(spec, EqualsSpecification)

    def test_create_specification_from_command(self):
        """Test creating specification from command method."""

        class MockCommand:
            def get_specification(self):
                return EqualsSpecification("id", 42)

        command = MockCommand()
        ctx = ProcessContext({"command": command})

        action = CreateSpecificationAction(
            specification_factory=lambda ctx: ctx["command"].get_specification(),
            ctx_var="validation_spec",
        )
        result = action.execute(ctx)

        spec = result["validation_spec"]
        assert isinstance(spec, EqualsSpecification)


class TestFetchEntityActionWithContextSpec:
    """Test FetchEntityAction with context-based specifications."""

    def test_fetch_with_default_specification_var(self):
        """Test fetching entity using default 'specification' context variable."""
        mock_repo = Mock()
        mock_repo.find_one.return_value = {"id": 1, "name": "Test User"}

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        spec = EqualsSpecification("id", 1)
        ctx = ProcessContext({"fractal": mock_fractal, "specification": spec})

        action = FetchEntityAction(repository_name="user_repository", ctx_var="user")
        result = action.execute(ctx)

        assert result["user"]["id"] == 1
        assert result["user"]["name"] == "Test User"
        mock_repo.find_one.assert_called_once_with(spec)

    def test_fetch_with_custom_specification_var(self):
        """Test fetching entity using custom specification context variable."""
        mock_repo = Mock()
        mock_repo.find_one.return_value = {"id": 123, "email": "test@example.com"}

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        spec = EqualsSpecification("id", 123)
        ctx = ProcessContext({"fractal": mock_fractal, "user_spec": spec})

        action = FetchEntityAction(
            repository_name="user_repository",
            specification="user_spec",
            ctx_var="user",
        )
        result = action.execute(ctx)

        assert result["user"]["id"] == 123
        mock_repo.find_one.assert_called_once_with(spec)

    def test_fetch_with_dot_notation_specification(self):
        """Test fetching entity with specification from nested context."""
        mock_repo = Mock()
        mock_repo.find_one.return_value = {"id": 1, "name": "Test"}

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        spec = EqualsSpecification("id", 1)
        ctx = ProcessContext({"fractal": mock_fractal, "filters": {"user_spec": spec}})

        action = FetchEntityAction(
            repository_name="user_repository",
            specification="filters.user_spec",
            ctx_var="user",
        )
        result = action.execute(ctx)

        assert result["user"]["id"] == 1

    def test_fetch_raises_error_when_specification_not_found(self):
        """Test that FetchEntityAction raises error when specification not in context."""
        mock_context = Mock()
        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal})

        action = FetchEntityAction(
            repository_name="user_repository",
            specification="missing_spec",
            ctx_var="user",
        )

        with pytest.raises(KeyError, match="missing_spec"):
            action.execute(ctx)


class TestFindEntitiesActionWithContextSpec:
    """Test FindEntitiesAction with context-based specifications."""

    def test_find_with_custom_specification_var(self):
        """Test finding entities using custom specification context variable."""
        mock_repo = Mock()
        mock_repo.find.return_value = [{"id": 1}, {"id": 2}, {"id": 3}]

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        spec = EqualsSpecification("status", "active")
        ctx = ProcessContext({"fractal": mock_fractal, "status_filter": spec})

        action = FindEntitiesAction(
            repository_name="user_repository",
            specification="status_filter",
            ctx_var="users",
        )
        result = action.execute(ctx)

        assert len(result["users"]) == 3
        mock_repo.find.assert_called_once_with(spec)

    def test_find_all_entities_without_specification(self):
        """Test finding all entities when specification is None."""
        mock_repo = Mock()
        mock_repo.find.return_value = [{"id": 1}, {"id": 2}]

        mock_context = Mock()
        mock_context.item_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal})

        action = FindEntitiesAction(repository_name="item_repository", ctx_var="items")
        result = action.execute(ctx)

        assert len(result["items"]) == 2
        mock_repo.find.assert_called_once_with(None)

    def test_find_with_dot_notation_specification(self):
        """Test finding entities with specification from nested context."""
        mock_repo = Mock()
        mock_repo.find.return_value = [{"id": 1}]

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        spec = EqualsSpecification("active", True)
        ctx = ProcessContext(
            {"fractal": mock_fractal, "filters": {"active_spec": spec}}
        )

        action = FindEntitiesAction(
            repository_name="user_repository",
            specification="filters.active_spec",
            ctx_var="users",
        )
        result = action.execute(ctx)

        assert len(result["users"]) == 1


class TestDeleteEntityActionWithContextSpec:
    """Test DeleteEntityAction with context-based specifications."""

    def test_delete_with_default_specification_var(self):
        """Test deleting entity using default 'specification' context variable."""
        mock_repo = Mock()

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        spec = EqualsSpecification("id", 1)
        ctx = ProcessContext({"fractal": mock_fractal, "specification": spec})

        action = DeleteEntityAction(repository_name="user_repository")
        action.execute(ctx)

        mock_repo.remove_one.assert_called_once_with(spec)

    def test_delete_with_custom_specification_var(self):
        """Test deleting entity using custom specification context variable."""
        mock_repo = Mock()

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        spec = EqualsSpecification("id", 123)
        ctx = ProcessContext({"fractal": mock_fractal, "delete_spec": spec})

        action = DeleteEntityAction(
            repository_name="user_repository", specification="delete_spec"
        )
        action.execute(ctx)

        mock_repo.remove_one.assert_called_once_with(spec)

    def test_delete_with_dot_notation_specification(self):
        """Test deleting entity with specification from nested context."""
        mock_repo = Mock()

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        spec = EqualsSpecification("id", 1)
        ctx = ProcessContext(
            {"fractal": mock_fractal, "operations": {"delete_spec": spec}}
        )

        action = DeleteEntityAction(
            repository_name="user_repository", specification="operations.delete_spec"
        )
        action.execute(ctx)

        mock_repo.remove_one.assert_called_once_with(spec)


class TestCompleteWorkflowWithSpecifications:
    """Test complete workflows using CreateSpecificationAction with entity actions."""

    def test_workflow_create_and_fetch(self):
        """Test workflow that creates specification and fetches entity."""
        mock_repo = Mock()
        mock_repo.find_one.return_value = {"id": 123, "name": "Alice"}

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal, "user_id": 123})

        process = Process(
            [
                CreateSpecificationAction(
                    specification_factory=lambda ctx: EqualsSpecification(
                        "id", ctx["user_id"]
                    ),
                    ctx_var="user_spec",
                ),
                FetchEntityAction(
                    repository_name="user_repository",
                    specification="user_spec",
                    ctx_var="user",
                ),
            ]
        )

        result = process.run(ctx)

        assert result["user"]["id"] == 123
        assert result["user"]["name"] == "Alice"

    def test_workflow_with_default_specification_variable(self):
        """Test workflow using default 'specification' context variable."""
        mock_repo = Mock()
        mock_repo.find_one.return_value = {"id": 1, "email": "test@example.com"}

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal})

        process = Process(
            [
                CreateSpecificationAction(
                    specification_factory=lambda ctx: EqualsSpecification("id", 1)
                    # Uses default ctx_var="specification"
                ),
                FetchEntityAction(
                    repository_name="user_repository"
                    # Uses default specification="specification"
                ),
            ]
        )

        result = process.run(ctx)

        assert result["entity"]["id"] == 1
        assert result["entity"]["email"] == "test@example.com"

    def test_workflow_create_find_and_delete(self):
        """Test workflow with multiple entity operations."""
        mock_repo = Mock()
        mock_repo.find.return_value = [{"id": 1}, {"id": 2}]

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal, "status": "inactive"})

        process = Process(
            [
                # Create specification for finding
                CreateSpecificationAction(
                    specification_factory=lambda ctx: EqualsSpecification(
                        "status", ctx["status"]
                    ),
                    ctx_var="find_spec",
                ),
                # Find entities
                FindEntitiesAction(
                    repository_name="user_repository",
                    specification="find_spec",
                    ctx_var="users",
                ),
                # Create specification for deletion
                CreateSpecificationAction(
                    specification_factory=lambda ctx: EqualsSpecification("id", 1),
                    ctx_var="delete_spec",
                ),
                # Delete entity
                DeleteEntityAction(
                    repository_name="user_repository", specification="delete_spec"
                ),
            ]
        )

        result = process.run(ctx)

        assert len(result["users"]) == 2
        mock_repo.remove_one.assert_called_once()

    def test_workflow_with_dynamic_specification_composition(self):
        """Test workflow building complex specification from context values."""
        mock_repo = Mock()
        mock_repo.find.return_value = [{"id": 1, "price": 250}]

        mock_context = Mock()
        mock_context.house_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext(
            {
                "fractal": mock_fractal,
                "filter_status": "active",
                "min_price": 100,
                "max_price": 500,
            }
        )

        process = Process(
            [
                CreateSpecificationAction(
                    specification_factory=lambda ctx: (
                        EqualsSpecification("status", ctx["filter_status"])
                        & GreaterThanSpecification("price", ctx["min_price"])
                        & LessThanSpecification("price", ctx["max_price"])
                    ),
                    ctx_var="house_filter",
                ),
                FindEntitiesAction(
                    repository_name="house_repository",
                    specification="house_filter",
                    ctx_var="houses",
                ),
            ]
        )

        result = process.run(ctx)

        assert len(result["houses"]) == 1
        assert result["houses"][0]["price"] == 250

    def test_workflow_reusing_specification(self):
        """Test workflow where same specification is used by multiple actions."""
        mock_repo = Mock()
        mock_repo.find_one.return_value = {"id": 1, "name": "Test"}
        mock_repo.find.return_value = [{"id": 1}]

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        spec = EqualsSpecification("status", "active")
        ctx = ProcessContext({"fractal": mock_fractal})

        process = Process(
            [
                # Create specification once
                CreateSpecificationAction(
                    specification_factory=lambda ctx: spec, ctx_var="active_spec"
                ),
                # Use it for find
                FindEntitiesAction(
                    repository_name="user_repository",
                    specification="active_spec",
                    ctx_var="users",
                ),
                # Reuse for fetch
                FetchEntityAction(
                    repository_name="user_repository",
                    specification="active_spec",
                    ctx_var="user",
                ),
            ]
        )

        result = process.run(ctx)

        assert len(result["users"]) == 1
        assert result["user"]["id"] == 1


class TestErrorHandling:
    """Test error handling for context-based specifications."""

    def test_fetch_fails_when_specification_missing(self):
        """Test that FetchEntityAction fails gracefully when specification is missing."""
        mock_context = Mock()
        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal})

        action = FetchEntityAction(
            repository_name="user_repository",
            specification="nonexistent_spec",
            ctx_var="user",
        )

        with pytest.raises(KeyError):
            action.execute(ctx)

    def test_find_fails_when_specification_missing(self):
        """Test that FindEntitiesAction fails gracefully when specification is missing."""
        mock_context = Mock()
        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal})

        action = FindEntitiesAction(
            repository_name="user_repository",
            specification="nonexistent_spec",
            ctx_var="users",
        )

        with pytest.raises(KeyError):
            action.execute(ctx)

    def test_delete_fails_when_specification_missing(self):
        """Test that DeleteEntityAction fails gracefully when specification is missing."""
        mock_context = Mock()
        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal})

        action = DeleteEntityAction(
            repository_name="user_repository", specification="nonexistent_spec"
        )

        with pytest.raises(KeyError):
            action.execute(ctx)
