import hmac
import json
from hashlib import sha256

from app.core.config import settings


def canonical_event_payload(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sign_event(
    *,
    dispute_id: str,
    sequence: int,
    event_type: str,
    payload: dict,
    producer: str,
    correlation_id: str,
) -> str:
    message = "|".join(
        [
            dispute_id,
            str(sequence),
            event_type,
            producer,
            correlation_id,
            canonical_event_payload(payload),
        ]
    )
    return hmac.new(
        settings.event_signature_secret.encode("utf-8"),
        message.encode("utf-8"),
        sha256,
    ).hexdigest()


def verify_event_signature(
    *,
    dispute_id: str,
    sequence: int,
    event_type: str,
    payload: dict,
    producer: str,
    correlation_id: str,
    signature: str,
) -> bool:
    expected = sign_event(
        dispute_id=dispute_id,
        sequence=sequence,
        event_type=event_type,
        payload=payload,
        producer=producer,
        correlation_id=correlation_id,
    )
    return hmac.compare_digest(expected, signature)
