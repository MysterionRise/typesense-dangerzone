"""Unit tests for Typesense client factory."""

from unittest.mock import MagicMock, patch

import pytest
from typesense.exceptions import ObjectNotFound, RequestUnauthorized, ServiceUnavailable

from typesense_dangerzone.client import (
    create_client,
    get_client,
    get_collection,
    health_check,
)
from typesense_dangerzone.config import Settings
from typesense_dangerzone.exceptions import (
    CollectionNotFoundError,
    ConnectionError,
    TypesenseDangerzoneError,
)


class TestCreateClient:
    """Tests for the create_client function."""

    def test_create_client_with_settings(self, mock_env_vars: dict[str, str]) -> None:
        """Test creating a client with default settings."""
        with patch("typesense_dangerzone.client.typesense.Client") as mock_client:
            create_client()

            mock_client.assert_called_once()
            call_args = mock_client.call_args[0][0]

            assert call_args["api_key"] == "test-api-key-12345"
            assert call_args["nodes"][0]["host"] == "localhost"
            assert call_args["nodes"][0]["port"] == "8108"
            assert call_args["nodes"][0]["protocol"] == "http"

    def test_create_client_with_custom_settings(self) -> None:
        """Test creating a client with custom settings."""
        custom_settings = Settings(
            api_key="custom-key",
            host="custom-host",
            port=9108,
            protocol="https",
        )

        with patch("typesense_dangerzone.client.typesense.Client") as mock_client:
            create_client(settings=custom_settings)

            call_args = mock_client.call_args[0][0]

            assert call_args["api_key"] == "custom-key"
            assert call_args["nodes"][0]["host"] == "custom-host"
            assert call_args["nodes"][0]["port"] == "9108"
            assert call_args["nodes"][0]["protocol"] == "https"


class TestGetClient:
    """Tests for the get_client function."""

    def test_get_client_is_cached(self, mock_env_vars: dict[str, str]) -> None:
        """Test get_client returns cached instance."""
        with patch("typesense_dangerzone.client.typesense.Client") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance

            client1 = get_client()
            client2 = get_client()

            assert client1 is client2
            mock_client.assert_called_once()


class TestHealthCheck:
    """Tests for the health_check function."""

    def test_health_check_returns_true_when_healthy(
        self, mock_typesense_client: MagicMock
    ) -> None:
        """Test health check returns True when server is healthy."""
        mock_typesense_client.operations.is_healthy.return_value = True

        result = health_check(client=mock_typesense_client)

        assert result is True

    def test_health_check_returns_false_when_unhealthy(
        self, mock_typesense_client: MagicMock
    ) -> None:
        """Test health check returns False when server is unhealthy."""
        mock_typesense_client.operations.is_healthy.return_value = False

        result = health_check(client=mock_typesense_client)

        assert result is False

    def test_health_check_returns_false_on_service_unavailable(
        self, mock_typesense_client: MagicMock
    ) -> None:
        """Test health check returns False on ServiceUnavailable."""
        mock_typesense_client.operations.is_healthy.side_effect = ServiceUnavailable(
            "Service unavailable"
        )

        result = health_check(client=mock_typesense_client)

        assert result is False

    def test_health_check_returns_false_on_auth_error(
        self, mock_typesense_client: MagicMock
    ) -> None:
        """Test health check returns False on authentication error."""
        mock_typesense_client.operations.is_healthy.side_effect = RequestUnauthorized(
            "Unauthorized"
        )

        result = health_check(client=mock_typesense_client)

        assert result is False


class TestGetCollection:
    """Tests for the get_collection function."""

    def test_get_collection_returns_collection(
        self, mock_typesense_client: MagicMock
    ) -> None:
        """Test get_collection returns collection data."""
        mock_typesense_client.collections.__getitem__.return_value.retrieve.return_value = {
            "name": "movies",
            "num_documents": 100,
        }

        result = get_collection("movies", client=mock_typesense_client)

        assert result["name"] == "movies"
        assert result["num_documents"] == 100

    def test_get_collection_raises_not_found_error(
        self, mock_typesense_client: MagicMock
    ) -> None:
        """Test get_collection raises CollectionNotFoundError."""
        mock_typesense_client.collections.__getitem__.return_value.retrieve.side_effect = ObjectNotFound(
            "Collection not found"
        )

        with pytest.raises(CollectionNotFoundError) as exc_info:
            get_collection("nonexistent", client=mock_typesense_client)

        assert exc_info.value.collection_name == "nonexistent"

    def test_get_collection_raises_connection_error(
        self, mock_typesense_client: MagicMock, mock_env_vars: dict[str, str]
    ) -> None:
        """Test get_collection raises ConnectionError on service unavailable."""
        mock_typesense_client.collections.__getitem__.return_value.retrieve.side_effect = ServiceUnavailable(
            "Server unavailable"
        )

        with pytest.raises(ConnectionError) as exc_info:
            get_collection("movies", client=mock_typesense_client)

        assert "unavailable" in exc_info.value.message.lower()

    def test_get_collection_raises_auth_error(
        self, mock_typesense_client: MagicMock
    ) -> None:
        """Test get_collection raises error on authentication failure."""
        mock_typesense_client.collections.__getitem__.return_value.retrieve.side_effect = RequestUnauthorized(
            "Invalid API key"
        )

        with pytest.raises(TypesenseDangerzoneError) as exc_info:
            get_collection("movies", client=mock_typesense_client)

        assert "Authentication failed" in exc_info.value.message
