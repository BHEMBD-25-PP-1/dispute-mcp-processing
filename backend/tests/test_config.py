from app.core.config import Settings
from app.core.llm_config import GigaChatProperties


def test_cors_origin_list_trims_empty_items():
    settings = Settings(cors_origins=" http://one.test, ,http://two.test ")

    assert settings.cors_origin_list() == ["http://one.test", "http://two.test"]


def test_gigachat_properties_expose_api_url_alias():
    settings = GigaChatProperties(GIGACHAT_API_URL="https://gigachat.test/chat")

    assert settings.GIGACHAT_API_URL == "https://gigachat.test/chat"
