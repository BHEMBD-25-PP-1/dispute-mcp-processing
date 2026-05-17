from app.services import nlu

def test_detect_service_calls_prompt(monkeypatch):

    captured = {}

    class FakeLLM:
        def chat(self, prompt: str):
            captured["prompt"] = prompt
            return "taxi"

    monkeypatch.setattr(nlu, "get_llm_client", lambda: FakeLLM())

    nlu.detect_service("поездка такси TXN-123")

    assert "TXN-123" in captured["prompt"]