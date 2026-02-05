"""Configuration management using Pydantic Settings."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Environment variables can be set directly or via a .env file.
    All variables are prefixed with TYPESENSE_ for namespace isolation.

    Example:
        export TYPESENSE_API_KEY=your-secure-api-key
        export TYPESENSE_HOST=localhost
        export TYPESENSE_PORT=8108
    """

    model_config = SettingsConfigDict(
        env_prefix="TYPESENSE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Connection settings
    host: str = Field(
        default="localhost",
        description="Typesense server hostname",
    )
    port: int = Field(
        default=8108,
        ge=1,
        le=65535,
        description="Typesense server port",
    )
    protocol: str = Field(
        default="http",
        pattern=r"^https?$",
        description="Connection protocol (http or https)",
    )
    api_key: SecretStr = Field(
        ...,  # Required, no default for security
        description="Typesense API key (required)",
        min_length=1,
    )

    # Timeout settings
    connection_timeout_seconds: int = Field(
        default=5,
        ge=1,
        le=60,
        description="Connection timeout in seconds",
    )
    search_timeout_seconds: int = Field(
        default=10,
        ge=1,
        le=120,
        description="Search operation timeout in seconds",
    )

    # Collection settings
    default_collection: str = Field(
        default="movies",
        description="Default collection name",
    )

    @property
    def node_config(self) -> dict[str, str | int]:
        """Generate node configuration for Typesense client."""
        return {
            "host": self.host,
            "port": self.port,
            "protocol": self.protocol,
        }


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        Settings: Application configuration loaded from environment.

    Note:
        Settings are cached after first load. Use get_settings.cache_clear()
        to reload settings if environment changes during runtime.
    """
    return Settings()
