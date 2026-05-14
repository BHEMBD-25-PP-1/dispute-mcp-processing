from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()

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