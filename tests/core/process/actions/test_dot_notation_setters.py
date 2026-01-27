"""Test dot notation support for all actions that set values in ProcessContext."""

from unittest.mock import AsyncMock, Mock

import pytest
from fractal_specifications.generic.operators import EqualsSpecification

from fractal.core.process.actions import (
    ApplyToValueAction,
    CommandAction,
    FetchEntityAction,
    FindEntitiesAction,
    IncreaseValueAction,
    QueryAction,
)
from fractal.core.process.process_context import ProcessContext


class TestApplyToValueActionDotNotation:
    """Test ApplyToValueAction with dot notation support."""

    def test_apply_to_simple_field(self):
        """Test backward compatibility - simple field without dots."""
        ctx = ProcessContext({"count": 5})
        action = ApplyToValueAction(field="count", function=lambda x: x * 2)
        result = action.execute(ctx)
        assert result["count"] == 10

    def test_apply_to_nested_field(self):
        """Test applying function to nested field."""
        ctx = ProcessContext({"stats": {"count": 5}})
        action = ApplyToValueAction(field="stats.count", function=lambda x: x * 2)
        result = action.execute(ctx)
        assert result["stats"]["count"] == 10

    def test_apply_to_deeply_nested_field(self):
        """Test applying function to deeply nested field."""
        ctx = ProcessContext({"data": {"stats": {"count": 5}}})
        action = ApplyToValueAction(field="data.stats.count", function=lambda x: x + 10)
        result = action.execute(ctx)
        assert result["data"]["stats"]["count"] == 15

    def test_apply_dict_transformation(self):
        """Test applying dict transformation to nested field."""
        ctx = ProcessContext({"user": {"preferences": {"theme": "light"}}})
        action = ApplyToValueAction(
            field="user.preferences",
            function=lambda prefs: {**prefs, "theme": "dark", "notifications": True},
        )
        result = action.execute(ctx)
        assert result["user"]["preferences"]["theme"] == "dark"
        assert result["user"]["preferences"]["notifications"] is True


class TestIncreaseValueActionDotNotation:
    """Test IncreaseValueAction with dot notation support."""

    def test_increase_simple_field(self):
        """Test backward compatibility - simple field without dots."""
        ctx = ProcessContext({"count": 5})
        action = IncreaseValueAction(field="count", value=3)
        result = action.execute(ctx)
        assert result["count"] == 8

    def test_increase_nested_field(self):
        """Test increasing nested field."""
        ctx = ProcessContext({"stats": {"views": 10}})
        action = IncreaseValueAction(field="stats.views", value=1)
        result = action.execute(ctx)
        assert result["stats"]["views"] == 11

    def test_increase_deeply_nested_field(self):
        """Test increasing deeply nested field."""
        ctx = ProcessContext({"metrics": {"page": {"views": 100}}})
        action = IncreaseValueAction(field="metrics.page.views", value=5)
        result = action.execute(ctx)
        assert result["metrics"]["page"]["views"] == 105

    def test_increase_negative_value(self):
        """Test decreasing with negative value."""
        ctx = ProcessContext({"stats": {"count": 10}})
        action = IncreaseValueAction(field="stats.count", value=-3)
        result = action.execute(ctx)
        assert result["stats"]["count"] == 7


class TestQueryActionDotNotation:
    """Test QueryAction with dot notation support."""

    def test_query_simple_field(self):
        """Test backward compatibility - simple field without dots."""
        ctx = ProcessContext({})
        action = QueryAction(query_func=lambda ctx: [1, 2, 3], result_field="result")
        result = action.execute(ctx)
        assert result["result"] == [1, 2, 3]

    def test_query_nested_field(self):
        """Test storing query result in nested field."""
        ctx = ProcessContext({"data": {}})
        action = QueryAction(
            query_func=lambda ctx: ["user1", "user2"], result_field="data.users"
        )
        result = action.execute(ctx)
        assert result["data"]["users"] == ["user1", "user2"]

    def test_query_deeply_nested_field(self):
        """Test storing query result in deeply nested field."""
        ctx = ProcessContext({"response": {"data": {}}})
        action = QueryAction(
            query_func=lambda ctx: {"total": 42},
            result_field="response.data.summary",
        )
        result = action.execute(ctx)
        assert result["response"]["data"]["summary"] == {"total": 42}

    def test_query_default_field(self):
        """Test using default result_field."""
        ctx = ProcessContext({})
        action = QueryAction(query_func=lambda ctx: "result_value")
        result = action.execute(ctx)
        assert result["last_query_result"] == "result_value"

    def test_query_with_context_access(self):
        """Test query function accessing context values."""
        ctx = ProcessContext({"filter": "active"})
        action = QueryAction(
            query_func=lambda ctx: f"filtered_{ctx['filter']}",
            result_field="data.result",
        )
        ctx = ProcessContext({"data": {}, "filter": "active"})
        result = action.execute(ctx)
        assert result["data"]["result"] == "filtered_active"


