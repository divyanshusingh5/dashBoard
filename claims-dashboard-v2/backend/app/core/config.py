"""
Application configuration using Pydantic Settings.
Supports both SQLite and Snowflake databases via DATABASE_TYPE environment variable.
"""

from typing import List, Literal
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # Application
    APP_NAME: str = "Claims Analytics Dashboard"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: str | List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v

    # Database Type Selection
    DATABASE_TYPE: Literal["sqlite", "snowflake"] = "sqlite"

    # SQLite Configuration
    SQLITE_DB_PATH: str = "./app/db/claims_analytics.db"
    SQLITE_POOL_SIZE: int = 20
    SQLITE_MAX_OVERFLOW: int = 40
    SQLITE_POOL_TIMEOUT: int = 30
    SQLITE_POOL_RECYCLE: int = 3600

    # Snowflake Configuration
    SNOWFLAKE_ACCOUNT: str = ""
    SNOWFLAKE_USER: str = ""
    SNOWFLAKE_PASSWORD: str = ""
    SNOWFLAKE_DATABASE: str = "CLAIMS_DB"
    SNOWFLAKE_SCHEMA: str = "ANALYTICS"
    SNOWFLAKE_WAREHOUSE: str = "COMPUTE_WH"
    SNOWFLAKE_ROLE: str = "ANALYST"
    SNOWFLAKE_POOL_SIZE: int = 5
    SNOWFLAKE_MAX_OVERFLOW: int = 10

    # Performance Settings
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # seconds
    MATERIALIZED_VIEWS_ENABLED: bool = True

    # Pagination
    DEFAULT_PAGE_SIZE: int = 100
    MAX_PAGE_SIZE: int = 10000

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.DATABASE_TYPE == "sqlite"

    @property
    def is_snowflake(self) -> bool:
        """Check if using Snowflake database."""
        return self.DATABASE_TYPE == "snowflake"

    @property
    def database_url(self) -> str:
        """Get the appropriate database URL based on DATABASE_TYPE."""
        if self.is_sqlite:
            return f"sqlite:///{self.SQLITE_DB_PATH}"
        elif self.is_snowflake:
            return (
                f"snowflake://{self.SNOWFLAKE_USER}:{self.SNOWFLAKE_PASSWORD}"
                f"@{self.SNOWFLAKE_ACCOUNT}/{self.SNOWFLAKE_DATABASE}"
                f"/{self.SNOWFLAKE_SCHEMA}?warehouse={self.SNOWFLAKE_WAREHOUSE}"
                f"&role={self.SNOWFLAKE_ROLE}"
            )
        else:
            raise ValueError(f"Unsupported DATABASE_TYPE: {self.DATABASE_TYPE}")


# Global settings instance
settings = Settings()
