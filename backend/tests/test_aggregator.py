from app.mcp.client import MCPClient
from app.services.dispute_processor import _build_operator_answer, process_dispute

def test_process_dispute(monkeypatch):
    class FakeLLM:
        def chat(self, prompt):
            return "taxi"
    monkeypatch.setattr("app.services.service_classifier.get_llm_client", lambda: FakeLLM())

    result = process_dispute("transaction_id=TXN-98765, order_id=TAXI-240518 проблема такси")

    assert result["status"] == "resolved"
    assert result["parsed"]["order_id"] == "TAXI-240518"
    assert result["parsed"]["transaction_id"] == "TXN-98765"
    assert result["nlu"]["service"] == "taxi"
    assert result["mcp"]["status"] == "found"


def test_process_dispute_unknown_service():
    result = process_dispute("Клиент оспаривает списание, деталей нет")

    assert result["status"] == "attention"
    assert result["nlu"]["service"] == "unknown"
    assert result["mcp"]["status"] == "skipped"


def test_process_dispute_handles_afisha_resolution():
    result = process_dispute("transaction_id=TXN-77210, order_id=AFISHA-8891 QR билет афиша")

    assert result["status"] == "resolved"
    assert result["nlu"]["service"] == "afisha"
    assert "Билет по заказу AFISHA-8891" in result["result"]


def test_process_dispute_marks_known_service_without_mcp_record_for_attention():
    result = process_dispute("transaction_id=TXN-000, order_id=TAXI-0000 проблема такси")

    assert result["status"] == "attention"
    assert result["mcp"]["status"] == "not_found"
    assert "не нашел данные" in result["result"]


def test_operator_answer_has_fallback_for_unhandled_service():
    answer = _build_operator_answer(
        {"order_id": "ORDER-1", "transaction_id": "TXN-1"},
        {"service": "custom"},
        {"status": "found"},
    )

    assert "нет правила" in answer


def test_mcp_client_returns_not_found_for_known_service_without_record():
    result = MCPClient().call("taxi", {"order_id": "TAXI-0000", "transaction_id": None})

    assert result["status"] == "not_found"
