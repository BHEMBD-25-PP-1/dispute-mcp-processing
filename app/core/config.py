from pydantic_settings import BaseSettings, SettingsConfigDict


class GigaChatProperties(BaseSettings):

    GIGACHAT_AUTH_KEY: str
    GIGACHAT_AUTH_URL: str
    GIGACHAT_API_URL: str
    LLM_PROVIDER: str = "gigachat"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


def get_settings():
    return GigaChatProperties()


gigaChatProperties = get_settings()