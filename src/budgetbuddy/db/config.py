from __future__ import annotations

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment.

    Env vars are prefixed with BB_. You can also use a .env file.
    Example: BB_DATABASE_USER, BB_DATABASE_PASSWORD, etc.
    """

    model_config = SettingsConfigDict(
        env_prefix="BB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_type: str = "postgresql"
    database_driver: str = "psycopg2"
    database_user: str = "postgres"
    database_password: str = "postgres"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "budgetbuddy"

    sqlalchemy_echo: bool = False

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"{self.database_type}+{self.database_driver}://"
            f"{self.database_user}:{self.database_password}@"
            f"{self.database_host}:{self.database_port}/{self.database_name}"
        )


# Instantiate settings once for application use
settings = Settings()

# Backward-compatible exports
DATABASE_URL = settings.database_url

NAMING_CONVENTION = {
    "ix": "ix__%(column_0_N_label)s",
    "uq": "uq__%(table_name)s__%(column_0_N_name)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(column_0_N_name)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}
