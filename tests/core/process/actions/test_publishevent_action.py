"""Tests for PublishEventAction."""

from dataclasses import dataclass
from datetime import datetime, timezone

from fractal.core.process.actions import PublishEventAction
from fractal.core.process.process_context import ProcessContext


@dataclass
class MockEvent:
    """Mock domain event."""

    id: str
    data: dict
    timestamp: datetime


class MockEventPublisher:
    """Mock event publisher for testing."""

    def __init__(self):
        self.published_events = []

    def publish_event(self, event):
        self.published_events.append(event)


class MockApplicationContext:
    """Mock application context with event publisher."""

    def __init__(self):
        self.event_publisher = MockEventPublisher()


def test_publishevent_creates_and_publishes_event():
    """Test that PublishEventAction creates and publishes an event."""
    app_context = MockApplicationContext()

    ctx = ProcessContext(
        {
            "fractal.context": app_context,
            "entity_id": "123",
            "entity_data": {"name": "Test"},
        }
    )

    action = PublishEventAction(
        event_factory=lambda ctx: MockEvent(
            id=ctx["entity_id"],
            data=ctx["entity_data"],
            timestamp=datetime.now(timezone.utc),
        )
    )

    result = action.execute(ctx)

    # Event should be published
    assert len(app_context.event_publisher.published_events) == 1
    event = app_context.event_publisher.published_events[0]
    assert event.id == "123"
    assert event.data == {"name": "Test"}

    # Context unchanged (side effect action)
    assert result["entity_id"] == "123"


def test_publishevent_accesses_nested_context():
    """Test that event factory can access nested context data."""
    app_context = MockApplicationContext()

    @dataclass
    class MockCommand:
        entity_id: str
        user_id: str

    command = MockCommand(entity_id="456", user_id="user_789")

    ctx = ProcessContext({"fractal.context": app_context, "command": command})

    action = PublishEventAction(
        event_factory=lambda ctx: MockEvent(
            id=ctx.command.entity_id,
            data={"user_id": ctx.command.user_id},
            timestamp=datetime.now(timezone.utc),
        )
    )

    action.execute(ctx)

    event = app_context.event_publisher.published_events[0]
    assert event.id == "456"
    assert event.data["user_id"] == "user_789"


def test_publishevent_in_workflow():
    """Test PublishEventAction in a complete workflow."""
    from fractal.core.process.actions import SetContextVariableAction
    from fractal.core.process.process import Process

    app_context = MockApplicationContext()

    process = Process(
        [
            SetContextVariableAction(entity_id="123", entity_name="Test Entity"),
            PublishEventAction(
                event_factory=lambda ctx: MockEvent(
                    id=ctx["entity_id"],
                    data={"name": ctx["entity_name"]},
                    timestamp=datetime.now(timezone.utc),
                )
            ),
        ]
    )

    result = process.run(ProcessContext({"fractal.context": app_context}))

    # Verify event was published
    assert len(app_context.event_publisher.published_events) == 1
    event = app_context.event_publisher.published_events[0]
    assert event.id == "123"
    assert event.data["name"] == "Test Entity"


def test_publishevent_with_command_handler_pattern():
    """Test PublishEventAction in a command handler pattern."""
    from fractal_specifications.generic.specification import Specification

    from fractal.core.process.actions import CreateSpecificationAction, SetValueAction
    from fractal.core.process.actions.control_flow import IfElseAction
    from fractal.core.process.process import Process
    from fractal.core.process.specifications import on_field

    app_context = MockApplicationContext()

    @dataclass
    class Entity:
        id: str
        name: str
        created_by_id: str = None

    class NameNotEmptySpec(Specification):
        """Specification that checks if name is not empty."""

        def is_satisfied_by(self, entity):
            return len(entity.name) > 0

        def to_collection(self):
            return None

    @dataclass
    class AddEntityCommand:
        entity: Entity
        user_id: str

        def get_specification(self):
            """Mock specification."""
            return NameNotEmptySpec()

    entity = Entity(id="123", name="Valid Entity")
    command = AddEntityCommand(entity=entity, user_id="user_456")

    # Command handler workflow
    process = Process(
        [
            CreateSpecificationAction(
                specification_factory=lambda ctx: on_field(
                    "command.entity", ctx.command.get_specification()
                ),
                ctx_var="entity_spec",
            ),
            IfElseAction(
                specification="entity_spec",
                actions_true=[
                    # Set audit field
                    SetValueAction(
                        target="command.entity.created_by_id", source="command.user_id"
                    ),
                    # Publish event
                    PublishEventAction(
                        event_factory=lambda ctx: MockEvent(
                            id=ctx.command.entity.id,
                            data={
                                "name": ctx.command.entity.name,
                                "created_by": ctx.command.entity.created_by_id,
                            },
                            timestamp=datetime.now(timezone.utc),
                        )
                    ),
                ],
            ),
        ]
    )

    result = process.run(
        ProcessContext({"fractal.context": app_context, "command": command})
    )

    # Verify entity was updated
    assert entity.created_by_id == "user_456"

    # Verify event was published
    assert len(app_context.event_publisher.published_events) == 1
    event = app_context.event_publisher.published_events[0]
    assert event.id == "123"
    assert event.data["name"] == "Valid Entity"
    assert event.data["created_by"] == "user_456"


def test_publishevent_multiple_events():
    """Test publishing multiple events in sequence."""
    from fractal.core.process.process import Process

    app_context = MockApplicationContext()

    process = Process(
        [
            PublishEventAction(
                event_factory=lambda ctx: MockEvent(
                    id="event1", data={"step": 1}, timestamp=datetime.now(timezone.utc)
                )
            ),
            PublishEventAction(
                event_factory=lambda ctx: MockEvent(
                    id="event2", data={"step": 2}, timestamp=datetime.now(timezone.utc)
                )
            ),
            PublishEventAction(
                event_factory=lambda ctx: MockEvent(
                    id="event3", data={"step": 3}, timestamp=datetime.now(timezone.utc)
                )
            ),
        ]
    )

    process.run(ProcessContext({"fractal.context": app_context}))

    # All three events should be published
    assert len(app_context.event_publisher.published_events) == 3
    assert app_context.event_publisher.published_events[0].id == "event1"
    assert app_context.event_publisher.published_events[1].id == "event2"
    assert app_context.event_publisher.published_events[2].id == "event3"
