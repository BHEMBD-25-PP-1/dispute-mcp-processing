from datetime import datetime, timedelta, timezone

from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models.dispute import Dispute
from app.models.dispute_event import DisputeEvent
from app.services.dispute_errors import (
    DisputeConflictError,
    DisputeNotFoundError,
    InvalidDisputeTransitionError,
)
from app.services.dispute_state import can_transition, is_final_status
from app.services.event_security import sign_event


async def find_existing_dispute(
    db: AsyncSession,
    *,
    idempotency_key: str | None,
    request_hash: str,
) -> Dispute | None:
    if idempotency_key:
        result = await db.execute(
            select(Dispute).where(
                or_(
                    Dispute.idempotency_key == idempotency_key,
                    Dispute.request_hash == request_hash,
                )
            )
        )
    else:
        result = await db.execute(select(Dispute).where(Dispute.request_hash == request_hash))
    return result.scalar_one_or_none()


async def create_dispute(
    db: AsyncSession,
    *,
    raw_text: str,
    request_hash: str,
    idempotency_key: str | None,
    parsed: dict,
) -> Dispute:
    dispute = Dispute(
        raw_text=raw_text,
        request_hash=request_hash,
        idempotency_key=idempotency_key,
        status="accepted",
        service=parsed.get("service_hint") or "unknown",
        transaction_id=parsed.get("transaction_id"),
        order_id=parsed.get("order_id"),
        response={},
    )
    db.add(dispute)
    await db.flush()
    logger.info(
        "Dispute created: dispute_id=%s request_hash=%s order_id=%s transaction_id=%s",
        dispute.id,
        request_hash[:12],
        dispute.order_id,
        dispute.transaction_id,
    )
    return dispute


async def get_dispute(db: AsyncSession, dispute_id: str) -> Dispute:
    result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = result.scalar_one_or_none()
    if not dispute:
        raise DisputeNotFoundError(f"Dispute {dispute_id} not found")
    return dispute


async def append_event(
    db: AsyncSession,
    *,
    dispute_id: str,
    event_type: str,
    payload: dict,
    producer: str,
    correlation_id: str,
) -> DisputeEvent:
    dispute = await get_dispute(db, dispute_id)
    dispute.last_event_sequence += 1
    sequence = dispute.last_event_sequence
    signature = sign_event(
        dispute_id=dispute_id,
        sequence=sequence,
        event_type=event_type,
        payload=payload,
        producer=producer,
        correlation_id=correlation_id,
    )
    event = DisputeEvent(
        dispute_id=dispute_id,
        sequence=sequence,
        event_type=event_type,
        payload=payload,
        producer=producer,
        correlation_id=correlation_id,
        signature=signature,
    )
    db.add(event)
    await db.flush()
    logger.info(
        "Dispute event appended: dispute_id=%s sequence=%s event_type=%s producer=%s correlation_id=%s",
        dispute_id,
        sequence,
        event_type,
        producer,
        correlation_id,
    )
    return event


async def update_dispute_state(
    db: AsyncSession,
    dispute: Dispute,
    *,
    status: str,
    service: str,
    response: dict,
) -> Dispute:
    dispute.status = status
    dispute.service = service
    dispute.transaction_id = response.get("parsed", {}).get("transaction_id")
    dispute.order_id = response.get("parsed", {}).get("order_id")
    dispute.response = response
    dispute.version += 1
    await db.flush()
    logger.info(
        "Dispute state updated: dispute_id=%s status=%s service=%s version=%s",
        dispute.id,
        dispute.status,
        dispute.service,
        dispute.version,
    )
    return dispute


def _is_lock_active(dispute: Dispute, now: datetime) -> bool:
    if not dispute.locked_until:
        return False
    locked_until = dispute.locked_until
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)
    return locked_until > now


def _ensure_expected_version(dispute: Dispute, expected_version: int, *, action: str, operator_id: str) -> None:
    if dispute.version == expected_version:
        return

    logger.warning(
        "%s rejected by version conflict: dispute_id=%s operator_id=%s expected_version=%s current_version=%s",
        action,
        dispute.id,
        operator_id,
        expected_version,
        dispute.version,
    )
    raise DisputeConflictError("Версия диспута изменилась")


def _ensure_lock_available(dispute: Dispute, *, operator_id: str, now: datetime, action: str) -> None:
    if not (_is_lock_active(dispute, now) and dispute.assigned_to != operator_id):
        return

    logger.warning(
        "%s rejected by active lock: dispute_id=%s operator_id=%s assigned_to=%s locked_until=%s",
        action,
        dispute.id,
        operator_id,
        dispute.assigned_to,
        dispute.locked_until,
    )
    raise DisputeConflictError("Диспут уже взят другим оператором")


