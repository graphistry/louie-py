# Testing Guide

## Quick Start

```bash
# Run unit tests (fast, no credentials needed)
./scripts/test.sh

# Run integration tests (requires credentials)
./scripts/test.sh --integration

# Run all tests with coverage
./scripts/test.sh --all --coverage
```

## Test Categories

### Unit Tests (`tests/unit/`)
Fast tests with mocked dependencies. No credentials required.

```bash
./bin/uv run pytest tests/unit/ -v
```

### Integration Tests (`tests/integration/`)
Tests against real Louie API. Requires credentials in `.env` file:

```env
GRAPHISTRY_SERVER=your-server.example.com
GRAPHISTRY_USERNAME=your_username  
GRAPHISTRY_PASSWORD=your_password
```

```bash
./bin/uv run pytest tests/integration/ -v
```

## Writing Tests

### Unit Test Pattern
```python
import pytest
from unittest.mock import patch
from louieai import LouieClient

@pytest.mark.unit
def test_feature(mock_graphistry):
    with patch('louieai.client.graphistry') as mock_g:
        mock_g.api_token.return_value = "fake-token"
        
        client = LouieClient()
        result = client.some_method()
        
        assert result.success
```

### Integration Test Pattern
```python
import pytest
from tests.conftest import skip_if_no_credentials

@pytest.mark.integration
@skip_if_no_credentials
def test_real_api(real_client):
    response = real_client.ask("test query")
    assert response.thread_id.startswith("D_")
```

## Coverage Goals

- Unit tests: >80% coverage
- Focus on business logic
- Mock all external dependencies

```bash
# Generate coverage report
./bin/uv run pytest tests/unit/ --cov=louieai --cov-report=html
```

## Debugging

```bash
# Verbose output
./bin/uv run pytest -v

# Stop on first failure  
./bin/uv run pytest -x

# Drop into debugger on failure
./bin/uv run pytest --pdb

# Run specific test
./bin/uv run pytest tests/unit/test_client.py::test_method
```

## Mock Objects

Use shared mocks from `tests/unit/mocks.py`:

```python
from tests.unit.mocks import create_mock_client

def test_something():
    client = create_mock_client()
    response = client.ask("test")
    assert response.text == "Sample analysis response with insights"
```

## Best Practices

1. **Keep unit tests fast** - <1 second each
2. **Test one behavior** per test
3. **Use descriptive names** - `test_create_thread_with_valid_name()`
4. **Mock external dependencies** - no real API calls in unit tests
5. **Make tests deterministic** - avoid timing/order dependencies