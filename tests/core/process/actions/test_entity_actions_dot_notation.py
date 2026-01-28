"""Tests for entity actions with dot notation support."""

from dataclasses import dataclass

from fractal.core.process.actions import AddEntityAction, UpdateEntityAction
from fractal.core.process.process_context import ProcessContext


@dataclass
class MockEntity:
    id: str
    name: str


class MockRepository:
    def __init__(self):
        self.entities = []
        self.updated_entities = []

    def add(self, entity):
        self.entities.append(entity)

    def update(self, entity, upsert=False):
        self.updated_entities.append((entity, upsert))


class MockApplicationContext:
    def __init__(self):
        self.test_repository = MockRepository()


def test_add_entity_with_simple_key():
    """Test AddEntityAction with simple entity key."""
    app_context = MockApplicationContext()
    entity = MockEntity(id="123", name="Test")

    ctx = ProcessContext({"fractal.context": app_context, "entity": entity})

    action = AddEntityAction(repository_name="test_repository", ctx_var="entity")
    result = action.execute(ctx)

    assert len(app_context.test_repository.entities) == 1
    assert app_context.test_repository.entities[0] == entity


def test_add_entity_with_dot_notation():
    """Test AddEntityAction with dot notation entity key."""
    app_context = MockApplicationContext()
    entity = MockEntity(id="456", name="Nested Test")

    @dataclass
    class Command:
        entity: MockEntity
        user_id: str

    command = Command(entity=entity, user_id="user_789")

    ctx = ProcessContext({"fractal.context": app_context, "command": command})

    # Use dot notation to reference nested entity
    action = AddEntityAction(
        repository_name="test_repository", ctx_var="command.entity"
    )
    result = action.execute(ctx)

    assert len(app_context.test_repository.entities) == 1
    assert app_context.test_repository.entities[0] == entity
    assert app_context.test_repository.entities[0].id == "456"


def test_add_entity_with_deep_nesting():
    """Test AddEntityAction with deeply nested entity."""
    app_context = MockApplicationContext()
    entity = MockEntity(id="789", name="Deep Test")

    @dataclass
    class Payload:
        entity: MockEntity

    @dataclass
    class Request:
        payload: Payload

    request = Request(payload=Payload(entity=entity))

    ctx = ProcessContext({"fractal.context": app_context, "request": request})

    action = AddEntityAction(
        repository_name="test_repository", ctx_var="request.payload.entity"
    )
    result = action.execute(ctx)

    assert len(app_context.test_repository.entities) == 1
    assert app_context.test_repository.entities[0] == entity
    assert app_context.test_repository.entities[0].id == "789"


def test_update_entity_with_simple_key():
    """Test UpdateEntityAction with simple entity key."""
    app_context = MockApplicationContext()
    entity = MockEntity(id="123", name="Test")

    ctx = ProcessContext({"fractal.context": app_context, "entity": entity})

    action = UpdateEntityAction(repository_name="test_repository", ctx_var="entity")
    result = action.execute(ctx)

    assert len(app_context.test_repository.updated_entities) == 1
    assert app_context.test_repository.updated_entities[0][0] == entity
    assert app_context.test_repository.updated_entities[0][1] is False  # upsert=False


def test_update_entity_with_dot_notation():
    """Test UpdateEntityAction with dot notation entity key."""
    app_context = MockApplicationContext()
    entity = MockEntity(id="456", name="Nested Test")

    @dataclass
    class Command:
        entity: MockEntity
        user_id: str

    command = Command(entity=entity, user_id="user_789")

    ctx = ProcessContext({"fractal.context": app_context, "command": command})

    action = UpdateEntityAction(
        repository_name="test_repository", ctx_var="command.entity", upsert=True
    )
    result = action.execute(ctx)

    assert len(app_context.test_repository.updated_entities) == 1
    assert app_context.test_repository.updated_entities[0][0] == entity
    assert app_context.test_repository.updated_entities[0][1] is True  # upsert=True


def test_update_entity_with_deep_nesting():
    """Test UpdateEntityAction with deeply nested entity."""
    app_context = MockApplicationContext()
    entity = MockEntity(id="789", name="Deep Test")

    @dataclass
    class Payload:
        entity: MockEntity

    @dataclass
    class Request:
        payload: Payload

    request = Request(payload=Payload(entity=entity))

    ctx = ProcessContext({"fractal.context": app_context, "request": request})

    action = UpdateEntityAction(
        repository_name="test_repository", ctx_var="request.payload.entity"
    )
    result = action.execute(ctx)

    assert len(app_context.test_repository.updated_entities) == 1
    assert app_context.test_repository.updated_entities[0][0] == entity
    assert app_context.test_repository.updated_entities[0][0].id == "789"


def test_entity_actions_in_workflow():
    """Test entity actions with dot notation in a complete workflow."""
    from fractal.core.process.actions import SetValueAction
    from fractal.core.process.process import Process

    app_context = MockApplicationContext()
    entity = MockEntity(id="workflow_123", name="Workflow Test")

    @dataclass
    class Command:
        entity: MockEntity
        user_id: str
        status: str = None

    command = Command(entity=entity, user_id="user_456")

    process = Process(
        [
            # Set a field on the nested entity
            SetValueAction(target="command.status", source="command.user_id"),
            # Add using dot notation
            AddEntityAction(
                repository_name="test_repository", ctx_var="command.entity"
            ),
            # Update using dot notation
            UpdateEntityAction(
                repository_name="test_repository", ctx_var="command.entity", upsert=True
            ),
        ]
    )

    result = process.run(
        ProcessContext({"fractal.context": app_context, "command": command})
    )

    # Verify both add and update were called
    assert len(app_context.test_repository.entities) == 1
    assert len(app_context.test_repository.updated_entities) == 1
    assert command.status == "user_456"