def _ensure_claimable(dispute: Dispute, *, operator_id: str) -> None:
    if not is_final_status(dispute.status):
        return

    logger.warning(
        "Claim rejected for final dispute: dispute_id=%s operator_id=%s status=%s",
        dispute.id,
        operator_id,
        dispute.status,
    )
    raise InvalidDisputeTransitionError("Завершенный диспут нельзя взять в работу")


def _ensure_transition_allowed(dispute: Dispute, *, operator_id: str, new_status: str) -> None:
    if can_transition(dispute.status, new_status):
        return

    logger.warning(
        "Status update rejected by transition guard: dispute_id=%s operator_id=%s from_status=%s to_status=%s",
        dispute.id,
        operator_id,
        dispute.status,
        new_status,
    )
    raise InvalidDisputeTransitionError(f"Переход {dispute.status} -> {new_status} запрещен")


def _ensure_update_won_race(rowcount: int, *, action: str, dispute_id: str, operator_id: str, expected_version: int) -> None:
    if rowcount == 1:
        return

    logger.warning(
        "%s lost race: dispute_id=%s operator_id=%s expected_version=%s",
        action,
        dispute_id,
        operator_id,
        expected_version,
    )
    raise DisputeConflictError("Версия диспута изменилась")


async def claim_dispute(
    db: AsyncSession,
    *,
    dispute_id: str,
    operator_id: str,
    expected_version: int,
    correlation_id: str,
    lock_minutes: int = 15,
) -> Dispute:
    now = datetime.now(timezone.utc)
    dispute = await get_dispute(db, dispute_id)
    logger.info(
        "Claim attempt: dispute_id=%s operator_id=%s expected_version=%s current_version=%s status=%s",
        dispute_id,
        operator_id,
        expected_version,
        dispute.version,
        dispute.status,
    )
    _ensure_expected_version(dispute, expected_version, action="Claim", operator_id=operator_id)
    _ensure_claimable(dispute, operator_id=operator_id)
    _ensure_lock_available(dispute, operator_id=operator_id, now=now, action="Claim")

    locked_until = now + timedelta(minutes=lock_minutes)
    result = await db.execute(
        update(Dispute)
        .where(Dispute.id == dispute_id, Dispute.version == expected_version)
        .values(
            assigned_to=operator_id,
            locked_until=locked_until,
            version=Dispute.version + 1,
        )
    )
    _ensure_update_won_race(
        result.rowcount,
        action="Claim update",
        dispute_id=dispute_id,
        operator_id=operator_id,
        expected_version=expected_version,
    )

    await db.flush()
    dispute = await get_dispute(db, dispute_id)
    await append_event(
        db,
        dispute_id=dispute.id,
        event_type="dispute.claimed",
        payload={
            "assigned_to": operator_id,
            "locked_until": locked_until.isoformat(),
            "version": dispute.version,
        },
        producer=f"user:{operator_id}",
        correlation_id=correlation_id,
    )
    await db.commit()
    await db.refresh(dispute)
    logger.info(
        "Dispute claimed: dispute_id=%s operator_id=%s version=%s locked_until=%s correlation_id=%s",
        dispute.id,
        operator_id,
        dispute.version,
        dispute.locked_until,
        correlation_id,
    )
    return dispute


async def change_dispute_status(
    db: AsyncSession,
    *,
    dispute_id: str,
    operator_id: str,
    new_status: str,
    expected_version: int,
    correlation_id: str,
) -> Dispute:
    now = datetime.now(timezone.utc)
    dispute = await get_dispute(db, dispute_id)
    logger.info(
        "Status update attempt: dispute_id=%s operator_id=%s from_status=%s to_status=%s expected_version=%s current_version=%s",
        dispute_id,
        operator_id,
        dispute.status,
        new_status,
        expected_version,
        dispute.version,
    )
    _ensure_expected_version(dispute, expected_version, action="Status update", operator_id=operator_id)
    _ensure_lock_available(dispute, operator_id=operator_id, now=now, action="Status update")
    _ensure_transition_allowed(dispute, operator_id=operator_id, new_status=new_status)

    result = await db.execute(
        update(Dispute)
        .where(Dispute.id == dispute_id, Dispute.version == expected_version)
        .values(status=new_status, version=Dispute.version + 1)
    )
    _ensure_update_won_race(
        result.rowcount,
        action="Status update",
        dispute_id=dispute_id,
        operator_id=operator_id,
        expected_version=expected_version,
    )

    await db.flush()
    dispute = await get_dispute(db, dispute_id)
    await append_event(
        db,
        dispute_id=dispute.id,
        event_type="dispute.status_changed",
        payload={"status": new_status, "version": dispute.version},
        producer=f"user:{operator_id}",
        correlation_id=correlation_id,
    )
    await db.commit()
    await db.refresh(dispute)
    logger.info(
        "Dispute status changed: dispute_id=%s operator_id=%s status=%s version=%s correlation_id=%s",
        dispute.id,
        operator_id,
        dispute.status,
        dispute.version,
        correlation_id,
    )
    return dispute
