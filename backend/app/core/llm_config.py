from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class GigaChatProperties(BaseSettings):
    auth_key: str = Field(default="", alias="GIGACHAT_AUTH_KEY")
    auth_url: str = Field(default="", alias="GIGACHAT_AUTH_URL")
    api_url: str = Field(default="", alias="GIGACHAT_API_URL")
    llm_provider: str = Field(default="gigachat", alias="LLM_PROVIDER")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def GIGACHAT_AUTH_KEY(self) -> str:
        return self.auth_key

    @property
    def GIGACHAT_AUTH_URL(self) -> str:
        return self.auth_url

    @property
    def GIGACHAT_API_URL(self) -> str:
        return self.api_url

    @property
    def LLM_PROVIDER(self) -> str:
        return self.llm_provider


def get_gigachat_settings():
    return GigaChatProperties()