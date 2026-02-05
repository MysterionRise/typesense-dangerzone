"""Integration tests for search functionality.

These tests require a running Typesense server.
"""

import os
from collections.abc import Generator
from typing import Any

import pytest

from typesense_dangerzone.client import create_client, health_check
from typesense_dangerzone.collections.movies import (
    Movie,
    create_movies_collection,
    delete_movies_collection,
    faceted_search,
    index_movies,
    keyword_search,
)
from typesense_dangerzone.config import Settings
from typesense_dangerzone.exceptions import (
    CollectionAlreadyExistsError,
    CollectionNotFoundError,
)

# Skip all integration tests if Typesense is not available
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def typesense_settings() -> Settings:
    """Get settings for integration tests."""
    return Settings(
        api_key=os.environ.get("TYPESENSE_API_KEY", "xyz"),
        host=os.environ.get("TYPESENSE_HOST", "localhost"),
        port=int(os.environ.get("TYPESENSE_PORT", "8108")),
        protocol=os.environ.get("TYPESENSE_PROTOCOL", "http"),
    )


@pytest.fixture(scope="module")
def integration_client(typesense_settings: Settings) -> Any:
    """Create a client for integration tests."""
    client = create_client(settings=typesense_settings)

    # Skip if server is not available
    if not health_check(client):
        pytest.skip("Typesense server not available")

    return client


@pytest.fixture
def clean_collection(integration_client: Any) -> Generator[Any, None, None]:
    """Ensure collection is clean before and after tests."""
    # Clean up before test
    try:
        delete_movies_collection(client=integration_client)
    except CollectionNotFoundError:
        pass

    yield integration_client

    # Clean up after test
    try:
        delete_movies_collection(client=integration_client)
    except CollectionNotFoundError:
        pass


@pytest.fixture
def sample_integration_movies() -> list[Movie]:
    """Sample movies for integration testing."""
    return [
        Movie(
            id="tt0111161",
            Title="The Shawshank Redemption",
            Year="1994",
            Genre="Drama",
            Director="Frank Darabont",
            imdbRating="9.3",
            Plot="Two imprisoned men bond over a number of years.",
        ),
        Movie(
            id="tt0068646",
            Title="The Godfather",
            Year="1972",
            Genre="Crime, Drama",
            Director="Francis Ford Coppola",
            imdbRating="9.2",
            Plot="The aging patriarch of an organized crime dynasty.",
        ),
        Movie(
            id="tt0468569",
            Title="The Dark Knight",
            Year="2008",
            Genre="Action, Crime, Drama",
            Director="Christopher Nolan",
            imdbRating="9.0",
            Plot="Batman faces the Joker in Gotham City.",
        ),
    ]


class TestCollectionLifecycle:
    """Integration tests for collection lifecycle operations."""

    def test_create_and_delete_collection(self, clean_collection: Any) -> None:
        """Test creating and deleting a collection."""
        # Create collection
        result = create_movies_collection(client=clean_collection)
        assert result["name"] == "movies"

        # Delete collection
        delete_result = delete_movies_collection(client=clean_collection)
        assert delete_result["name"] == "movies"

    def test_create_collection_twice_raises_error(
        self,
        clean_collection: Any,
    ) -> None:
        """Test creating a collection twice raises error."""
        create_movies_collection(client=clean_collection)

        with pytest.raises(CollectionAlreadyExistsError):
            create_movies_collection(client=clean_collection)

    def test_delete_nonexistent_collection_raises_error(
        self,
        clean_collection: Any,
    ) -> None:
        """Test deleting a nonexistent collection raises error."""
        with pytest.raises(CollectionNotFoundError):
            delete_movies_collection(client=clean_collection)


class TestIndexing:
    """Integration tests for document indexing."""

    def test_index_movies(
        self,
        clean_collection: Any,
        sample_integration_movies: list[Movie],
    ) -> None:
        """Test indexing movies into collection."""
        create_movies_collection(client=clean_collection)

        count = index_movies(sample_integration_movies, client=clean_collection)

        assert count == 3


class TestSearch:
    """Integration tests for search functionality."""

    _client: Any

    @pytest.fixture(autouse=True)
    def setup_collection(
        self,
        clean_collection: Any,
        sample_integration_movies: list[Movie],
    ) -> None:
        """Set up collection with sample data."""
        create_movies_collection(client=clean_collection)
        index_movies(sample_integration_movies, client=clean_collection)
        # Store client for use in tests
        self._client = clean_collection

    def test_keyword_search(self) -> None:
        """Test keyword search functionality."""
        result = keyword_search("Shawshank", client=self._client)

        assert result["found"] >= 1
        assert any("Shawshank" in hit["document"]["Title"] for hit in result["hits"])

    def test_keyword_search_no_results(self) -> None:
        """Test keyword search with no results."""
        result = keyword_search("NonexistentMovie12345", client=self._client)

        assert result["found"] == 0
        assert len(result["hits"]) == 0

    def test_faceted_search(self) -> None:
        """Test faceted search functionality."""
        result = faceted_search(
            "drama",
            query_by="Genre,Plot",
            facet_by="Director,Genre",
            client=self._client,
        )

        assert result["found"] >= 0
        # Facet counts should be present
        assert "facet_counts" in result

    def test_faceted_search_with_filter(self) -> None:
        """Test faceted search with filter."""
        result = faceted_search(
            "*",
            query_by="Title",
            facet_by="Director",
            filter_by="Year:1994",
            client=self._client,
        )

        # Should find Shawshank Redemption (1994)
        for hit in result["hits"]:
            assert hit["document"]["Year"] == "1994"
