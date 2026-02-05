"""Custom exception hierarchy for Typesense operations."""

from typing import Any


class TypesenseDangerzoneError(Exception):
    """Base exception for all Typesense Dangerzone errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConnectionError(TypesenseDangerzoneError):
    """Raised when unable to connect to Typesense server."""

    def __init__(
        self,
        message: str = "Failed to connect to Typesense server",
        host: str | None = None,
        port: int | None = None,
    ) -> None:
        details: dict[str, Any] = {}
        if host:
            details["host"] = host
        if port:
            details["port"] = port
        super().__init__(message, details)


class CollectionNotFoundError(TypesenseDangerzoneError):
    """Raised when a collection does not exist."""

    def __init__(self, collection_name: str) -> None:
        super().__init__(
            f"Collection '{collection_name}' not found",
            {"collection_name": collection_name},
        )
        self.collection_name = collection_name


class CollectionAlreadyExistsError(TypesenseDangerzoneError):
    """Raised when trying to create a collection that already exists."""

    def __init__(self, collection_name: str) -> None:
        super().__init__(
            f"Collection '{collection_name}' already exists",
            {"collection_name": collection_name},
        )
        self.collection_name = collection_name


class DocumentNotFoundError(TypesenseDangerzoneError):
    """Raised when a document does not exist."""

    def __init__(self, document_id: str, collection_name: str) -> None:
        super().__init__(
            f"Document '{document_id}' not found in collection '{collection_name}'",
            {"document_id": document_id, "collection_name": collection_name},
        )
        self.document_id = document_id
        self.collection_name = collection_name


class SearchError(TypesenseDangerzoneError):
    """Raised when a search operation fails."""

    def __init__(
        self,
        message: str = "Search operation failed",
        query: str | None = None,
        collection_name: str | None = None,
    ) -> None:
        details: dict[str, Any] = {}
        if query:
            details["query"] = query
        if collection_name:
            details["collection_name"] = collection_name
        super().__init__(message, details)


class IndexingError(TypesenseDangerzoneError):
    """Raised when indexing documents fails."""

    def __init__(
        self,
        message: str = "Indexing operation failed",
        failed_count: int | None = None,
        total_count: int | None = None,
    ) -> None:
        details: dict[str, Any] = {}
        if failed_count is not None:
            details["failed_count"] = failed_count
        if total_count is not None:
            details["total_count"] = total_count
        super().__init__(message, details)
