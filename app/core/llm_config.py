from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class GigaChatProperties(BaseSettings):
    auth_key: str = Field(alias="GIGACHAT_AUTH_KEY")
    auth_url: str = Field(alias="GIGACHAT_AUTH_URL")
    api_url: str = Field(alias="GIGACHAT_API_URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


def get_gigachat_settings():
    return GigaChatProperties()