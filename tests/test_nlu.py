from app.services import nlu


def test_detect_service_taxi(monkeypatch):

    class FakeGigaChat:
        def chat(self, prompt: str):
            return "taxi"

    monkeypatch.setattr(nlu, "get_llm_client", lambda: FakeGigaChat())

    result = nlu.detect_service("order_id=TXN-123 поездка такси")

    assert result["service"] == "taxi"