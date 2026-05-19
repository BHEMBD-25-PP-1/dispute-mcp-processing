from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.logger import logger
from app.models.dispute import Dispute
from app.services.dispute_parser import parse_dispute
from app.services.dispute_processor import process_dispute
from app.services.dispute_repository import (
    append_event,
    create_dispute,
    find_existing_dispute,
    update_dispute_state,
)
from app.services.idempotency import build_request_hash


def build_process_response(dispute: Dispute, *, replayed: bool = False) -> dict:
    response = dispute.response or {}
    return {
        "dispute_id": dispute.id,
        "idempotency_key": dispute.idempotency_key,
        "replayed": replayed,
        "version": dispute.version,
        "assigned_to": dispute.assigned_to,
        "locked_until": dispute.locked_until,
        "status": dispute.status,
        "parsed": response.get("parsed", {}),
        "nlu": response.get("nlu", {}),
        "mcp": response.get("mcp", {}),
        "result": response.get("result", ""),
    }


async def _record_replay(
    db: AsyncSession,
    *,
    dispute: Dispute,
    request_hash: str,
    producer: str,
    correlation_id: str,
) -> dict:
    logger.info(
        "Recording idempotent replay: dispute_id=%s request_hash=%s correlation_id=%s producer=%s",
        dispute.id,
        request_hash[:12],
        correlation_id,
        producer,
    )
    await append_event(
        db,
        dispute_id=dispute.id,
        event_type="dispute.replayed",
        payload={"request_hash": request_hash},
        producer=producer,
        correlation_id=correlation_id,
    )
    await db.commit()
    await db.refresh(dispute)
    return build_process_response(dispute, replayed=True)


async def submit_dispute(
    db: AsyncSession,
    *,
    text: str,
    idempotency_key: str | None,
    producer: str,
    correlation_id: str,
) -> dict:
    request_hash = build_request_hash(text)
    logger.info(
        "Submitting dispute: request_hash=%s idempotency_key_present=%s correlation_id=%s producer=%s",
        request_hash[:12],
        bool(idempotency_key),
        correlation_id,
        producer,
    )
    existing = await find_existing_dispute(
        db,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
    )
    if existing:
        logger.info(
            "Existing dispute found before insert: dispute_id=%s status=%s version=%s correlation_id=%s",
            existing.id,
            existing.status,
            existing.version,
            correlation_id,
        )
        return await _record_replay(
            db,
            dispute=existing,
            request_hash=request_hash,
            producer=producer,
            correlation_id=correlation_id,
        )

    parsed = parse_dispute(text)
    try:
        dispute = await create_dispute(
            db,
            raw_text=text,
            request_hash=request_hash,
            idempotency_key=idempotency_key,
            parsed=parsed,
        )
    except IntegrityError:
        logger.warning(
            "Idempotency race detected on dispute insert: request_hash=%s correlation_id=%s",
            request_hash[:12],
            correlation_id,
        )
        await db.rollback()
        existing = await find_existing_dispute(
            db,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
        )
        if not existing:
            logger.exception(
                "IntegrityError could not be resolved as idempotent replay: request_hash=%s correlation_id=%s",
                request_hash[:12],
                correlation_id,
            )
            raise
        return await _record_replay(
            db,
            dispute=existing,
            request_hash=request_hash,
            producer=producer,
            correlation_id=correlation_id,
        )
    await append_event(
        db,
        dispute_id=dispute.id,
        event_type="dispute.accepted",
        payload={"request_hash": request_hash, "parsed": parsed},
        producer=producer,
        correlation_id=correlation_id,
    )
    await append_event(
        db,
        dispute_id=dispute.id,
        event_type="dispute.processing_started",
        payload={},
        producer="dispute-api",
        correlation_id=correlation_id,
    )

    response = process_dispute(text, parsed=parsed)
    logger.info(
        "Dispute processing completed: dispute_id=%s status=%s service=%s correlation_id=%s",
        dispute.id,
        response["status"],
        response.get("nlu", {}).get("service", "unknown"),
        correlation_id,
    )
    await update_dispute_state(
        db,
        dispute,
        status=response["status"],
        service=response.get("nlu", {}).get("service", "unknown"),
        response=response,
    )
    await append_event(
        db,
        dispute_id=dispute.id,
        event_type=f"dispute.{response['status']}",
        payload=response,
        producer="dispute-api",
        correlation_id=correlation_id,
    )
    await db.commit()
    await db.refresh(dispute)
    logger.info(
        "Dispute persisted: dispute_id=%s status=%s version=%s last_event_sequence=%s correlation_id=%s",
        dispute.id,
        dispute.status,
        dispute.version,
        dispute.last_event_sequence,
        correlation_id,
    )
    return build_process_response(dispute)
