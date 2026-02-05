"""Collection-specific operations for Typesense."""

from typesense_dangerzone.collections.movies import (
    MOVIES_SCHEMA,
    Movie,
    create_movies_collection,
    delete_movies_collection,
    faceted_search,
    index_movies,
    keyword_search,
)

__all__ = [
    "MOVIES_SCHEMA",
    "Movie",
    "create_movies_collection",
    "delete_movies_collection",
    "faceted_search",
    "index_movies",
    "keyword_search",
]
