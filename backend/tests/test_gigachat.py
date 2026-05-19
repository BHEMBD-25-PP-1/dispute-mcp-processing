from types import SimpleNamespace
from app.llm.gigachat import GigaChatClient
import app.llm.gigachat as gigachat_module


def test_chat(monkeypatch):

    class FakeResponse:
        def __init__(self, json_data):
            self._json = json_data

        def raise_for_status(self):
            pass

        def json(self):
            return self._json

    def fake_post(url, *args, **kwargs):
        if url == "test_auth_url":
            return FakeResponse({"access_token": "fake_token"})

        return FakeResponse({
            "choices": [
                {"message": {"content": "taxi"}}
            ]
        })

    monkeypatch.setattr(gigachat_module.requests, "post", fake_post)

    fake_settings = SimpleNamespace(
        GIGACHAT_AUTH_KEY="test_auth_key",
        GIGACHAT_AUTH_URL="test_auth_url",
        GIGACHAT_API_URL="test_api_url"
    )

    monkeypatch.setattr(
        "app.llm.gigachat.gigachat_settings",
        fake_settings
    )

    client = GigaChatClient()

    result = client.chat("test")

    assert result == "taxi"