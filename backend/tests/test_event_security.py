from app.services.event_security import sign_event, verify_event_signature


def test_event_signature_verification():
    signature = sign_event(
        dispute_id="DSP-1",
        sequence=1,
        event_type="dispute.accepted",
        payload={"status": "accepted"},
        producer="test",
        correlation_id="corr-1",
    )

    assert verify_event_signature(
        dispute_id="DSP-1",
        sequence=1,
        event_type="dispute.accepted",
        payload={"status": "accepted"},
        producer="test",
        correlation_id="corr-1",
        signature=signature,
    )


def test_event_signature_rejects_tampering():
    signature = sign_event(
        dispute_id="DSP-1",
        sequence=1,
        event_type="dispute.accepted",
        payload={"status": "accepted"},
        producer="test",
        correlation_id="corr-1",
    )

    assert not verify_event_signature(
        dispute_id="DSP-1",
        sequence=1,
        event_type="dispute.accepted",
        payload={"status": "resolved"},
        producer="test",
        correlation_id="corr-1",
        signature=signature,
    )
