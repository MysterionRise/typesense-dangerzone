# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An enterprise-grade Python project demonstrating Typesense search capabilities. Uses a proper Python package structure with type safety, structured logging, and comprehensive testing.

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
```

### Key Patterns

- **Configuration:** Uses Pydantic Settings with `TYPESENSE_` prefix for all env vars
- **Client:** Cached singleton via `get_client()`, factory via `create_client()`
- **Errors:** Custom exceptions inherit from `TypesenseDangerzoneError`
- **Logging:** Structured JSON logging in production, console in development

## Development Commands

```bash
# Start Typesense (required before running scripts)
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
pytest tests/integration -m integration

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
- **pytest:** 80% coverage threshold, separate unit/integration markers
- **bandit:** Security scanning
- **detect-secrets:** Credential leak prevention

## Environment Variables

Required:
- `TYPESENSE_API_KEY` - API key for Typesense server

Optional (with defaults):
- `TYPESENSE_HOST` (localhost)
- `TYPESENSE_PORT` (8108)
- `TYPESENSE_PROTOCOL` (http)

## Docker Setup

Typesense runs via Docker Compose on port 8108. API key is configured via `TYPESENSE_API_KEY` environment variable (default: `xyz` for local development).

```bash
# Start with custom API key
TYPESENSE_API_KEY=your-key docker-compose up -d
```
