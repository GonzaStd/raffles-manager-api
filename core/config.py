from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated, Any, Literal, Optional

from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
    Field
)


def parse_cors(v: Any) -> list[str]:
    if v is None or v == "":
        return []
    if isinstance(v, str):
        if v.startswith("[") and v.endswith("]"):
            # Try to parse as JSON list
            try:
                import json
                return json.loads(v)
            except:
                return []
        else:
            # Parse as comma-separated string
            return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list):
        return v
    return []


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra="ignore",
        env_ignore_empty=True,
    )
    DOMAIN: str = 'localhost'
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"

    @computed_field
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    # Simple string field that we'll process manually to avoid Pydantic auto-parsing
    backend_cors_origins_raw: str = Field(default="", alias="BACKEND_CORS_ORIGINS")

    @computed_field
    @property
    def BACKEND_CORS_ORIGINS(self) -> list[str]:
        return parse_cors(self.backend_cors_origins_raw)

    # Railway MySQL variables
    DATABASE_URL: Optional[str] = None
    MYSQL_URL: Optional[str] = None
    MYSQLUSER: Optional[str] = None
    MYSQLPASSWORD: Optional[str] = None
    MYSQLHOST: Optional[str] = None
    MYSQLPORT: int = 3306
    MYSQLDATABASE: Optional[str] = None

    # Local MariaDB variables
    MARIADB_USERNAME: str = ""
    MARIADB_PASSWORD: str = ""
    MARIADB_SERVER: str = ""
    MARIADB_PORT: int = 3306
    MARIADB_DATABASE: str = ""

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # First priority: Use DATABASE_URL if available (Railway standard)
        if self.DATABASE_URL:
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
        # Third priority: Use Railway variables if available
        elif self.MYSQLUSER and self.MYSQLHOST and self.MYSQLDATABASE:
            return f"mysql+pymysql://{self.MYSQLUSER}:{self.MYSQLPASSWORD}@{self.MYSQLHOST}:{self.MYSQLPORT}/{self.MYSQLDATABASE}"
        # Fallback: Local development with .env variables
        else:
            return f"mysql+pymysql://{self.MARIADB_USERNAME}:{self.MARIADB_PASSWORD}@{self.MARIADB_SERVER}:{self.MARIADB_PORT}/{self.MARIADB_DATABASE}"
