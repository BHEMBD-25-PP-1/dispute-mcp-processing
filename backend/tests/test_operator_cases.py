import pytest

from app.services import operator_cases


def test_operator_cases_are_served_from_backend():
    cases = operator_cases.list_cases()

    assert cases
    assert cases[0]["id"].startswith("DSP-")
    assert cases[0]["connectors"]


def test_parse_case_updates_identifiers_and_timeline():
    original = operator_cases.list_cases()[0]
    case = operator_cases.parse_case(
        "DSP-1042",
        "transaction_id=TXN-98765, order_id=TAXI-240518 поездка не состоялась",
    )
    fresh = operator_cases.list_cases()[0]

    assert case["identifiers"]["service"] == "taxi"
    assert case["identifiers"]["orderId"] == "TAXI-240518"
    assert case["status"] == "processing"
    assert case["timeline"][-1]["title"] == "Парсинг выполнен"
    assert fresh == original


def test_run_mcp_blocks_unknown_service():
    case = operator_cases.run_mcp("DSP-1039", "Клиент оспаривает списание, сервис не указан")

    assert case["status"] == "attention"
    assert all(connector["status"] == "failed" for connector in case["connectors"])


def test_generate_result_uses_backend_processor():
    case = operator_cases.generate_result(
        "DSP-1042",
        "transaction_id=TXN-98765, order_id=TAXI-240518 поездка не состоялась",
    )
    fresh = operator_cases.list_cases()[0]

    assert case["status"] == "resolved"
    assert "Транзакция TXN-98765 подтверждена" in case["result"]
    assert fresh["status"] == "new"
    assert fresh["result"] == ""


def test_unknown_case_raises_key_error():
    with pytest.raises(KeyError):
        operator_cases.parse_case("DSP-404", "message")


def test_run_mcp_updates_taxi_connector_fields():
    case = operator_cases.run_mcp(
        "DSP-1042",
        "transaction_id=TXN-98765, order_id=TAXI-240518 поездка такси",
    )
    taxi = next(connector for connector in case["connectors"] if connector["service"] == "taxi")
    afisha = next(connector for connector in case["connectors"] if connector["service"] == "afisha")

    assert case["status"] == "processing"
    assert taxi["status"] == "done"
    assert taxi["confidence"] == 97
    assert taxi["fields"][0]["value"] == "Аэропорт Внуково -> Тверская, 9"
    assert afisha["status"] == "ready"


def test_run_mcp_updates_afisha_connector_fields():
    case = operator_cases.run_mcp(
        "DSP-1041",
        "transaction_id=TXN-77210, order_id=AFISHA-8891 билет афиша",
    )
    afisha = next(connector for connector in case["connectors"] if connector["service"] == "afisha")

    assert afisha["status"] == "done"
    assert afisha["confidence"] == 93
    assert afisha["fields"][0]["value"] == "Stand-up Hall, 12 мая"
    assert afisha["fields"][2]["value"] == "разрешен"


def test_generate_result_attention_adds_manual_review_timeline():
    case = operator_cases.generate_result("DSP-1039", "Клиент оспаривает списание без деталей")

    assert case["status"] == "attention"
    assert case["timeline"][-1]["detail"] == "Добавлен комментарий для ручной проверки"
    assert case["timeline"][-1]["status"] == "warning"


def test_update_result_changes_only_returned_copy():
    updated = operator_cases.update_result("DSP-1042", "Новый итог")
    fresh = operator_cases.list_cases()[0]

    assert updated["result"] == "Новый итог"
    assert fresh["result"] == ""
