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


def test_detect_service_uses_explicit_hint_before_rules():
    result = service_classifier.detect_service("театр и поездка одновременно", service_hint="afisha")

    assert result == {"service": "afisha", "confidence": 98, "source": "explicit_hint"}


def test_detect_service_handles_empty_llm_response(monkeypatch):
    class EmptyLLM:
        def chat(self, prompt: str):
            return ""

    monkeypatch.setattr(service_classifier, "get_llm_client", lambda: EmptyLLM())

    result = service_classifier.detect_service("спорное списание без подсказок")

    assert result == {"service": "unknown", "confidence": 35, "source": "llm"}


def test_detect_service_normalizes_unexpected_llm_response(monkeypatch):
    class InvalidLLM:
        def chat(self, prompt: str):
            return "hotel"

    monkeypatch.setattr(service_classifier, "get_llm_client", lambda: InvalidLLM())

    result = service_classifier.detect_service("спорное списание без явного сервиса")

    assert result == {"service": "unknown", "confidence": 35, "source": "llm"}
