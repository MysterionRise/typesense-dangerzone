"""Unit tests for movie collection operations."""

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from typesense.exceptions import ObjectAlreadyExists, ObjectNotFound

from typesense_dangerzone.collections.movies import (
    COLLECTION_NAME,
    MOVIES_SCHEMA,
    Movie,
    create_movies_collection,
    delete_movies_collection,
    faceted_search,
    index_movies,
    keyword_search,
    load_movies_from_file,
)
from typesense_dangerzone.exceptions import (
    CollectionAlreadyExistsError,
    CollectionNotFoundError,
    IndexingError,
    SearchError,
)


class TestMoviesSchema:
    """Tests for movies collection schema."""

    def test_schema_has_correct_name(self) -> None:
        """Test schema has correct collection name."""
        assert MOVIES_SCHEMA["name"] == COLLECTION_NAME
        assert COLLECTION_NAME == "movies"

    def test_schema_has_required_fields(self) -> None:
        """Test schema contains all required fields."""
        field_names = [f["name"] for f in MOVIES_SCHEMA["fields"]]

        assert "id" in field_names
        assert "Title" in field_names
        assert "Genre" in field_names
        assert "Director" in field_names


class TestCreateMoviesCollection:
    """Tests for create_movies_collection function."""

    def test_create_collection_success(self, mock_typesense_client: MagicMock) -> None:
        """Test successful collection creation."""
        result = create_movies_collection(client=mock_typesense_client)

        mock_typesense_client.collections.create.assert_called_once_with(MOVIES_SCHEMA)
        assert result["name"] == "movies"

    def test_create_collection_already_exists(
        self, mock_typesense_client: MagicMock
    ) -> None:
        """Test error when collection already exists."""
        mock_typesense_client.collections.create.side_effect = ObjectAlreadyExists(
            "Collection already exists"
        )

        with pytest.raises(CollectionAlreadyExistsError) as exc_info:
            create_movies_collection(client=mock_typesense_client)

        assert exc_info.value.collection_name == COLLECTION_NAME


class TestDeleteMoviesCollection:
    """Tests for delete_movies_collection function."""

    def test_delete_collection_success(self, mock_typesense_client: MagicMock) -> None:
        """Test successful collection deletion."""
        mock_typesense_client.collections.__getitem__.return_value.delete.return_value = {
            "name": "movies"
        }

        result = delete_movies_collection(client=mock_typesense_client)

        assert result["name"] == "movies"

    def test_delete_collection_not_found(
        self, mock_typesense_client: MagicMock
    ) -> None:
        """Test error when collection not found."""
        mock_typesense_client.collections.__getitem__.return_value.delete.side_effect = ObjectNotFound(
            "Collection not found"
        )

        with pytest.raises(CollectionNotFoundError) as exc_info:
            delete_movies_collection(client=mock_typesense_client)

        assert exc_info.value.collection_name == COLLECTION_NAME


class TestIndexMovies:
    """Tests for index_movies function."""

    def test_index_movies_success(
        self, mock_typesense_client: MagicMock, sample_movies: list[Movie]
    ) -> None:
        """Test successful movie indexing."""
        mock_typesense_client.collections.__getitem__.return_value.documents.import_.return_value = [
            {"success": True},
            {"success": True},
            {"success": True},
        ]

        result = index_movies(sample_movies, client=mock_typesense_client)

        assert result == 3

    def test_index_movies_empty_list(self, mock_typesense_client: MagicMock) -> None:
        """Test indexing empty list returns 0."""
        result = index_movies([], client=mock_typesense_client)

        assert result == 0

    def test_index_movies_partial_failure(
        self, mock_typesense_client: MagicMock, sample_movies: list[Movie]
    ) -> None:
        """Test error when some documents fail to index."""
        mock_typesense_client.collections.__getitem__.return_value.documents.import_.return_value = [
            {"success": True},
            {"success": False, "error": "Invalid document"},
            {"success": True},
        ]

        with pytest.raises(IndexingError) as exc_info:
            index_movies(sample_movies, client=mock_typesense_client)

        assert exc_info.value.details["failed_count"] == 1
        assert exc_info.value.details["total_count"] == 3

    def test_index_movies_collection_not_found(
        self, mock_typesense_client: MagicMock, sample_movies: list[Movie]
    ) -> None:
        """Test error when collection not found."""
        mock_typesense_client.collections.__getitem__.return_value.documents.import_.side_effect = ObjectNotFound(
            "Collection not found"
        )

        with pytest.raises(CollectionNotFoundError):
            index_movies(sample_movies, client=mock_typesense_client)


