# Typesense Dangerzone

[![CI](https://github.com/MysterionRise/typesense-dangerzone/actions/workflows/ci.yml/badge.svg)](https://github.com/MysterionRise/typesense-dangerzone/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Coverage 90%+](https://img.shields.io/badge/coverage-90%25+-brightgreen.svg)](https://github.com/MysterionRise/typesense-dangerzone)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Enterprise-grade Python SDK for [Typesense](https://typesense.org/) search engine** — featuring type-safe configuration, structured logging, comprehensive testing, and production-ready CI/CD pipeline.

Typesense is an open-source, typo-tolerant search engine and a modern alternative to Algolia and Elasticsearch.

## Features

- **Type-safe configuration** with Pydantic Settings and SecretStr
- **Structured logging** with structlog (JSON-ready for production)
- **Comprehensive error handling** with custom exception hierarchy
- **Full type hints** with mypy strict mode
- **90%+ test coverage** with pytest (unit + integration tests)
- **Production-ready CI/CD** with GitHub Actions (lint, security scan, matrix testing)
- **Secure credential management** via environment variables

## Quick Start

### Prerequisites

- Python 3.10+
- Docker and Docker Compose

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/MysterionRise/typesense-dangerzone.git
   cd typesense-dangerzone
   ```

2. **Set up environment:**

   ```bash
   cp .env.example .env
   # Edit .env and set your TYPESENSE_API_KEY
   ```

3. **Start Typesense:**

   ```bash
   docker-compose up -d
   ```

4. **Install the package:**

   ```bash
   pip install -e ".[dev]"
   ```

### Usage

```python
from typesense_dangerzone import get_client
from typesense_dangerzone.collections.movies import (
    create_movies_collection,
    index_movies,
    keyword_search,
    load_movies_from_file,
)

# Create collection
create_movies_collection()

# Load and index movies
movies = load_movies_from_file("data/movies.json")
index_movies(movies)

# Search
results = keyword_search("Legend")
for hit in results["hits"]:
    print(f"{hit['document']['Title']} ({hit['document']['Year']})")
```

## Configuration

Configuration is managed through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TYPESENSE_API_KEY` | API key for Typesense (required) | - |
| `TYPESENSE_HOST` | Typesense server hostname | `localhost` |
| `TYPESENSE_PORT` | Typesense server port | `8108` |
| `TYPESENSE_PROTOCOL` | Connection protocol (`http`/`https`) | `http` |
| `TYPESENSE_CONNECTION_TIMEOUT_SECONDS` | Connection timeout | `5` |

## Development

### Setup

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install --install-hooks
```

### Code Quality

```bash
# Run all pre-commit checks
pre-commit run --all-files

# Run linting
ruff check src tests

# Run type checking
mypy src tests

# Run tests
pytest

# Run tests with coverage
pytest --cov --cov-report=html
```

### Project Structure

```
typesense-dangerzone/
├── src/typesense_dangerzone/    # Main package
│   ├── __init__.py
│   ├── config.py                # Pydantic Settings configuration
│   ├── client.py                # Typesense client factory
│   ├── exceptions.py            # Custom exception hierarchy
│   ├── logging_config.py        # Structured logging setup
│   └── collections/
│       └── movies.py            # Movie collection operations
├── tests/
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── data/
│   └── movies.json              # Sample movie data
├── pyproject.toml               # Project configuration
└── docker-compose.yml           # Typesense container
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
