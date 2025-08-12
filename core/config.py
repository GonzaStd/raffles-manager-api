from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
    Field
)


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra="ignore",
        env_ignore_empty = True,
    )
    DOMAIN: str = 'localhost'
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    JWT_SECRET_KEY: str

    @computed_field
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    BACKEND_CORS_ORIGINS: list[str] = Field(default_factory=list)

    # Local development variables (from .env)
    MARIADB_USERNAME: str = ""
    MARIADB_PASSWORD: str = ""
    MARIADB_SERVER: str = ""
    MARIADB_PORT: int = 3306
    MARIADB_DATABASE: str = ""

    # Railway production variables - use the full DATABASE_URL that Railway provides
    DATABASE_URL: str = ""  # Railway's complete database URL
    MYSQL_URL: str = ""     # Alternative Railway variable name

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # First priority: Use DATABASE_URL if available (Railway standard)
        if self.DATABASE_URL:
            # Convert mysql:// to mysql+pymysql://
            url = self.DATABASE_URL
            if url.startswith("mysql://"):
                url = url.replace("mysql://", "mysql+pymysql://", 1)
            return url

        # Second priority: Use MYSQL_URL if available
        elif self.MYSQL_URL:
            url = self.MYSQL_URL
            if url.startswith("mysql://"):
                url = url.replace("mysql://", "mysql+pymysql://", 1)
            return url

        # Fallback: Local development with .env variables
        else:
            return f"mysql+pymysql://{self.MARIADB_USERNAME}:{self.MARIADB_PASSWORD}@{self.MARIADB_SERVER}:{self.MARIADB_PORT}/{self.MARIADB_DATABASE}"