class TestFetchEntityActionDotNotation:
    """Test FetchEntityAction with dot notation support."""

    def test_fetch_simple_field(self):
        """Test backward compatibility - simple field without dots."""
        mock_repo = Mock()
        mock_repo.find_one.return_value = {"id": 1, "name": "Test"}

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal})
        spec = EqualsSpecification("id", 1)
        action = FetchEntityAction(
            repository_name="user_repository", specification=spec, entity="user"
        )
        result = action.execute(ctx)

        assert result["user"]["id"] == 1
        assert result["user"]["name"] == "Test"
        mock_repo.find_one.assert_called_once_with(spec)

    def test_fetch_nested_field(self):
        """Test storing fetched entity in nested field."""
        mock_repo = Mock()
        mock_repo.find_one.return_value = {"id": 1, "name": "Test"}

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal, "request": {}})
        spec = EqualsSpecification("id", 1)
        action = FetchEntityAction(
            repository_name="user_repository", specification=spec, entity="request.user"
        )
        result = action.execute(ctx)

        assert result["request"]["user"]["id"] == 1
        assert result["request"]["user"]["name"] == "Test"

    def test_fetch_deeply_nested_field(self):
        """Test storing fetched entity in deeply nested field."""
        mock_repo = Mock()
        mock_repo.find_one.return_value = {"id": 1, "profile": "data"}

        mock_context = Mock()
        mock_context.profile_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal, "request": {"data": {}}})
        spec = EqualsSpecification("user_id", 1)
        action = FetchEntityAction(
            repository_name="profile_repository",
            specification=spec,
            entity="request.data.profile",
        )
        result = action.execute(ctx)

        assert result["request"]["data"]["profile"]["id"] == 1


class TestFindEntitiesActionDotNotation:
    """Test FindEntitiesAction with dot notation support."""

    def test_find_simple_field(self):
        """Test backward compatibility - simple field without dots."""
        mock_repo = Mock()
        mock_repo.find.return_value = [{"id": 1}, {"id": 2}]

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal})
        spec = EqualsSpecification("status", "active")
        action = FindEntitiesAction(
            repository_name="user_repository", specification=spec, entities="users"
        )
        result = action.execute(ctx)

        assert len(result["users"]) == 2
        assert result["users"][0]["id"] == 1
        assert result["users"][1]["id"] == 2

    def test_find_nested_field(self):
        """Test storing found entities in nested field."""
        mock_repo = Mock()
        mock_repo.find.return_value = [{"id": 1}, {"id": 2}, {"id": 3}]

        mock_context = Mock()
        mock_context.user_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal, "data": {}})
        spec = EqualsSpecification("status", "active")
        action = FindEntitiesAction(
            repository_name="user_repository", specification=spec, entities="data.users"
        )
        result = action.execute(ctx)

        assert len(result["data"]["users"]) == 3

    def test_find_without_specification(self):
        """Test finding all entities without specification."""
        mock_repo = Mock()
        mock_repo.find.return_value = [{"id": 1}, {"id": 2}]

        mock_context = Mock()
        mock_context.item_repository = mock_repo

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal, "response": {}})
        action = FindEntitiesAction(
            repository_name="item_repository", entities="response.items"
        )
        result = action.execute(ctx)

        assert len(result["response"]["items"]) == 2
        mock_repo.find.assert_called_once_with(None)


