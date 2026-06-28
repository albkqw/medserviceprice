from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Application
    APP_NAME: str = "MedServicePrice"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # CORS — list parsed from JSON string in .env
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Admin API key — required for scheduler endpoints (POST /run, GET /jobs, /runs)
    ADMIN_API_KEY: str

    # PostgreSQL connection parts — composed into a URL via computed_field
    # so individual parts stay readable/overridable in CI and Docker environments
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
