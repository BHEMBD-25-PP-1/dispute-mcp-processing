from datetime import datetime, timezone

import pytest

from app.models.dispute_event import DisputeEvent
from app.services import event_publisher


@pytest.mark.asyncio
async def test_publish_dispute_event_skips_when_kafka_disabled(monkeypatch):
    monkeypatch.setattr(event_publisher.settings, "kafka_enabled", False)

    async def fail_if_called():
        raise AssertionError("Kafka producer should not be created")

    monkeypatch.setattr(event_publisher, "_get_producer", fail_if_called)

    await event_publisher.publish_dispute_event(
        DisputeEvent(
            id="evt-1",
            dispute_id="DSP-1",
            sequence=1,
            event_type="dispute.accepted",
            payload={"status": "accepted"},
            producer="test",
            correlation_id="corr-1",
            signature="sig",
        )
    )


@pytest.mark.asyncio
async def test_publish_dispute_event_sends_serialized_payload(monkeypatch):
    sent = {}

    class FakeProducer:
        async def send_and_wait(self, topic, *, key, value):
            sent["topic"] = topic
            sent["key"] = key
            sent["value"] = value

    monkeypatch.setattr(event_publisher.settings, "kafka_enabled", True)
    monkeypatch.setattr(event_publisher.settings, "kafka_events_topic", "dispute-events")

    async def get_fake_producer():
        return FakeProducer()

    monkeypatch.setattr(event_publisher, "_get_producer", get_fake_producer)

    event = DisputeEvent(
        id="evt-1",
        dispute_id="DSP-1",
        sequence=7,
        event_type="dispute.resolved",
        payload={"status": "resolved"},
        producer="test",
        correlation_id="corr-1",
        signature="sig",
    )
    event.createdAt = datetime(2026, 1, 1, tzinfo=timezone.utc)

    await event_publisher.publish_dispute_event(event)

    assert sent["topic"] == "dispute-events"
    assert sent["key"] == "DSP-1"
    assert sent["value"]["sequence"] == 7
    assert sent["value"]["event_type"] == "dispute.resolved"
    assert sent["value"]["signature"] == "sig"
