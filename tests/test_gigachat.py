from app.llm.gigachat import GigaChatClient


# TEST CHAT 
def test_chat(monkeypatch):

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": "taxi"
                        }
                    }
                ]
            }

    def fake_post(*args, **kwargs):
        return FakeResponse()

    import app.mcp.gigachat as gigachat_module
    monkeypatch.setattr(gigachat_module.requests, "post", fake_post)

    client = GigaChatClient()

    result = client.chat("order dispute taxi test")

    assert result == "taxi"


# TEST TOKEN 
def test_get_token(monkeypatch):

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "access_token": "fake_token_123"
            }

    def fake_post(*args, **kwargs):
        return FakeResponse()

    import app.mcp.gigachat as gigachat_module
    monkeypatch.setattr(gigachat_module.requests, "post", fake_post)

    client = GigaChatClient()

    assert client.token == "fake_token_123"