"""Typesense client factory with error handling."""

from functools import lru_cache
from typing import Any

import typesense
from typesense.exceptions import (
    ObjectNotFound,
    RequestUnauthorized,
    ServerError,
    ServiceUnavailable,
)

from typesense_dangerzone.config import Settings, get_settings
from typesense_dangerzone.exceptions import (
    CollectionNotFoundError,
    ConnectionError,
    TypesenseDangerzoneError,
)
from typesense_dangerzone.logging_config import get_logger

logger = get_logger(__name__)


def create_client(settings: Settings | None = None) -> Any:
    """Create a new Typesense client instance.

    Args:
        settings: Optional settings override. Uses default settings if not provided.

    Returns:
        A configured Typesense client.

    Raises:
        ConnectionError: If unable to connect to Typesense server.
    """
    if settings is None:
        settings = get_settings()

    config: dict[str, Any] = {
        "nodes": [
            {
                "host": settings.host,
                "port": str(settings.port),
                "protocol": settings.protocol,
            }
        ],
        "api_key": settings.api_key.get_secret_value(),
        "connection_timeout_seconds": settings.connection_timeout_seconds,
    }

    logger.debug(
        "creating_typesense_client",
        host=settings.host,
        port=settings.port,
        protocol=settings.protocol,
    )

    return typesense.Client(config)  # type: ignore[attr-defined,arg-type]


@lru_cache
def get_client() -> Any:
    """Get a cached Typesense client instance.

    Returns:
        A cached Typesense client.

    Note:
        The client is cached after first creation. Use get_client.cache_clear()
        to recreate the client if settings change during runtime.
    """
    return create_client()


def health_check(client: Any | None = None) -> bool:
    """Check if Typesense server is healthy.

    Args:
        client: Optional client instance. Uses cached client if not provided.

    Returns:
        True if server is healthy, False otherwise.
    """
    if client is None:
        client = get_client()

    try:
        health = client.operations.is_healthy()
        logger.debug("health_check_completed", healthy=health)
        return bool(health)
    except (ServiceUnavailable, ServerError, RequestUnauthorized) as e:
        logger.warning("health_check_failed", error=str(e))
        return False
    except Exception as e:
        logger.error("health_check_error", error=str(e), error_type=type(e).__name__)
        return False


def get_collection(
    collection_name: str,
    client: Any | None = None,
) -> Any:
    """Get a collection by name with error handling.

    Args:
        collection_name: Name of the collection to retrieve.
        client: Optional client instance. Uses cached client if not provided.

    Returns:
        The collection object.

    Raises:
        CollectionNotFoundError: If collection does not exist.
        ConnectionError: If unable to connect to server.
    """
    if client is None:
        client = get_client()

    try:
        collection = client.collections[collection_name].retrieve()
        logger.debug("collection_retrieved", collection_name=collection_name)
        return collection
    except ObjectNotFound as e:
        raise CollectionNotFoundError(collection_name) from e
    except ServiceUnavailable as e:
        settings = get_settings()
        raise ConnectionError(
            message=f"Typesense server unavailable: {e}",
            host=settings.host,
            port=settings.port,
        ) from e
    except RequestUnauthorized as e:
        raise TypesenseDangerzoneError(
            "Authentication failed. Check your API key.",
            {"hint": "Ensure TYPESENSE_API_KEY is set correctly"},
        ) from e
