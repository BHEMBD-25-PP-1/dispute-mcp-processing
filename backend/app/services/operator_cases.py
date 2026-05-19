from copy import deepcopy
from datetime import datetime
from typing import Any

from app.services.dispute_parser import parse_dispute
from app.services.dispute_processor import process_dispute
from app.services.mcp_dispatcher import dispatch
from app.services.service_classifier import detect_service


def _format_now() -> str:
    return datetime.now().strftime("%H:%M")


def _connectors() -> list[dict[str, Any]]:
    return [
        {
            "id": "taxi",
            "name": "MCP Такси",
            "service": "taxi",
            "status": "ready",
            "sla": "00:28",
            "confidence": 0,
            "fields": [
                {"label": "Маршрут", "value": "ожидает запроса"},
                {"label": "Статус поездки", "value": "ожидает запроса"},
                {"label": "Оплата", "value": "ожидает запроса"},
            ],
        },
        {
            "id": "afisha",
            "name": "MCP Афиша",
            "service": "afisha",
            "status": "ready",
            "sla": "00:33",
            "confidence": 0,
            "fields": [
                {"label": "Событие", "value": "ожидает запроса"},
                {"label": "Статус билета", "value": "ожидает запроса"},
                {"label": "Возврат", "value": "ожидает запроса"},
            ],
        },
    ]


def _empty_identifiers() -> dict[str, Any]:
    return {"service": "unknown", "confidence": 0}


def _base_timeline() -> list[dict[str, Any]]:
    return [
        {
            "id": "evt-1",
            "title": "Сообщение принято",
            "detail": "Кейс создан из входящего обращения НСПК",
            "time": "09:41",
            "status": "info",
        }
    ]


_CASES: list[dict[str, Any]] = [
    {
        "id": "DSP-1042",
        "title": "Списание за несостоявшуюся поездку",
        "partner": "НСПК",
        "channel": "HTTP",
        "priority": "P1",
        "status": "new",
        "receivedAt": "09:41",
        "amount": "1 280 ₽",
        "customerName": "Ирина С.",
        "message": (
            "От НСПК поступил диспут: transaction_id=TXN-98765, order_id=TAXI-240518. "
            "Клиент сообщает, что поездка не состоялась, но оплата списана."
        ),
        "identifiers": {
            "orderId": "TAXI-240518",
            "transactionId": "TXN-98765",
            "service": "taxi",
            "confidence": 96,
        },
        "connectors": _connectors(),
        "timeline": _base_timeline(),
        "result": "",
    },
    {
        "id": "DSP-1041",
        "title": "Билет не активирован",
        "partner": "НСПК",
        "channel": "HTTP",
        "priority": "P2",
        "status": "processing",
        "receivedAt": "09:18",
        "amount": "3 600 ₽",
        "customerName": "Максим К.",
        "message": (
            "Диспут по транзакции TXN-77210. Заказ AFISHA-8891, сервис Афиша. "
            "Клиент оплатил билет, QR не был использован."
        ),
        "identifiers": {
            "orderId": "AFISHA-8891",
            "transactionId": "TXN-77210",
            "service": "afisha",
            "confidence": 88,
        },
        "connectors": _connectors(),
        "timeline": [
            *_base_timeline(),
            {
                "id": "evt-2",
                "title": "Афиша ответила",
                "detail": "Билет найден и не был активирован",
                "time": "09:20",
                "status": "success",
            },
        ],
        "result": "",
    },
    {
        "id": "DSP-1039",
        "title": "Не хватает идентификаторов",
        "partner": "НСПК",
        "channel": "HTTP",
        "priority": "P2",
        "status": "attention",
        "receivedAt": "08:56",
        "amount": "не определена",
        "customerName": "Клиент",
        "message": "Клиент оспаривает списание, сервис не указан. Нужна ручная проверка.",
        "identifiers": _empty_identifiers(),
        "connectors": _connectors(),
        "timeline": [
            *_base_timeline(),
            {
                "id": "evt-2",
                "title": "Низкая уверенность",
                "detail": "Парсер не нашел order_id и service",
                "time": "08:57",
                "status": "warning",
            },
        ],
        "result": "Требуется ручная проверка: недостаточно данных для обращения к MCP-серверам.",
    },
]


def _to_frontend_identifiers(parsed: dict[str, Any], nlu: dict[str, Any]) -> dict[str, Any]:
    return {
        "orderId": parsed.get("order_id"),
        "transactionId": parsed.get("transaction_id"),
        "userId": parsed.get("user_id"),
        "service": nlu.get("service", "unknown"),
        "confidence": nlu.get("confidence", 42),
    }


