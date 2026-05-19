import json
from typing import Any

from aiokafka import AIOKafkaProducer

from app.core.config import settings
from app.core.logger import logger
from app.models.dispute_event import DisputeEvent

_producer: AIOKafkaProducer | None = None


def _event_payload(event: DisputeEvent) -> dict[str, Any]:
    return {
        "event_id": event.id,
        "dispute_id": event.dispute_id,
        "sequence": event.sequence,
        "event_type": event.event_type,
        "payload": event.payload,
        "producer": event.producer,
        "correlation_id": event.correlation_id,
        "signature": event.signature,
        "created_at": event.createdAt.isoformat() if event.createdAt else None,
    }


async def _get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda value: json.dumps(value, ensure_ascii=False).encode("utf-8"),
            key_serializer=lambda value: value.encode("utf-8"),
        )
        await _producer.start()
        logger.info(
            "Kafka producer started: bootstrap_servers=%s topic=%s",
            settings.kafka_bootstrap_servers,
            settings.kafka_events_topic,
        )
    return _producer


async def publish_dispute_event(event: DisputeEvent) -> None:
    if not settings.kafka_enabled:
        return

    producer = await _get_producer()
    await producer.send_and_wait(
        settings.kafka_events_topic,
        key=event.dispute_id,
        value=_event_payload(event),
    )
    logger.info(
        "Kafka event published: topic=%s dispute_id=%s sequence=%s event_type=%s correlation_id=%s",
        settings.kafka_events_topic,
        event.dispute_id,
        event.sequence,
        event.event_type,
        event.correlation_id,
    )


async def close_kafka_producer() -> None:
    global _producer
    if _producer is None:
        return

    await _producer.stop()
    _producer = None
    logger.info("Kafka producer stopped")