class TestCommandActionDotNotation:
    """Test CommandAction with dot notation support."""

    def test_command_default_field(self):
        """Test backward compatibility - default result_field."""
        mock_command_bus = Mock()
        mock_command_bus.handle.return_value = {"success": True, "id": 123}

        mock_context = Mock()
        mock_context.command_bus = mock_command_bus

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal})
        mock_command = Mock()
        action = CommandAction(command_factory=lambda ctx: mock_command)
        result = action.execute(ctx)

        assert result["last_command_result"]["success"] is True
        assert result["last_command_result"]["id"] == 123

    def test_command_simple_field(self):
        """Test storing command result in custom simple field."""
        mock_command_bus = Mock()
        mock_command_bus.handle.return_value = {"success": True}

        mock_context = Mock()
        mock_context.command_bus = mock_command_bus

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal})
        mock_command = Mock()
        action = CommandAction(
            command_factory=lambda ctx: mock_command, result_field="result"
        )
        result = action.execute(ctx)

        assert result["result"]["success"] is True

    def test_command_nested_field(self):
        """Test storing command result in nested field."""
        mock_command_bus = Mock()
        mock_command_bus.handle.return_value = {"user_id": 456}

        mock_context = Mock()
        mock_context.command_bus = mock_command_bus

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        ctx = ProcessContext({"fractal": mock_fractal, "command": {}})
        mock_command = Mock()
        action = CommandAction(
            command_factory=lambda ctx: mock_command, result_field="command.result"
        )
        result = action.execute(ctx)

        assert result["command"]["result"]["user_id"] == 456

    def test_command_factory_uses_context(self):
        """Test command factory accessing context values."""
        mock_command_bus = Mock()
        mock_command_bus.handle.return_value = "ok"

        mock_context = Mock()
        mock_context.command_bus = mock_command_bus

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        mock_command_class = Mock()
        ctx = ProcessContext({"fractal": mock_fractal, "user_name": "Alice"})
        action = CommandAction(
            command_factory=lambda ctx: mock_command_class(name=ctx["user_name"]),
            result_field="data.result",
        )
        ctx = ProcessContext(
            {"fractal": mock_fractal, "data": {}, "user_name": "Alice"}
        )
        result = action.execute(ctx)

        mock_command_class.assert_called_once_with(name="Alice")


class TestCompleteWorkflow:
    """Test complete workflow combining multiple actions with dot notation."""

    def test_workflow_with_nested_structure(self):
        """Test multiple actions setting nested values in same Process."""
        # Setup mocks
        mock_repo = Mock()
        mock_repo.find.return_value = [{"id": 1}, {"id": 2}]
        mock_repo.find_one.return_value = {"id": 1, "name": "Primary"}

        mock_command_bus = Mock()
        mock_command_bus.handle.return_value = {"created_id": 999}

        mock_context = Mock()
        mock_context.user_repository = mock_repo
        mock_context.command_bus = mock_command_bus

        mock_fractal = Mock()
        mock_fractal.context = mock_context

        # Initialize context with nested structure
        ctx = ProcessContext(
            {
                "fractal": mock_fractal,
                "data": {},
                "request": {},
                "stats": {"views": 0},
            }
        )

        # Execute multiple actions
        # 1. Find entities into nested field
        action1 = FindEntitiesAction(
            repository_name="user_repository",
            entities="data.users",
        )
        ctx = action1.execute(ctx)

        # 2. Fetch entity into nested field
        action2 = FetchEntityAction(
            repository_name="user_repository",
            specification=EqualsSpecification("id", 1),
            entity="request.user",
        )
        ctx = action2.execute(ctx)

        # 3. Query into nested field
        action3 = QueryAction(
            query_func=lambda c: {"total": len(c["data"]["users"])},
            result_field="data.summary",
        )
        ctx = action3.execute(ctx)

        # 4. Increase nested counter
        action4 = IncreaseValueAction(field="stats.views", value=1)
        ctx = action4.execute(ctx)

        # 5. Command into nested field
        action5 = CommandAction(
            command_factory=lambda c: Mock(),
            result_field="request.command_result",
        )
        ctx = action5.execute(ctx)

        # Verify all nested structures created correctly
        assert len(ctx["data"]["users"]) == 2
        assert ctx["data"]["summary"]["total"] == 2
        assert ctx["request"]["user"]["id"] == 1
        assert ctx["request"]["user"]["name"] == "Primary"
        assert ctx["request"]["command_result"]["created_id"] == 999
        assert ctx["stats"]["views"] == 1

    def test_workflow_modifying_nested_fields(self):
        """Test applying transformations to nested fields."""
        ctx = ProcessContext(
            {
                "user": {"profile": {"views": 10, "likes": 5}},
                "stats": {"total": 100},
            }
        )

        # Apply transformation to nested dict
        action1 = ApplyToValueAction(
            field="user.profile",
            function=lambda p: {**p, "views": p["views"] + 1},
        )
        ctx = action1.execute(ctx)

        # Increase nested value
        action2 = IncreaseValueAction(field="stats.total", value=50)
        ctx = action2.execute(ctx)

        # Apply to deeply nested value
        action3 = ApplyToValueAction(
            field="user.profile.likes",
            function=lambda x: x * 2,
        )
        ctx = action3.execute(ctx)

        assert ctx["user"]["profile"]["views"] == 11
        assert ctx["user"]["profile"]["likes"] == 10
        assert ctx["stats"]["total"] == 150