class TestLoadMoviesFromFile:
    """Tests for load_movies_from_file function."""

    def test_load_movies_from_file(self, sample_movies: list[Movie]) -> None:
        """Test loading movies from JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_movies, f)
            temp_path = Path(f.name)

        try:
            result = load_movies_from_file(temp_path)

            assert len(result) == 3
            assert result[0]["Title"] == "The Shawshank Redemption"
        finally:
            temp_path.unlink()

    def test_load_movies_adds_id_from_imdb(self) -> None:
        """Test that imdbID is used as id when id is missing."""
        movies_data = [
            {"Title": "Test Movie", "imdbID": "tt1234567"},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(movies_data, f)
            temp_path = Path(f.name)

        try:
            result = load_movies_from_file(temp_path)

            assert result[0]["id"] == "tt1234567"
        finally:
            temp_path.unlink()

    def test_load_movies_file_not_found(self) -> None:
        """Test error when file not found."""
        with pytest.raises(FileNotFoundError):
            load_movies_from_file("/nonexistent/path/movies.json")


class TestKeywordSearch:
    """Tests for keyword_search function."""

    def test_keyword_search_success(
        self, mock_typesense_client: MagicMock, mock_search_result: dict[str, Any]
    ) -> None:
        """Test successful keyword search."""
        mock_typesense_client.collections.__getitem__.return_value.documents.search.return_value = mock_search_result

        result = keyword_search("Shawshank", client=mock_typesense_client)

        assert result["found"] == 2
        assert len(result["hits"]) == 2

    def test_keyword_search_with_custom_query_by(
        self, mock_typesense_client: MagicMock, mock_search_result: dict[str, Any]
    ) -> None:
        """Test keyword search with custom query_by field."""
        mock_typesense_client.collections.__getitem__.return_value.documents.search.return_value = mock_search_result

        keyword_search("Drama", query_by="Genre", client=mock_typesense_client)

        call_args = (
            mock_typesense_client.collections.__getitem__().documents.search.call_args[
                0
            ][0]
        )
        assert call_args["query_by"] == "Genre"

    def test_keyword_search_collection_not_found(
        self, mock_typesense_client: MagicMock
    ) -> None:
        """Test error when collection not found."""
        mock_typesense_client.collections.__getitem__.return_value.documents.search.side_effect = ObjectNotFound(
            "Collection not found"
        )

        with pytest.raises(CollectionNotFoundError):
            keyword_search("test", client=mock_typesense_client)

    def test_keyword_search_error(self, mock_typesense_client: MagicMock) -> None:
        """Test error handling for search failures."""
        mock_typesense_client.collections.__getitem__.return_value.documents.search.side_effect = Exception(
            "Search failed"
        )

        with pytest.raises(SearchError) as exc_info:
            keyword_search("test", client=mock_typesense_client)

        assert "test" in str(exc_info.value.details)


class TestFacetedSearch:
    """Tests for faceted_search function."""

    def test_faceted_search_success(
        self, mock_typesense_client: MagicMock, mock_search_result: dict[str, Any]
    ) -> None:
        """Test successful faceted search."""
        mock_typesense_client.collections.__getitem__.return_value.documents.search.return_value = mock_search_result

        result = faceted_search("drama", client=mock_typesense_client)

        assert result["found"] == 2
        assert len(result["facet_counts"]) == 1

    def test_faceted_search_with_filter(
        self, mock_typesense_client: MagicMock, mock_search_result: dict[str, Any]
    ) -> None:
        """Test faceted search with filter."""
        mock_typesense_client.collections.__getitem__.return_value.documents.search.return_value = mock_search_result

        faceted_search(
            "drama",
            filter_by="Genre:=Drama",
            client=mock_typesense_client,
        )

        call_args = (
            mock_typesense_client.collections.__getitem__().documents.search.call_args[
                0
            ][0]
        )
        assert call_args["filter_by"] == "Genre:=Drama"

    def test_faceted_search_collection_not_found(
        self, mock_typesense_client: MagicMock
    ) -> None:
        """Test error when collection not found."""
        mock_typesense_client.collections.__getitem__.return_value.documents.search.side_effect = ObjectNotFound(
            "Collection not found"
        )

        with pytest.raises(CollectionNotFoundError):
            faceted_search("test", client=mock_typesense_client)
