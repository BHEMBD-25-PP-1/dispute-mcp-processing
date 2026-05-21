from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://dispute:dispute@localhost:5432/dispute"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    event_signature_secret: str = "dev-event-secret-change-me"
    seed_operator_username: str | None = None
    seed_operator_password: str | None = None
    kafka_enabled: bool = False
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_events_topic: str = "dispute-events"
    log_level: str = "INFO"
    cors_origins: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "https://bhembd-25-pp-1.github.io"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()

