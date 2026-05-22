from types import SimpleNamespace

import pytest

from app.services import dispute_repository


@pytest.mark.asyncio
async def test_publish_events_logs_and_continues_after_publish_error(monkeypatch):
    async def fail_publish(event):
        raise RuntimeError("kafka down")

    monkeypatch.setattr(dispute_repository, "publish_dispute_event", fail_publish)

    await dispute_repository.publish_events(
        [
            SimpleNamespace(
                dispute_id="DSP-1",
                sequence=1,
                event_type="dispute.accepted",
            )
        ]
    )
