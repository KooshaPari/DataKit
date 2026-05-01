"""
Tests for pheno-events package.
"""

import asyncio
from datetime import datetime

import pytest
from pheno_events import (
    Event,
    EventBus,
    EventStore,
    SimpleEventBus,
    StoredEvent,
)
from pheno_events.webhooks.signature import WebhookReceiver, WebhookSigner


class TestEvent:
    """Tests for Event dataclass."""

    def test_event_creation(self):
        """Test basic event creation."""
        event = Event(name="test.event", data={"key": "value"})
        assert event.name == "test.event"
        assert event.data == {"key": "value"}
        assert event.timestamp is not None
        assert event.source is None
        assert event.correlation_id is None

    def test_event_with_timestamp(self):
        """Test event with custom timestamp."""
        ts = datetime(2024, 1, 1, 12, 0, 0)
        event = Event(name="test.event", data={}, timestamp=ts)
        assert event.timestamp == ts

    def test_event_with_metadata(self):
        """Test event with source and correlation_id."""
        event = Event(
            name="test.event",
            data={},
            source="test-service",
            correlation_id="corr-123",
        )
        assert event.source == "test-service"
        assert event.correlation_id == "corr-123"


class TestEventBus:
    """Tests for async EventBus."""

    @pytest.mark.asyncio
    async def test_publish_and_subscribe(self):
        """Test basic publish-subscribe pattern."""
        bus = EventBus()
        received_events = []

        async def handler(event):
            received_events.append(event)

        bus.subscribe("test.event", handler)  # subscribe is sync
        await bus.publish("test.event", {"data": "value"})

        # Allow async handlers to execute
        await asyncio.sleep(0.01)

        assert len(received_events) == 1
        assert received_events[0].name == "test.event"
        assert received_events[0].data == {"data": "value"}

    @pytest.mark.asyncio
    async def test_decorator_syntax(self):
        """Test decorator-based subscription."""
        bus = EventBus()
        received_events = []

        @bus.on("test.event")
        async def handler(event):
            received_events.append(event)

        await bus.publish("test.event", {"test": True})
        await asyncio.sleep(0.01)

        assert len(received_events) == 1

    @pytest.mark.asyncio
    async def test_wildcard_subscription(self):
        """Test wildcard event matching."""
        bus = EventBus()
        received_events = []

        @bus.on("user.*")
        async def handler(event):
            received_events.append(event)

        await bus.publish("user.created", {"id": 1})
        await bus.publish("user.updated", {"id": 1})
        await bus.publish("order.created", {"id": 1})  # Should not match
        await asyncio.sleep(0.01)

        assert len(received_events) == 2

    @pytest.mark.asyncio
    async def test_multiple_handlers(self):
        """Test multiple handlers for same event."""
        bus = EventBus()
        handler1_results = []
        handler2_results = []

        async def handler1(event):
            handler1_results.append(event)

        async def handler2(event):
            handler2_results.append(event)

        bus.subscribe("test.event", handler1)
        bus.subscribe("test.event", handler2)
        await bus.publish("test.event", {})

        await asyncio.sleep(0.01)

        assert len(handler1_results) == 1
        assert len(handler2_results) == 1

    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        """Test unsubscribe functionality."""
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe("test.event", handler)
        await bus.publish("test.event", {"count": 1})
        await asyncio.sleep(0.01)

        bus.unsubscribe("test.event", handler)
        await bus.publish("test.event", {"count": 2})
        await asyncio.sleep(0.01)

        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_unsubscribe_all(self):
        """Test unsubscribe all handlers for event."""
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe("test.event", handler)
        await bus.publish("test.event", {"count": 1})
        await asyncio.sleep(0.01)

        bus.unsubscribe("test.event")
        await bus.publish("test.event", {"count": 2})
        await asyncio.sleep(0.01)

        assert len(received) == 1

    def test_get_handlers(self):
        """Test getting handlers for event."""
        bus = EventBus()

        async def handler1(event):
            pass

        async def handler2(event):
            pass

        bus.subscribe("test.event", handler1)
        bus.subscribe("test.event", handler2)

        handlers = bus.get_handlers("test.event")
        assert len(handlers) == 2

    def test_clear_handlers(self):
        """Test clearing all handlers."""
        bus = EventBus()

        async def handler(event):
            pass

        bus.subscribe("test.event", handler)
        bus.clear()

        assert len(bus.get_handlers("test.event")) == 0


class TestSimpleEventBus:
    """Tests for synchronous SimpleEventBus."""

    def test_sync_publish_subscribe(self):
        """Test synchronous publish-subscribe."""
        bus = SimpleEventBus()
        received = []

        def handler(event):
            received.append(event)

        bus.subscribe("test.event", handler)
        bus.publish("test.event", {"sync": True})

        assert len(received) == 1
        assert received[0].name == "test.event"

    def test_sync_decorator(self):
        """Test decorator-based subscription."""
        bus = SimpleEventBus()
        received = []

        @bus.on("test.event")
        def handler(event):
            received.append(event)

        bus.publish("test.event", {})

        assert len(received) == 1

    def test_sync_multiple_handlers(self):
        """Test multiple synchronous handlers."""
        bus = SimpleEventBus()
        results = []

        def handler1(event):
            results.append("h1")

        def handler2(event):
            results.append("h2")

        bus.subscribe("test.event", handler1)
        bus.subscribe("test.event", handler2)
        bus.publish("test.event", {})

        assert len(results) == 2
        assert "h1" in results
        assert "h2" in results

    def test_sync_unsubscribe(self):
        """Test synchronous unsubscribe."""
        bus = SimpleEventBus()
        received = []

        def handler(event):
            received.append(event)

        bus.subscribe("test.event", handler)
        bus.publish("test.event", {"count": 1})
        bus.unsubscribe("test.event", handler)
        bus.publish("test.event", {"count": 2})

        assert len(received) == 1


