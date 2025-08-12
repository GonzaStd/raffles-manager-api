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

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = Field(default=lambda: [])

    # Local development variables (from .env)
    MARIADB_USERNAME: str = ""
    MARIADB_PASSWORD: str = ""
    MARIADB_SERVER: str = ""
    MARIADB_PORT: int = 3306
    MARIADB_DATABASE: str = ""

    # Railway production variables
    MYSQLUSER: str = ""
    MYSQLPASSWORD: str = ""
    MYSQLHOST: str = ""
    MYSQLPORT: int = 3306
    MYSQLDATABASE: str = ""

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Use Railway variables if available (production), otherwise use local variables
        if self.MYSQLUSER and self.MYSQLHOST:
            # Production environment with Railway variables
            return f"mysql+pymysql://{self.MYSQLUSER}:{self.MYSQLPASSWORD}@{self.MYSQLHOST}:{self.MYSQLPORT}/{self.MYSQLDATABASE}"
        else:
            # Local development with .env variables
            return f"mysql+pymysql://{self.MARIADB_USERNAME}:{self.MARIADB_PASSWORD}@{self.MARIADB_SERVER}:{self.MARIADB_PORT}/{self.MARIADB_DATABASE}"