# Async tests (only run if AsyncAction is available)
try:
    from fractal.core.process.actions import AsyncCommandAction, AsyncQueryAction

    class TestAsyncQueryActionDotNotation:
        """Test AsyncQueryAction with dot notation support."""

        @pytest.mark.asyncio
        async def test_async_query_simple_field(self):
            """Test backward compatibility - simple field without dots."""
            ctx = ProcessContext({})

            async def async_query(ctx):
                return [1, 2, 3]

            action = AsyncQueryAction(query_func=async_query, result_field="result")
            result = await action.execute_async(ctx)
            assert result["result"] == [1, 2, 3]

        @pytest.mark.asyncio
        async def test_async_query_nested_field(self):
            """Test storing async query result in nested field."""
            ctx = ProcessContext({"data": {}})

            async def async_query(ctx):
                return ["user1", "user2"]

            action = AsyncQueryAction(query_func=async_query, result_field="data.users")
            result = await action.execute_async(ctx)
            assert result["data"]["users"] == ["user1", "user2"]

        @pytest.mark.asyncio
        async def test_async_query_default_field(self):
            """Test using default result_field."""
            ctx = ProcessContext({})

            async def async_query(ctx):
                return "async_result"

            action = AsyncQueryAction(query_func=async_query)
            result = await action.execute_async(ctx)
            assert result["last_query_result"] == "async_result"

    class TestAsyncCommandActionDotNotation:
        """Test AsyncCommandAction with dot notation support."""

        @pytest.mark.asyncio
        async def test_async_command_default_field(self):
            """Test backward compatibility - default result_field."""
            mock_command_bus = Mock()
            mock_command_bus.handle_async = AsyncMock(
                return_value={"success": True, "id": 789}
            )

            mock_context = Mock()
            mock_context.command_bus = mock_command_bus

            mock_fractal = Mock()
            mock_fractal.context = mock_context

            ctx = ProcessContext({"fractal": mock_fractal})
            mock_command = Mock()
            action = AsyncCommandAction(command_factory=lambda ctx: mock_command)
            result = await action.execute_async(ctx)

            assert result["last_command_result"]["success"] is True
            assert result["last_command_result"]["id"] == 789

        @pytest.mark.asyncio
        async def test_async_command_nested_field(self):
            """Test storing async command result in nested field."""
            mock_command_bus = Mock()
            mock_command_bus.handle_async = AsyncMock(return_value={"user_id": 999})

            mock_context = Mock()
            mock_context.command_bus = mock_command_bus

            mock_fractal = Mock()
            mock_fractal.context = mock_context

            ctx = ProcessContext({"fractal": mock_fractal, "async": {}})
            mock_command = Mock()
            action = AsyncCommandAction(
                command_factory=lambda ctx: mock_command,
                result_field="async.command_result",
            )
            result = await action.execute_async(ctx)

            assert result["async"]["command_result"]["user_id"] == 999

except ImportError:
    # AsyncAction not available, skip async tests
    pass
