"""Movie collection operations for Typesense."""

import json
from pathlib import Path
from typing import Any, TypedDict

from typesense.exceptions import ObjectAlreadyExists, ObjectNotFound

from typesense_dangerzone.client import get_client
from typesense_dangerzone.exceptions import (
    CollectionAlreadyExistsError,
    CollectionNotFoundError,
    IndexingError,
    SearchError,
)
from typesense_dangerzone.logging_config import get_logger

logger = get_logger(__name__)

# Collection name constant
COLLECTION_NAME = "movies"

# Schema definition for movies collection
MOVIES_SCHEMA: dict[str, Any] = {
    "name": COLLECTION_NAME,
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "Title", "type": "string"},
        {"name": "Year", "type": "string", "optional": True},
        {"name": "Genre", "type": "string", "optional": True, "facet": True},
        {"name": "Director", "type": "string", "optional": True, "facet": True},
        {"name": "imdbRating", "type": "string", "optional": True},
        {"name": "Plot", "type": "string", "optional": True},
    ],
    "default_sorting_field": None,
}


class Movie(TypedDict, total=False):
    """Type definition for movie documents."""

    id: str
    Title: str
    Year: str
    Genre: str
    Director: str
    imdbRating: str
    Plot: str


class SearchHit(TypedDict):
    """Type definition for search result hits."""

    document: Movie
    highlight: dict[str, Any]
    text_match: int


class SearchResult(TypedDict):
    """Type definition for search results."""

    found: int
    hits: list[SearchHit]
    facet_counts: list[dict[str, Any]]
    search_time_ms: int


def create_movies_collection(
    client: Any | None = None,
) -> dict[str, Any]:
    """Create the movies collection with predefined schema.

    Args:
        client: Optional Typesense client. Uses cached client if not provided.

    Returns:
        The created collection metadata.

    Raises:
        CollectionAlreadyExistsError: If collection already exists.
    """
    if client is None:
        client = get_client()

    try:
        result = client.collections.create(MOVIES_SCHEMA)
        logger.info("collection_created", collection_name=COLLECTION_NAME)
        return dict(result)
    except ObjectAlreadyExists as e:
        raise CollectionAlreadyExistsError(COLLECTION_NAME) from e


def delete_movies_collection(
    client: Any | None = None,
) -> dict[str, Any]:
    """Delete the movies collection.

    Args:
        client: Optional Typesense client. Uses cached client if not provided.

    Returns:
        The deleted collection metadata.

    Raises:
        CollectionNotFoundError: If collection does not exist.
    """
    if client is None:
        client = get_client()

    try:
        result = client.collections[COLLECTION_NAME].delete()
        logger.info("collection_deleted", collection_name=COLLECTION_NAME)
        return dict(result)
    except ObjectNotFound as e:
        raise CollectionNotFoundError(COLLECTION_NAME) from e


def index_movies(
    movies: list[Movie],
    client: Any | None = None,
) -> int:
    """Index a list of movies into the collection.

    Args:
        movies: List of movie documents to index.
        client: Optional Typesense client. Uses cached client if not provided.

    Returns:
        Number of successfully indexed documents.

    Raises:
        IndexingError: If indexing fails for any documents.
        CollectionNotFoundError: If collection does not exist.
    """
    if client is None:
        client = get_client()

    if not movies:
        logger.warning("index_movies_empty_list")
        return 0

    try:
        results = client.collections[COLLECTION_NAME].documents.import_(
            movies, {"action": "upsert"}
        )
    except ObjectNotFound as e:
        raise CollectionNotFoundError(COLLECTION_NAME) from e

    # Count successes and failures
    success_count = 0
    failed_count = 0

    for result in results:
        if result.get("success", False):
            success_count += 1
        else:
            failed_count += 1
            logger.warning(
                "document_index_failed",
                error=result.get("error"),
                document=result.get("document"),
            )

    logger.info(
        "movies_indexed",
        success_count=success_count,
        failed_count=failed_count,
        total=len(movies),
    )

    if failed_count > 0:
        raise IndexingError(
            f"Failed to index {failed_count} of {len(movies)} documents",
            failed_count=failed_count,
            total_count=len(movies),
        )

    return success_count