class TestEventStore:
    """Tests for EventStore."""

    @pytest.mark.asyncio
    async def test_append_event(self):
        """Test appending events to store."""
        store = EventStore()

        event = await store.append(
            event_type="OrderPlaced",
            aggregate_id="order-123",
            aggregate_type="Order",
            data={"amount": 100},
        )

        assert event.event_type == "OrderPlaced"
        assert event.aggregate_id == "order-123"
        assert event.data == {"amount": 100}
        assert event.event_id is not None

    @pytest.mark.asyncio
    async def test_get_stream(self):
        """Test getting stream of events for aggregate."""
        store = EventStore()

        await store.append("OrderPlaced", "order-1", "Order", {"amount": 100})
        await store.append("OrderPaid", "order-1", "Order", {"paid": True})
        await store.append("OrderPlaced", "order-2", "Order", {"amount": 200})

        events = await store.get_stream("order-1")

        assert len(events) == 2
        assert events[0].event_type == "OrderPlaced"
        assert events[1].event_type == "OrderPaid"

    @pytest.mark.asyncio
    async def test_get_events_filtered(self):
        """Test filtering events by type."""
        store = EventStore()

        await store.append("OrderPlaced", "order-1", "Order", {})
        await store.append("OrderPaid", "order-1", "Order", {})
        await store.append("OrderPlaced", "order-2", "Order", {})

        events = await store.get_events(event_type="OrderPlaced")

        assert len(events) == 2

    @pytest.mark.asyncio
    async def test_get_events_by_aggregate_type(self):
        """Test filtering by aggregate type."""
        store = EventStore()

        await store.append("OrderPlaced", "order-1", "Order", {})
        await store.append("UserCreated", "user-1", "User", {})

        events = await store.get_events(aggregate_type="Order")

        assert len(events) == 1
        assert events[0].aggregate_type == "Order"

    @pytest.mark.asyncio
    async def test_replay(self):
        """Test replaying events with reducer."""
        store = EventStore()

        # Clear any pre-existing events
        await store.append("AmountAdded", "calc-1", "Calculator", {"amount": 10})
        await store.append("AmountAdded", "calc-1", "Calculator", {"amount": 20})
        await store.append("AmountAdded", "calc-1", "Calculator", {"amount": 30})

        def reducer(state, event):
            if state is None:
                return event.data.get("amount", 0)
            return state + event.data.get("amount", 0)

        result = await store.replay("calc-1", reducer)

        # 10 + 20 + 30 = 60
        assert result == 60

    @pytest.mark.asyncio
    async def test_stored_event_to_dict(self):
        """Test StoredEvent serialization."""
        event = StoredEvent(
            event_type="TestEvent",
            aggregate_id="agg-1",
            aggregate_type="Test",
            data={"key": "value"},
        )

        data = event.to_dict()

        assert data["event_type"] == "TestEvent"
        assert data["aggregate_id"] == "agg-1"
        assert data["data"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_stored_event_from_dict(self):
        """Test StoredEvent deserialization."""
        data = {
            "event_id": "evt-123",
            "event_type": "TestEvent",
            "aggregate_id": "agg-1",
            "aggregate_type": "Test",
            "data": {"key": "value"},
            "metadata": {"meta": True},
            "timestamp": "2024-01-01T00:00:00",
            "version": 1,
        }

        event = StoredEvent.from_dict(data)

        assert event.event_id == "evt-123"
        assert event.event_type == "TestEvent"
        assert event.data == {"key": "value"}


class TestWebhookSigner:
    """Tests for WebhookSigner."""

    def test_sign_payload(self):
        """Test signing a payload."""
        signer = WebhookSigner(secret="test-secret")
        payload = '{"event": "test"}'  # String, not bytes

        signature = signer.sign(payload)

        assert signature is not None
        assert len(signature) > 0
        assert signature.startswith("sha256=")

    def test_verify_valid_signature(self):
        """Test verifying a valid signature."""
        signer = WebhookSigner(secret="test-secret")
        payload = '{"event": "test"}'

        signature = signer.sign(payload)
        # verify is a static method that takes (payload, signature, secret)
        is_valid = WebhookSigner.verify(payload, signature, "test-secret")

        assert is_valid is True

    def test_verify_invalid_signature(self):
        """Test verifying an invalid signature."""
        payload = '{"event": "test"}'

        is_valid = WebhookSigner.verify(payload, "invalid-signature", "test-secret")

        assert is_valid is False

    def test_verify_tampered_payload(self):
        """Test verifying tampered payload."""
        signer = WebhookSigner(secret="test-secret")
        payload = '{"event": "test"}'

        signature = signer.sign(payload)
        tampered_payload = '{"event": "hacked"}'

        is_valid = WebhookSigner.verify(tampered_payload, signature, "test-secret")

        assert is_valid is False


class TestWebhookReceiver:
    """Tests for WebhookReceiver."""

    def test_validate_valid_webhook(self):
        """Test validating a valid webhook."""
        secret = "webhook-secret"
        receiver = WebhookReceiver(secret=secret)  # Takes string, not signer
        payload = '{"event": "test", "data": {"id": 1}}'

        signature = WebhookSigner(secret).sign(payload)
        is_valid = receiver.verify(payload, signature)

        assert is_valid is True

    def test_validate_missing_signature(self):
        """Test validation fails with missing signature."""
        receiver = WebhookReceiver(secret="secret")

        is_valid = receiver.verify('{"event": "test"}', "")

        assert is_valid is False
