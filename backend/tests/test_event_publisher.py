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


@pytest.mark.asyncio
async def test_get_producer_starts_reuses_and_closes(monkeypatch):
    instances = []

    class FakeProducer:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.started = False
            self.stopped = False
            instances.append(self)

        async def start(self):
            self.started = True

        async def stop(self):
            self.stopped = True

    monkeypatch.setattr(event_publisher, "_producer", None)
    monkeypatch.setattr(event_publisher, "AIOKafkaProducer", FakeProducer)

    await event_publisher.close_kafka_producer()
    producer = await event_publisher._get_producer()
    reused = await event_publisher._get_producer()

    assert producer is reused
    assert producer.started is True
    assert len(instances) == 1
    assert producer.kwargs["key_serializer"]("DSP-1") == b"DSP-1"
    assert producer.kwargs["value_serializer"]({"text": "привет"}) == '{"text": "привет"}'.encode("utf-8")

    await event_publisher.close_kafka_producer()

    assert producer.stopped is True
    assert event_publisher._producer is None