def load_movies_from_file(file_path: Path | str) -> list[Movie]:
    """Load movies from a JSON file.

    Args:
        file_path: Path to the JSON file containing movie data.

    Returns:
        List of movie documents.

    Raises:
        FileNotFoundError: If file does not exist.
        json.JSONDecodeError: If file is not valid JSON.
    """
    path = Path(file_path)
    logger.debug("loading_movies_from_file", file_path=str(path))

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Ensure each movie has an id field
    movies: list[Movie] = []
    for item in data:
        movie = dict(item)
        if "id" not in movie and "imdbID" in movie:
            movie["id"] = movie["imdbID"]
        movies.append(Movie(**movie))  # type: ignore[typeddict-item]

    logger.info("movies_loaded_from_file", count=len(movies), file_path=str(path))
    return movies


def keyword_search(
    query: str,
    query_by: str = "Title",
    client: Any | None = None,
    per_page: int = 10,
) -> SearchResult:
    """Perform a keyword search on the movies collection.

    Args:
        query: Search query string.
        query_by: Field(s) to search. Comma-separated for multiple fields.
        client: Optional Typesense client. Uses cached client if not provided.
        per_page: Number of results per page.

    Returns:
        Search results with hits and metadata.

    Raises:
        SearchError: If search operation fails.
        CollectionNotFoundError: If collection does not exist.
    """
    if client is None:
        client = get_client()

    search_params: dict[str, Any] = {
        "q": query,
        "query_by": query_by,
        "per_page": per_page,
    }

    try:
        result = client.collections[COLLECTION_NAME].documents.search(search_params)
        logger.info(
            "keyword_search_completed",
            query=query,
            found=result.get("found", 0),
            search_time_ms=result.get("search_time_ms"),
        )
        return SearchResult(
            found=result.get("found", 0),
            hits=result.get("hits", []),
            facet_counts=result.get("facet_counts", []),
            search_time_ms=result.get("search_time_ms", 0),
        )
    except ObjectNotFound as e:
        raise CollectionNotFoundError(COLLECTION_NAME) from e
    except Exception as e:
        raise SearchError(
            message=f"Keyword search failed: {e}",
            query=query,
            collection_name=COLLECTION_NAME,
        ) from e


def faceted_search(
    query: str,
    query_by: str = "Title,Plot",
    facet_by: str = "Director,Genre",
    client: Any | None = None,
    per_page: int = 10,
    filter_by: str | None = None,
) -> SearchResult:
    """Perform a faceted search on the movies collection.

    Args:
        query: Search query string.
        query_by: Field(s) to search. Comma-separated for multiple fields.
        facet_by: Field(s) to facet by. Comma-separated for multiple fields.
        client: Optional Typesense client. Uses cached client if not provided.
        per_page: Number of results per page.
        filter_by: Optional filter expression.

    Returns:
        Search results with hits, facet counts, and metadata.

    Raises:
        SearchError: If search operation fails.
        CollectionNotFoundError: If collection does not exist.
    """
    if client is None:
        client = get_client()

    search_params: dict[str, Any] = {
        "q": query,
        "query_by": query_by,
        "facet_by": facet_by,
        "per_page": per_page,
    }

    if filter_by:
        search_params["filter_by"] = filter_by

    try:
        result = client.collections[COLLECTION_NAME].documents.search(search_params)
        logger.info(
            "faceted_search_completed",
            query=query,
            found=result.get("found", 0),
            facet_counts=len(result.get("facet_counts", [])),
            search_time_ms=result.get("search_time_ms"),
        )
        return SearchResult(
            found=result.get("found", 0),
            hits=result.get("hits", []),
            facet_counts=result.get("facet_counts", []),
            search_time_ms=result.get("search_time_ms", 0),
        )
    except ObjectNotFound as e:
        raise CollectionNotFoundError(COLLECTION_NAME) from e
    except Exception as e:
        raise SearchError(
            message=f"Faceted search failed: {e}",
            query=query,
            collection_name=COLLECTION_NAME,
        ) from e
