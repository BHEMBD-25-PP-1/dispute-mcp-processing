from types import SimpleNamespace
from app.llm.gigachat import GigaChatClient

def test_get_token(monkeypatch):

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"access_token": "fake_token"}

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "app.llm.gigachat.requests.post",
        fake_post
    )

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

    assert client.token == "fake_token"