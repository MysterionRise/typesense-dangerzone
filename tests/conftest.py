"""Pytest fixtures for typesense-dangerzone tests."""

import os
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from typesense_dangerzone.collections.movies import Movie


@pytest.fixture(autouse=True)
def reset_caches() -> Generator[None, None, None]:
    """Reset all LRU caches before each test."""
    from typesense_dangerzone.client import get_client
    from typesense_dangerzone.config import get_settings

    get_settings.cache_clear()
    get_client.cache_clear()
    yield
    get_settings.cache_clear()
    get_client.cache_clear()


@pytest.fixture
def mock_env_vars() -> Generator[dict[str, str], None, None]:
    """Set up mock environment variables for testing."""
    env_vars = {
        "TYPESENSE_API_KEY": "test-api-key-12345",
        "TYPESENSE_HOST": "localhost",
        "TYPESENSE_PORT": "8108",
        "TYPESENSE_PROTOCOL": "http",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def sample_movies() -> list[Movie]:
    """Provide sample movie data for testing."""
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


@pytest.fixture
def mock_typesense_client() -> Generator[MagicMock, None, None]:
    """Create a mock Typesense client for unit tests."""
    mock_client = MagicMock()

    # Mock health check
    mock_client.operations.is_healthy.return_value = True

    # Mock collections
    mock_collection = MagicMock()
    mock_client.collections.__getitem__.return_value = mock_collection

    # Mock collection creation
    mock_client.collections.create.return_value = {
        "name": "movies",
        "num_documents": 0,
        "fields": [],
    }

    # Mock search results
    mock_collection.documents.search.return_value = {
        "found": 1,
        "hits": [
            {
                "document": {
                    "id": "tt0111161",
                    "Title": "The Shawshank Redemption",
                    "Year": "1994",
                },
                "highlight": {},
                "text_match": 100,
            }
        ],
        "facet_counts": [],
        "search_time_ms": 5,
    }

    # Mock import results
    mock_collection.documents.import_.return_value = [
        {"success": True},
        {"success": True},
        {"success": True},
    ]

    yield mock_client


@pytest.fixture
def mock_search_result() -> dict[str, Any]:
    """Provide a mock search result for testing."""
    return {
        "found": 2,
        "hits": [
            {
                "document": {
                    "id": "tt0111161",
                    "Title": "The Shawshank Redemption",
                    "Year": "1994",
                    "Genre": "Drama",
                    "Director": "Frank Darabont",
                    "imdbRating": "9.3",
                },
                "highlight": {"Title": {"snippet": "<mark>Shawshank</mark>"}},
                "text_match": 100,
            },
            {
                "document": {
                    "id": "tt0068646",
                    "Title": "The Godfather",
                    "Year": "1972",
                    "Genre": "Crime, Drama",
                    "Director": "Francis Ford Coppola",
                    "imdbRating": "9.2",
                },
                "highlight": {},
                "text_match": 80,
            },
        ],
        "facet_counts": [
            {
                "field_name": "Genre",
                "counts": [
                    {"value": "Drama", "count": 2},
                    {"value": "Crime", "count": 1},
                ],
            }
        ],
        "search_time_ms": 10,
    }