def _event(case: dict[str, Any], title: str, detail: str, status: str) -> dict[str, Any]:
    return {
        "id": f"evt-{len(case['timeline']) + 1}",
        "title": title,
        "detail": detail,
        "time": _format_now(),
        "status": status,
    }


def _get_case(case_id: str) -> dict[str, Any]:
    case = next((item for item in _CASES if item["id"] == case_id), None)
    if not case:
        raise KeyError(case_id)
    return case


def list_cases() -> list[dict[str, Any]]:
    return deepcopy(_CASES)


def parse_case(case_id: str, message: str) -> dict[str, Any]:
    case = _get_case(case_id)
    parsed = parse_dispute(message)
    nlu = detect_service(message, parsed.get("service_hint"))
    identifiers = _to_frontend_identifiers(parsed, nlu)
    case.update(
        {
            "message": message,
            "identifiers": identifiers,
            "status": "attention" if identifiers["confidence"] < 70 else "processing",
        }
    )
    case["timeline"].append(
        _event(
            case,
            "Парсинг выполнен",
            (
                f"Найдены service={identifiers['service']}, "
                f"order_id={identifiers.get('orderId') or 'нет'}, "
                f"transaction_id={identifiers.get('transactionId') or 'нет'}"
            ),
            "warning" if identifiers["confidence"] < 70 else "success",
        )
    )
    return deepcopy(case)


def run_mcp(case_id: str, message: str) -> dict[str, Any]:
    case = _get_case(case_id)
    parsed = parse_dispute(message)
    nlu = detect_service(message, parsed.get("service_hint"))
    identifiers = _to_frontend_identifiers(parsed, nlu)
    mcp_response = dispatch(nlu.get("service"), parsed)
    case.update(
        {
            "message": message,
            "identifiers": identifiers,
            "status": "attention" if nlu.get("service") == "unknown" else "processing",
            "connectors": _build_connectors(nlu.get("service"), mcp_response),
        }
    )
    case["timeline"].append(
        _event(
            case,
            "Маршрутизация остановлена" if nlu.get("service") == "unknown" else "MCP-ответ получен",
            (
                "Сервис не определен, нужен ручной выбор"
                if nlu.get("service") == "unknown"
                else f"Запрос направлен в {nlu.get('service')}"
            ),
            "warning" if nlu.get("service") == "unknown" else "success",
        )
    )
    return deepcopy(case)


def generate_result(case_id: str, message: str) -> dict[str, Any]:
    case = _get_case(case_id)
    response = process_dispute(message)
    case.update(
        {
            "message": message,
            "identifiers": _to_frontend_identifiers(response["parsed"], response["nlu"]),
            "status": response["status"],
            "result": response["result"],
        }
    )
    case["timeline"].append(
        _event(
            case,
            "Ответ сформирован",
            "Добавлен комментарий для ручной проверки"
            if response["status"] == "attention"
            else "Итог готов для передачи в НСПК",
            "warning" if response["status"] == "attention" else "success",
        )
    )
    return deepcopy(case)


def update_result(case_id: str, result: str) -> dict[str, Any]:
    case = _get_case(case_id)
    case["result"] = result
    return deepcopy(case)


def _build_connectors(service: str | None, mcp_response: dict[str, Any]) -> list[dict[str, Any]]:
    connectors = _connectors()
    if service not in {"taxi", "afisha"}:
        for connector in connectors:
            connector["status"] = "failed"
            connector["fields"] = [
                {**field, "value": "сервис не определен, нужен ручной выбор"}
                for field in connector["fields"]
            ]
        return connectors

    for connector in connectors:
        if connector["service"] != service:
            continue
        connector["status"] = "done" if mcp_response.get("status") == "found" else "failed"
        connector["confidence"] = 97 if service == "taxi" else 93
        data = mcp_response.get("data") or {}
        connector["fields"] = _taxi_fields(data) if service == "taxi" else _afisha_fields(data)
    return connectors


def _taxi_fields(data: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"label": "Маршрут", "value": data.get("route", "нет данных")},
        {"label": "Статус поездки", "value": data.get("ride_status", "нет данных")},
        {"label": "Оплата", "value": data.get("payment_status", "нет данных")},
    ]


def _afisha_fields(data: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"label": "Событие", "value": data.get("event", "нет данных")},
        {"label": "Статус билета", "value": data.get("ticket_status", "нет данных")},
        {"label": "Возврат", "value": "разрешен" if data.get("refund_allowed") else "нет данных"},
    ]
