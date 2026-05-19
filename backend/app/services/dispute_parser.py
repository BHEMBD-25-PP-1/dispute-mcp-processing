import re
from typing import Iterable

from app.core.logger import logger


ORDER_ID_PATTERNS = (
    r"order[_\s-]?id\s*[:=]\s*([A-ZА-Я0-9-]+)",
    r"заказ[ау]?\s*(?:N|№|#)?\s*([A-ZА-Я0-9-]+)",
    r"\b(TAXI-\d{4,})\b",
    r"\b(AFISHA-\d{4,})\b",
)

TRANSACTION_ID_PATTERNS = (
    r"transaction[_\s-]?id\s*[:=]\s*([A-ZА-Я0-9-]+)",
    r"транзакци[ияю]\s*(?:N|№|#)?\s*([A-ZА-Я0-9-]+)",
    r"\b(TXN-\d{3,})\b",
)

USER_ID_PATTERNS = (
    r"user[_\s-]?id\s*[:=]\s*([A-ZА-Я0-9-]+)",
    r"клиент\s*(?:N|№|#)?\s*([A-ZА-Я0-9-]+)",
)

SERVICE_HINT_PATTERNS = (
    r"service\s*[:=]\s*(taxi|afisha)",
    r"сервис\s*[:=]?\s*(такси|taxi|афиша|afisha)",
)


def _pick(text: str, patterns: Iterable[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return None


def _normalize_service(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.lower()
    if normalized in {"taxi", "такси"}:
        return "taxi"
    if normalized in {"afisha", "афиша"}:
        return "afisha"
    return None


def parse_dispute(text: str):
    order_id = _pick(text, ORDER_ID_PATTERNS)
    transaction_id = _pick(text, TRANSACTION_ID_PATTERNS)
    user_id = _pick(text, USER_ID_PATTERNS)
    service_hint = _normalize_service(_pick(text, SERVICE_HINT_PATTERNS))

    logger.info(
        "Parsed dispute identifiers: order_id=%s transaction_id=%s user_id=%s service_hint=%s",
        order_id,
        transaction_id,
        user_id,
        service_hint,
    )

    return {
        "order_id": order_id,
        "transaction_id": transaction_id,
        "user_id": user_id,
        "service_hint": service_hint,
        "raw_text": text,
    }
