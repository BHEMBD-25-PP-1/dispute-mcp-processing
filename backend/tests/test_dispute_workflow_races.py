from types import SimpleNamespace

import pytest
from sqlalchemy.exc import IntegrityError

from app.services import dispute_workflow


class _FakeDb:
    def __init__(self):
        self.rolled_back = False

    async def rollback(self):
        self.rolled_back = True


def _integrity_error():
    return IntegrityError("insert dispute", {"idempotency_key": "idem"}, Exception("duplicate"))


@pytest.mark.asyncio
async def test_submit_dispute_recovers_integrity_race_as_replay(monkeypatch):
    db = _FakeDb()
    existing = SimpleNamespace(id="DSP-1")
    find_results = iter([None, existing])

    async def find_existing(db_arg, *, idempotency_key, request_hash):
        assert db_arg is db
        return next(find_results)

    async def create_dispute(*args, **kwargs):
        raise _integrity_error()

    async def record_replay(db_arg, *, dispute, request_hash, producer, correlation_id):
        assert db_arg is db
        assert dispute is existing
        return {"dispute_id": dispute.id, "replayed": True}

    monkeypatch.setattr(dispute_workflow, "find_existing_dispute", find_existing)
    monkeypatch.setattr(dispute_workflow, "create_dispute", create_dispute)
    monkeypatch.setattr(dispute_workflow, "_record_replay", record_replay)

    result = await dispute_workflow.submit_dispute(
        db,
        text="transaction_id=TXN-98765",
        idempotency_key="idem",
        producer="test",
        correlation_id="corr-1",
    )

    assert db.rolled_back is True
    assert result == {"dispute_id": "DSP-1", "replayed": True}


@pytest.mark.asyncio
async def test_submit_dispute_reraises_unresolved_integrity_error(monkeypatch):
    db = _FakeDb()

    async def find_existing(*args, **kwargs):
        return None

    async def create_dispute(*args, **kwargs):
        raise _integrity_error()

    monkeypatch.setattr(dispute_workflow, "find_existing_dispute", find_existing)
    monkeypatch.setattr(dispute_workflow, "create_dispute", create_dispute)

    with pytest.raises(IntegrityError):
        await dispute_workflow.submit_dispute(
            db,
            text="transaction_id=TXN-98765",
            idempotency_key="idem",
            producer="test",
            correlation_id="corr-1",
        )

    assert db.rolled_back is True
