import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.base import Base
from app.models.dispute import Dispute
from app.models.dispute_event import DisputeEvent
from app.models.user import User  # noqa: F401
from app.services.dispute_errors import (
    DisputeConflictError,
    DisputeNotFoundError,
    InvalidDisputeTransitionError,
)
from app.services.dispute_repository import (
    _ensure_update_won_race,
    change_dispute_status,
    claim_dispute,
    get_dispute,
)
from app.services.dispute_workflow import submit_dispute


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        yield db

    await engine.dispose()


@pytest.mark.asyncio
async def test_submit_dispute_is_idempotent_by_key(session):
    first = await submit_dispute(
        session,
        text="transaction_id=TXN-98765, order_id=TAXI-240518 проблема такси",
        idempotency_key="idem-1",
        producer="test",
        correlation_id="corr-1",
    )
    second = await submit_dispute(
        session,
        text="transaction_id=TXN-98765, order_id=TAXI-240518 проблема такси",
        idempotency_key="idem-1",
        producer="test",
        correlation_id="corr-2",
    )

    disputes = (await session.execute(select(Dispute))).scalars().all()
    events = (await session.execute(select(DisputeEvent))).scalars().all()

    assert first["dispute_id"] == second["dispute_id"]
    assert second["replayed"] is True
    assert len(disputes) == 1
    assert [event.event_type for event in events] == [
        "dispute.accepted",
        "dispute.processing_started",
        "dispute.resolved",
        "dispute.replayed",
    ]
    assert [event.sequence for event in events] == [1, 2, 3, 4]
    assert all(event.signature for event in events)


@pytest.mark.asyncio
async def test_submit_dispute_is_idempotent_by_request_hash(session):
    first = await submit_dispute(
        session,
        text="Клиент оспаривает списание, деталей нет",
        idempotency_key=None,
        producer="test",
        correlation_id="corr-1",
    )
    second = await submit_dispute(
        session,
        text="  Клиент   оспаривает списание, деталей нет  ",
        idempotency_key=None,
        producer="test",
        correlation_id="corr-2",
    )

    disputes = (await session.execute(select(Dispute))).scalars().all()

    assert first["dispute_id"] == second["dispute_id"]
    assert first["status"] == "attention"
    assert second["replayed"] is True
    assert len(disputes) == 1


@pytest.mark.asyncio
async def test_claim_dispute_uses_optimistic_lock(session):
    result = await submit_dispute(
        session,
        text="Клиент оспаривает списание, деталей нет",
        idempotency_key="claim-1",
        producer="test",
        correlation_id="corr-1",
    )

    claimed = await claim_dispute(
        session,
        dispute_id=result["dispute_id"],
        operator_id="operator-1",
        expected_version=result["version"],
        correlation_id="corr-2",
    )

    assert claimed.assigned_to == "operator-1"
    assert claimed.version == result["version"] + 1

    with pytest.raises(DisputeConflictError):
        await claim_dispute(
            session,
            dispute_id=result["dispute_id"],
            operator_id="operator-2",
            expected_version=result["version"],
            correlation_id="corr-3",
        )


@pytest.mark.asyncio
async def test_status_update_requires_current_version_and_allowed_transition(session):
    result = await submit_dispute(
        session,
        text="Клиент оспаривает списание, деталей нет",
        idempotency_key="status-1",
        producer="test",
        correlation_id="corr-1",
    )
    claimed = await claim_dispute(
        session,
        dispute_id=result["dispute_id"],
        operator_id="operator-1",
        expected_version=result["version"],
        correlation_id="corr-2",
    )
    claimed_version = claimed.version
    updated = await change_dispute_status(
        session,
        dispute_id=result["dispute_id"],
        operator_id="operator-1",
        new_status="processing",
        expected_version=claimed_version,
        correlation_id="corr-3",
    )

    assert updated.status == "processing"
    assert updated.version == claimed_version + 1

    with pytest.raises(DisputeConflictError):
        await change_dispute_status(
            session,
            dispute_id=result["dispute_id"],
            operator_id="operator-1",
            new_status="resolved",
            expected_version=claimed_version,
            correlation_id="corr-4",
        )

    with pytest.raises(InvalidDisputeTransitionError):
        await change_dispute_status(
            session,
            dispute_id=result["dispute_id"],
            operator_id="operator-1",
            new_status="accepted",
            expected_version=updated.version,
            correlation_id="corr-5",
        )


@pytest.mark.asyncio
async def test_repository_reports_missing_disputes(session):
    with pytest.raises(DisputeNotFoundError, match="missing-id"):
        await get_dispute(session, "missing-id")


@pytest.mark.asyncio
async def test_claim_dispute_rejects_active_lock_for_other_operator(session):
    result = await submit_dispute(
        session,
        text="Клиент оспаривает списание, деталей нет",
        idempotency_key="lock-1",
        producer="test",
        correlation_id="corr-1",
    )
    claimed = await claim_dispute(
        session,
        dispute_id=result["dispute_id"],
        operator_id="operator-1",
        expected_version=result["version"],
        correlation_id="corr-2",
    )

    with pytest.raises(DisputeConflictError):
        await claim_dispute(
            session,
            dispute_id=result["dispute_id"],
            operator_id="operator-2",
            expected_version=claimed.version,
            correlation_id="corr-3",
        )


@pytest.mark.asyncio
async def test_claim_dispute_rejects_final_dispute(session):
    result = await submit_dispute(
        session,
        text="transaction_id=TXN-98765, order_id=TAXI-240518 проблема такси",
        idempotency_key="final-1",
        producer="test",
        correlation_id="corr-1",
    )

    with pytest.raises(InvalidDisputeTransitionError):
        await claim_dispute(
            session,
            dispute_id=result["dispute_id"],
            operator_id="operator-1",
            expected_version=result["version"],
            correlation_id="corr-2",
        )


def test_update_race_guard_raises_conflict():
    with pytest.raises(DisputeConflictError):
        _ensure_update_won_race(
            0,
            action="Status update",
            dispute_id="DSP-1",
            operator_id="operator-1",
            expected_version=7,
        )
