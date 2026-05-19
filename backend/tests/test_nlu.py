from app.services import service_classifier

def test_detect_service_uses_rules_first():
    result = service_classifier.detect_service("поездка такси TXN-123")

    assert result["service"] == "taxi"
    assert result["source"] == "rules"


def test_detect_service_calls_llm_when_rules_are_unclear(monkeypatch):
    captured = {}

    class FakeLLM:
        def chat(self, prompt: str):
            captured["prompt"] = prompt
            return "taxi"

    monkeypatch.setattr(service_classifier, "get_llm_client", lambda: FakeLLM())

    result = service_classifier.detect_service("спорное списание TXN-123")

    assert "TXN-123" in captured["prompt"]
    assert result["service"] == "taxi"
    assert result["source"] == "llm"