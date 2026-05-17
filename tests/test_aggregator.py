from app.services.aggregator import process_dispute

def test_process_dispute(monkeypatch):
    class FakeLLM:
        def chat(self, prompt):
            return "taxi"
    monkeypatch.setattr("app.services.nlu.get_llm_client", lambda: FakeLLM())

    result = process_dispute("TXN-123 проблема такси")

    assert result["parsed"]["order_id"] == "TXN-123"
    assert result["nlu"]["service"] == "taxi"   