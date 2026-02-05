# Contributing to Typesense Dangerzone

Thank you for your interest in contributing! This document outlines the development workflow and guidelines.

## Development Setup

1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/typesense-dangerzone.git
   cd typesense-dangerzone
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies:**

   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks:**

   ```bash
   pre-commit install --install-hooks
   ```

5. **Set up environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Development Workflow

### Creating a Branch

Create a branch from `main` for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Making Changes

1. **Write code** following the existing patterns and style
2. **Add tests** for new functionality
3. **Run quality checks** before committing:

   ```bash
   # Run all checks
   pre-commit run --all-files

   # Or run individually
   ruff check src tests
   ruff format src tests
   mypy src tests
   pytest
   ```

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/). Format:

```
<type>(<scope>): <description>

[optional body]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(search): add support for multi-field queries
fix(client): handle connection timeout gracefully
docs(readme): update installation instructions
test(movies): add integration tests for faceted search
```

### Running Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit

# Run only integration tests (requires Typesense running)
pytest tests/integration -m integration

# Run with coverage report
pytest --cov --cov-report=html
open htmlcov/index.html
```

### Code Style

- **Line length:** 88 characters (ruff default)
- **Imports:** Sorted by ruff (isort-compatible)
- **Type hints:** Required for all public functions
- **Docstrings:** Google style for public APIs

## Pull Request Process

1. **Ensure all checks pass:**
   - Pre-commit hooks
   - CI pipeline (lint, security, tests)
   - Coverage threshold (80%)

2. **Update documentation** if needed

3. **Write a clear PR description:**
   - What changes were made
   - Why the changes were necessary
   - How to test the changes

4. **Request review** from maintainers

5. **Address feedback** promptly

## Security

- **Never commit secrets** - use environment variables
- **Run security scans** before submitting:

  ```bash
  bandit -r src
  pip-audit
  detect-secrets scan
  ```

- **Report vulnerabilities** via GitHub Security Advisories

## Questions?

Open an issue with the `question` label or start a discussion.
