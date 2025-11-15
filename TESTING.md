# Testing Guide

This document provides detailed information about testing the Typesense Hybrid Search Demo.

## Table of Contents

- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Backend Tests](#backend-tests)
- [Frontend Tests](#frontend-tests)
- [Integration Tests](#integration-tests)
- [Continuous Integration](#continuous-integration)
- [Writing New Tests](#writing-new-tests)

## Test Structure

```
typesense-hybrid-demo/
├── backend/
│   └── tests/
│       ├── __init__.py
│       ├── test_synth_data.py      # Data generation tests
│       └── test_integration.py     # Typesense integration tests
├── ui/
│   └── __tests__/
│       ├── components/
│       │   └── GeoControls.test.tsx
│       └── lib/
│           ├── typesenseAdapter.test.ts
│           └── api.test.ts
├── pytest.ini                       # pytest configuration
├── Makefile                         # Test commands
└── .github/workflows/ci.yml         # CI configuration
```

## Running Tests

### Quick Start

```bash
# All tests
make test

# Individual test suites
make test-backend
make test-frontend
make test-integration

# With coverage
cd backend && pytest --cov=. --cov-report=html
cd ui && npm test -- --coverage
```

## Backend Tests

### Test Framework
- **pytest** - Test framework
- **pytest-cov** - Coverage reporting
- **pytest-mock** - Mocking support

### Running Backend Tests

```bash
# All backend tests
cd backend
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=term --cov-report=html

# Specific test file
pytest tests/test_synth_data.py -v

# Specific test function
pytest tests/test_synth_data.py::TestProductGeneration::test_generates_valid_product -v

# Run with markers
pytest -m unit  # Unit tests only
pytest -m "not slow"  # Skip slow tests
```

### Test Coverage

**test_synth_data.py:**
- ✅ Product title generation
- ✅ Description generation
- ✅ Brand selection by category
- ✅ Full product document generation
- ✅ Geo-coordinate validation
- ✅ Brand document generation
- ✅ Data consistency and schema validation
- ✅ Deterministic random seeding

**test_integration.py:**
- ✅ Product schema validation
- ✅ Embedding field configuration
- ✅ Facet field configuration
- ✅ Brand schema validation
- ✅ Synonym configuration
- ✅ Override/curation rules
- ✅ Data generation output validation

### Writing Backend Tests

Example test structure:

```python
import pytest
from synth_data import generate_product

class TestProductGeneration:
    """Test product generation"""

    def test_generates_valid_product(self):
        """Test that a valid product is generated"""
        product = generate_product(1)

        assert product['id'] == '1'
        assert 'title' in product
        assert isinstance(product['price'], float)
        assert product['price'] > 0
```

## Frontend Tests

### Test Framework
- **Jest** - Test framework
- **React Testing Library** - Component testing
- **@testing-library/user-event** - User interaction simulation

### Running Frontend Tests

```bash
cd ui

# All tests
npm test

# Watch mode
npm run test:watch

# With coverage
npm run test:coverage

# Specific test file
npm test -- GeoControls.test

# Update snapshots
npm test -- -u
```

### Test Coverage

**GeoControls.test.tsx:**
- ✅ Component rendering
- ✅ Enable/disable toggle
- ✅ City preset selection
- ✅ Latitude/longitude inputs
- ✅ Radius slider
- ✅ "Use My Location" button

**typesenseAdapter.test.ts:**
- ✅ Adapter creation with defaults
- ✅ Custom alpha configuration
- ✅ Additional parameters
- ✅ Vector query configuration

**api.test.ts:**
- ✅ Query suggestions fetching
- ✅ Multi-search execution
- ✅ Error handling

### Writing Frontend Tests

Example test structure:

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import MyComponent from '../MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<MyComponent onClick={handleClick} />);

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalled();
  });
});
```

## Integration Tests

Integration tests verify the entire stack works together.

### Running Integration Tests

```bash
# Using Make (recommended)
make test-integration

# Manual steps
docker compose up -d typesense
docker compose run --rm backend python /app/synth_data.py
docker compose run --rm backend python /app/index_products.py
# ... run verification queries
docker compose down
```

### What's Tested

1. **Service Startup**
   - Typesense starts and becomes healthy
   - Backend can connect to Typesense
   - UI can serve requests

2. **Data Generation**
   - Products NDJSON is created
   - Brands NDJSON is created
   - Files contain valid JSON
   - Sufficient data is generated

3. **Indexing**
   - Collections are created
   - Documents are imported
   - Embeddings are generated
   - No import errors

4. **Search Functionality**
   - Basic keyword search works
   - Hybrid search with embeddings works
   - Faceting returns results
   - Geo-search filters correctly

### CI Integration Tests

GitHub Actions runs a comprehensive smoke test:

```yaml
- Start Typesense
- Wait for health check
- Run data generation
- Verify data files exist
- Run indexing
- Verify collections exist
- Test search queries
- Start UI
- Verify UI accessibility
- Clean up
```

## Continuous Integration

### GitHub Actions Workflow

The CI pipeline runs on every push and pull request:

**Jobs:**
1. `backend-tests` - Python tests with pytest
2. `frontend-tests` - React tests with Jest
3. `integration-tests` - Full stack verification
4. `docker-build` - Verify images build
5. `smoke-test` - End-to-end validation

### Viewing CI Results

- Go to **Actions** tab in GitHub
- Click on latest workflow run
- View job logs for details
- Download coverage artifacts

### CI Configuration

See [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for the complete configuration.

## Writing New Tests

### Backend Test Template

```python
# backend/tests/test_feature.py
import pytest
from module import function_to_test

class TestFeature:
    """Test description"""

    @pytest.fixture
    def sample_data(self):
        """Fixture for test data"""
        return {'key': 'value'}

    def test_basic_functionality(self, sample_data):
        """Test that basic functionality works"""
        result = function_to_test(sample_data)
        assert result is not None

    def test_edge_case(self):
        """Test edge case handling"""
        with pytest.raises(ValueError):
            function_to_test(None)
```

### Frontend Test Template

```typescript
// ui/__tests__/components/Feature.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import Feature from '../../src/components/Feature';

describe('Feature', () => {
  const defaultProps = {
    value: 'test',
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with default props', () => {
    render(<Feature {...defaultProps} />);
    expect(screen.getByText('test')).toBeInTheDocument();
  });

  it('calls onChange when interacted with', () => {
    render(<Feature {...defaultProps} />);
    fireEvent.click(screen.getByRole('button'));
    expect(defaultProps.onChange).toHaveBeenCalled();
  });
});
```

## Test Best Practices

### General
- ✅ Write tests for new features
- ✅ Keep tests isolated and independent
- ✅ Use descriptive test names
- ✅ Test edge cases and error conditions
- ✅ Maintain high test coverage (>80%)
- ✅ Mock external dependencies
- ✅ Clean up after tests

### Backend
- ✅ Use fixtures for reusable test data
- ✅ Mock Typesense client in unit tests
- ✅ Test with different data configurations
- ✅ Validate data schemas
- ✅ Check for proper error handling

### Frontend
- ✅ Test user interactions
- ✅ Verify accessibility
- ✅ Mock API calls
- ✅ Test component props and state
- ✅ Snapshot test for UI consistency
- ✅ Test responsive behavior

## Debugging Tests

### Backend

```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb

# Run specific test with debugging
pytest tests/test_file.py::test_function -s -v
```

### Frontend

```bash
# Debug mode
npm test -- --no-coverage

# Run single test
npm test -- -t "test name"

# Watch mode for debugging
npm run test:watch
```

## Code Coverage

### Viewing Coverage Reports

**Backend:**
```bash
cd backend
pytest --cov=. --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Frontend:**
```bash
cd ui
npm run test:coverage
open coverage/lcov-report/index.html
```

### Coverage Goals

- **Overall**: >80%
- **Critical paths**: >90%
- **New features**: 100%

## Troubleshooting

### Common Issues

**Tests fail locally but pass in CI:**
- Check Python/Node versions match CI
- Ensure dependencies are up to date
- Clear caches: `make clean`

**Import errors:**
- Verify PYTHONPATH includes project root
- Check virtual environment is activated

**Mocking issues:**
- Ensure mocks are reset between tests
- Use `jest.clearAllMocks()` in `beforeEach`

**Timeout errors:**
- Increase timeout for slow tests
- Use `pytest.mark.slow` for long tests

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Jest documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Happy Testing! 🧪**
