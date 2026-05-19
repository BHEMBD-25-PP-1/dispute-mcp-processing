from app.services.dispute_processor import process_dispute

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