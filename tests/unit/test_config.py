"""Unit tests for configuration management."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from typesense_dangerzone.config import Settings, get_settings


class TestSettings:
    """Tests for the Settings class."""

    def test_settings_with_required_env_vars(
        self, mock_env_vars: dict[str, str]
    ) -> None:
        """Test settings load correctly with required environment variables."""
        settings = Settings()

        assert settings.api_key.get_secret_value() == "test-api-key-12345"
        assert settings.host == "localhost"
        assert settings.port == 8108
        assert settings.protocol == "http"

    def test_settings_default_values(self, mock_env_vars: dict[str, str]) -> None:
        """Test default values are applied correctly."""
        settings = Settings()

        assert settings.connection_timeout_seconds == 5
        assert settings.search_timeout_seconds == 10
        assert settings.default_collection == "movies"

    def test_settings_missing_api_key_raises_error(self) -> None:
        """Test that missing API key raises ValidationError."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            assert any(e["loc"] == ("api_key",) for e in errors)

    def test_settings_invalid_port_raises_error(
        self, mock_env_vars: dict[str, str]
    ) -> None:
        """Test that invalid port raises ValidationError."""
        with patch.dict(os.environ, {"TYPESENSE_PORT": "99999"}, clear=False):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            assert any("port" in str(e["loc"]) for e in errors)

    def test_settings_invalid_protocol_raises_error(
        self, mock_env_vars: dict[str, str]
    ) -> None:
        """Test that invalid protocol raises ValidationError."""
        with patch.dict(os.environ, {"TYPESENSE_PROTOCOL": "ftp"}, clear=False):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            assert any("protocol" in str(e["loc"]) for e in errors)

    def test_node_config_property(self, mock_env_vars: dict[str, str]) -> None:
        """Test node_config property returns correct structure."""
        settings = Settings()
        node_config = settings.node_config

        assert node_config == {
            "host": "localhost",
            "port": 8108,
            "protocol": "http",
        }

    def test_api_key_is_secret_str(self, mock_env_vars: dict[str, str]) -> None:
        """Test that API key is stored as SecretStr."""
        settings = Settings()

        # SecretStr should not expose value in string representation
        assert "test-api-key" not in str(settings.api_key)
        assert "test-api-key" not in repr(settings.api_key)

        # But should be accessible via get_secret_value
        assert settings.api_key.get_secret_value() == "test-api-key-12345"


class TestGetSettings:
    """Tests for the get_settings function."""

    def test_get_settings_returns_settings(self, mock_env_vars: dict[str, str]) -> None:
        """Test get_settings returns a Settings instance."""
        settings = get_settings()

        assert isinstance(settings, Settings)
        assert settings.api_key.get_secret_value() == "test-api-key-12345"

    def test_get_settings_is_cached(self, mock_env_vars: dict[str, str]) -> None:
        """Test get_settings returns the same cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_get_settings_cache_clear(self, mock_env_vars: dict[str, str]) -> None:
        """Test cache can be cleared to reload settings."""
        settings1 = get_settings()

        get_settings.cache_clear()

        settings2 = get_settings()

        # Different instances after cache clear
        assert settings1 is not settings2
        # But same values
        assert (
            settings1.api_key.get_secret_value() == settings2.api_key.get_secret_value()
        )
