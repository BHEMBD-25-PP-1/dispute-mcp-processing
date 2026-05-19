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
