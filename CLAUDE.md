# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Enterprise-grade Python SDK for Typesense search engine — featuring type-safe configuration, structured logging, comprehensive testing (90%+ coverage), and production-ready CI/CD pipeline.

## Architecture

### Package Structure

```
src/typesense_dangerzone/
├── __init__.py           # Public API exports
├── config.py             # Pydantic Settings (env-based configuration)
├── client.py             # Typesense client factory with caching
├── exceptions.py         # Custom exception hierarchy
├── logging_config.py     # Structured logging with structlog
└── collections/
    └── movies.py         # Movie collection operations (CRUD, search)

tests/
├── conftest.py           # Shared fixtures (mock client, sample data)
├── unit/                 # Unit tests (no external dependencies)
│   ├── test_config.py
│   ├── test_client.py
│   ├── test_exceptions.py
│   └── test_movies.py
└── integration/          # Integration tests (require Typesense)
    └── test_search.py
```

### Key Patterns

- **Configuration:** Pydantic Settings with `TYPESENSE_` prefix, SecretStr for API key
- **Client:** Cached singleton via `get_client()`, factory via `create_client()`
- **Errors:** Custom exceptions inherit from `TypesenseDangerzoneError`
- **Logging:** Structured JSON logging in production, console in development
- **Testing:** Unit tests mock the Typesense client, integration tests use real server

## Development Commands

```bash
# Start Typesense (required for integration tests)
docker-compose up -d

# Install dependencies (includes dev tools)
pip install -e ".[dev]"

# Run all pre-commit checks (ruff, mypy, bandit, detect-secrets)
pre-commit run --all-files

# Run tests with coverage
pytest --cov --cov-report=term-missing

# Run only unit tests (no Typesense required)
pytest tests/unit

# Run integration tests (Typesense required)
pytest tests/integration -m integration --no-cov

# Type checking
mypy src tests

# Linting and formatting
ruff check src tests
ruff format src tests
```

## Code Quality

All configuration is in `pyproject.toml`:

- **ruff:** Unified linter/formatter (replaces black, isort, flake8)
- **mypy:** Strict type checking with Pydantic plugin
- **pytest:** 80% coverage threshold (currently at 90%+)
- **bandit:** Security scanning
- **detect-secrets:** Credential leak prevention

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push/PR:

1. **Lint & Format** - ruff check, ruff format, mypy
2. **Security Scan** - bandit, pip-audit, detect-secrets
3. **Test Matrix** - Python 3.10, 3.11, 3.12 with Typesense container
4. **All Checks Pass** - Summary gate for branch protection

## Environment Variables

Required:
- `TYPESENSE_API_KEY` - API key for Typesense server

Optional (with defaults):
- `TYPESENSE_HOST` (localhost)
- `TYPESENSE_PORT` (8108)
- `TYPESENSE_PROTOCOL` (http)
- `TYPESENSE_CONNECTION_TIMEOUT_SECONDS` (5)

## Docker Setup

Typesense runs via Docker Compose on port 8108. API key is configured via `TYPESENSE_API_KEY` environment variable.

```bash
# Start with custom API key
TYPESENSE_API_KEY=your-key docker-compose up -d

# Or use .env file
cp .env.example .env
# Edit .env with your API key
docker-compose up -d
```
