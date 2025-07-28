# Testing Guide

This guide covers testing the Louie.ai Python client, including unit tests and integration tests.

## Test Organization

Tests are split into two main categories:

- **Unit Tests** (`tests/unit/`): Fast tests with no external dependencies
- **Integration Tests** (`tests/integration/`): Tests against real Louie API

## Quick Start

```bash
# Run unit tests (default)
./scripts/test.sh

# Run integration tests
./scripts/test.sh --integration

# Run all tests with coverage
./scripts/test.sh --all --coverage

# Get help
./scripts/test.sh --help
```

## Running Tests

### Unit Tests

Unit tests don't require any credentials and test the client logic in isolation:

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=louieai

# Run specific test file
pytest tests/unit/test_documentation.py -v

# Run tests matching pattern
pytest tests/unit/ -k "test_create"
```

### Integration Tests

Integration tests connect to a real Louie instance and require credentials.

#### Setting Up Credentials

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your test credentials:
   ```env
   GRAPHISTRY_SERVER=your-server.example.com
   GRAPHISTRY_USERNAME=your_username
   GRAPHISTRY_PASSWORD=your_password
   LOUIE_SERVER=https://louie.your-server.com  # Optional
   ```

3. Run integration tests:
   ```bash
   pytest tests/integration/ -v
   
   # Or using the test script
   ./scripts/test.sh --integration
   ```

**Important Security Notes:**
- Never commit credentials to git
- The `.env` file is git-ignored for security
- Use separate test accounts when possible
- Rotate credentials regularly

#### Environment Variables

You can also set credentials via environment variables:

```bash
export GRAPHISTRY_SERVER=your-server.example.com
export GRAPHISTRY_USERNAME=your_username
export GRAPHISTRY_PASSWORD=your_password

pytest tests/integration/
```

## Test Categories

### Documentation Tests
Tests all code examples in the documentation to ensure they work:

```bash
pytest tests/unit/test_documentation.py -v
```

### Client Tests
Core client functionality including thread management and API calls:

```bash
pytest tests/unit/test_client.py -v
```

### Authentication Tests
Auth manager and retry logic:

```bash
pytest tests/unit/test_auth.py -v
```

## Writing Tests

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, patch
from louieai import LouieClient

@pytest.mark.unit
class TestMyFeature:
    def test_create_thread(self, mock_graphistry):
        """Test thread creation with mocked backend."""
        # Mock the API response
        with patch('louieai.client.graphistry') as mock_g:
            mock_g.api_token.return_value = "fake-token"
            
            client = LouieClient()
            thread = client.create_thread(name="Test")
            
            assert thread.name == "Test"
```

### Integration Test Example

```python
import pytest
from tests.conftest import skip_if_no_credentials

@pytest.mark.integration
@skip_if_no_credentials
class TestRealAPI:
    def test_real_query(self, real_client):
        """Test with real Louie instance."""
        response = real_client.ask("Hello, how are you?")
        
        assert response.thread_id.startswith("D_")
        assert len(response.elements) > 0
```

## Continuous Integration

The project uses GitHub Actions for CI. Tests run automatically on:
- Every push to main/develop branches
- Every pull request

### CI Configuration

```yaml
# .github/workflows/test.yml
- name: Run Unit Tests
  run: pytest tests/unit/ --cov

- name: Run Integration Tests
  if: ${{ secrets.GRAPHISTRY_USERNAME != '' }}
  env:
    GRAPHISTRY_USERNAME: ${{ secrets.GRAPHISTRY_USERNAME }}
    GRAPHISTRY_PASSWORD: ${{ secrets.GRAPHISTRY_PASSWORD }}
  run: pytest tests/integration/
```

## Test Coverage

### Generate Coverage Report

```bash
# Terminal report
pytest tests/unit/ --cov=louieai --cov-report=term-missing

# HTML report
pytest tests/unit/ --cov=louieai --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest tests/unit/ --cov=louieai --cov-report=xml
```

### Coverage Goals
- Unit tests: >80% coverage
- Focus on business logic
- Mock external dependencies

## Debugging Tests

### Verbose Output
```bash
pytest -v   # Verbose test names
pytest -vv  # Very verbose with full diffs
pytest -s   # Show print statements
```

### Debug Failed Tests
```bash
# Drop into debugger on failure
pytest --pdb

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

### Running Specific Tests
```bash
# Run specific test file
pytest tests/unit/test_client.py

# Run specific test class
pytest tests/unit/test_client.py::TestLouieClient

# Run specific test method
pytest tests/unit/test_client.py::TestLouieClient::test_create_thread
```

## Mock Objects

The test suite includes comprehensive mocks in `tests/unit/mocks.py`:

- `MockDataFrame`: Simulates pandas DataFrame behavior
- `MockResponse`: Simulates API response objects
- `MockThread`: Simulates conversation threads
- `create_mock_client()`: Creates a fully mocked LouieClient

Example usage:

```python
from tests.unit.mocks import create_mock_client

def test_something():
    client = create_mock_client()
    response = client.ask("test")
    assert response.text == "Sample analysis response with insights"
```

## Best Practices

1. **Keep tests fast**: Unit tests should run in <1 second each
2. **Use fixtures**: Share common setup code via pytest fixtures
3. **Test one thing**: Each test should verify a single behavior
4. **Clear names**: Test names should describe what they test
5. **Deterministic**: Tests should not depend on timing or order
6. **Isolation**: Tests should not affect each other
7. **No real API calls in unit tests**: Always use mocks

## Troubleshooting

### Import Errors
```bash
# Ensure running from project root
cd /path/to/louie-py
pytest tests/

# Install in development mode
pip install -e ".[dev]"
```

### Tests Skipped
- Check pytest markers: `@pytest.mark.unit` or `@pytest.mark.integration`
- Integration tests skip without credentials
- Check `LOUIE_TEST_MODE` environment variable

### Flaky Tests
- Look for timing dependencies
- Ensure proper mocking
- Check for test order dependencies
- Use deterministic test data

### Missing Dependencies
```bash
# Install all dev dependencies
uv sync --dev

# Or with pip
pip install -e ".[dev]"
```

## Advanced Testing

### Testing with Different Python Versions
```bash
# Using UV
uv run --python 3.8 pytest tests/unit/
uv run --python 3.12 pytest tests/unit/

# Using tox (if configured)
tox -e py38,py312
```

### Parallel Test Execution
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto tests/unit/
```

### Test Profiling
```bash
# Profile test execution time
pytest --durations=10

# Generate test timing report
pytest --junit-xml=test-results.xml
```