from app.core.logger import logger
from app.services.dispute_parser import parse_dispute
from app.services.mcp_dispatcher import dispatch
from app.services.service_classifier import detect_service


def _build_operator_answer(parsed: dict, nlu: dict, mcp_data: dict) -> str:
    service = nlu.get("service")
    order_id = parsed.get("order_id") or "не определен"
    transaction_id = parsed.get("transaction_id") or "не определена"

    if service == "unknown":
        return (
            "Требуется ручная проверка: по тексту обращения не удалось надежно "
            f"определить сервис для заказа {order_id} и транзакции {transaction_id}."
        )

    if mcp_data.get("status") == "not_found":
        return (
            f"Требуется ручная проверка: {service} не нашел данные по заказу "
            f"{order_id} или транзакции {transaction_id}."
        )

    if service == "taxi":
        return (
            f"Транзакция {transaction_id} подтверждена. Поездка по заказу {order_id} "
            "не состоялась, списание подлежит возврату клиенту."
        )

    if service == "afisha":
        return (
            f"Транзакция {transaction_id} подтверждена. Билет по заказу {order_id} "
            "не был активирован, списание подлежит возврату клиенту."
        )

    return "Требуется ручная проверка: нет правила для формирования итогового ответа."


def _resolve_status(nlu: dict, mcp_data: dict) -> str:
    if nlu.get("service") == "unknown" or mcp_data.get("status") != "found":
        return "attention"
    return "resolved"


def process_dispute(text: str, parsed: dict | None = None):
    logger.info("Starting dispute processing pipeline")
    parsed = parsed or parse_dispute(text)
    nlu = detect_service(text, parsed.get("service_hint")) or {}
    service = nlu.get("service")
    mcp_data = dispatch(service, parsed)
    status = _resolve_status(nlu, mcp_data)
    logger.info(
        "Dispute decision prepared: status=%s service=%s service_source=%s mcp_status=%s order_id=%s transaction_id=%s",
        status,
        service,
        nlu.get("source"),
        mcp_data.get("status"),
        parsed.get("order_id"),
        parsed.get("transaction_id"),
    )

    return {
        "status": status,
        "parsed": parsed,
        "nlu": nlu,
        "mcp": mcp_data,
        "result": _build_operator_answer(parsed, nlu, mcp_data),
    }
