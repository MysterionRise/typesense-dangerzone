"""Typesense Dangerzone - Enterprise-grade Typesense search examples."""

from typesense_dangerzone.client import get_client
from typesense_dangerzone.config import Settings, get_settings
from typesense_dangerzone.exceptions import (
    CollectionAlreadyExistsError,
    CollectionNotFoundError,
    ConnectionError,
    DocumentNotFoundError,
    TypesenseDangerzoneError,
)

__version__ = "0.1.0"

__all__ = [
    "CollectionAlreadyExistsError",
    "CollectionNotFoundError",
    "ConnectionError",
    "DocumentNotFoundError",
    "Settings",
    "TypesenseDangerzoneError",
    "__version__",
    "get_client",
    "get_settings",
]
