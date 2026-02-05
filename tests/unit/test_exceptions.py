"""Unit tests for custom exceptions."""

from typesense_dangerzone.exceptions import (
    CollectionAlreadyExistsError,
    CollectionNotFoundError,
    ConnectionError,
    DocumentNotFoundError,
    IndexingError,
    SearchError,
    TypesenseDangerzoneError,
)


class TestTypesenseDangerzoneError:
    """Tests for the base exception class."""

    def test_error_with_message_only(self) -> None:
        """Test error with message only."""
        error = TypesenseDangerzoneError("Something went wrong")

        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.details == {}

    def test_error_with_details(self) -> None:
        """Test error with details."""
        error = TypesenseDangerzoneError(
            "Something went wrong",
            details={"key": "value", "count": 42},
        )

        assert "Something went wrong" in str(error)
        assert "key" in str(error)
        assert error.details == {"key": "value", "count": 42}


class TestConnectionError:
    """Tests for ConnectionError."""

    def test_connection_error_default_message(self) -> None:
        """Test default message."""
        error = ConnectionError()

        assert "Failed to connect" in error.message

    def test_connection_error_with_host_and_port(self) -> None:
        """Test with host and port details."""
        error = ConnectionError(
            message="Cannot connect",
            host="localhost",
            port=8108,
        )

        assert error.details["host"] == "localhost"
        assert error.details["port"] == 8108


class TestCollectionNotFoundError:
    """Tests for CollectionNotFoundError."""

    def test_collection_not_found_error(self) -> None:
        """Test CollectionNotFoundError."""
        error = CollectionNotFoundError("movies")

        assert "movies" in str(error)
        assert error.collection_name == "movies"
        assert error.details["collection_name"] == "movies"


class TestCollectionAlreadyExistsError:
    """Tests for CollectionAlreadyExistsError."""

    def test_collection_already_exists_error(self) -> None:
        """Test CollectionAlreadyExistsError."""
        error = CollectionAlreadyExistsError("movies")

        assert "movies" in str(error)
        assert "already exists" in str(error)
        assert error.collection_name == "movies"


class TestDocumentNotFoundError:
    """Tests for DocumentNotFoundError."""

    def test_document_not_found_error(self) -> None:
        """Test DocumentNotFoundError."""
        error = DocumentNotFoundError("doc123", "movies")

        assert "doc123" in str(error)
        assert "movies" in str(error)
        assert error.document_id == "doc123"
        assert error.collection_name == "movies"


class TestSearchError:
    """Tests for SearchError."""

    def test_search_error_default_message(self) -> None:
        """Test default message."""
        error = SearchError()

        assert "Search operation failed" in error.message

    def test_search_error_with_query(self) -> None:
        """Test with query details."""
        error = SearchError(
            message="Search failed",
            query="test query",
            collection_name="movies",
        )

        assert error.details["query"] == "test query"
        assert error.details["collection_name"] == "movies"


class TestIndexingError:
    """Tests for IndexingError."""

    def test_indexing_error_default_message(self) -> None:
        """Test default message."""
        error = IndexingError()

        assert "Indexing operation failed" in error.message

    def test_indexing_error_with_counts(self) -> None:
        """Test with count details."""
        error = IndexingError(
            message="Some documents failed",
            failed_count=5,
            total_count=100,
        )

        assert error.details["failed_count"] == 5
        assert error.details["total_count"] == 100
