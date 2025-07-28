# Testing Guide

This guide covers the testing setup for the LouieAI Python client.

## Test Organization

Tests are organized into two main categories:

### Unit Tests (`tests/unit/`)
- Run without external dependencies
- Use mocks for all external services
- Fast and deterministic
- Should always pass locally

### Integration Tests (`tests/integration/`)
- Require real Louie API access
- Need valid credentials
- Test actual API behavior
- May be slower and depend on network

## Running Tests

### Quick Start

```bash
# Run unit tests (default)
./scripts/test.sh

# Run integration tests
./scripts/test.sh --integration

# Run all tests
./scripts/test.sh --all

# Run with coverage
./scripts/test.sh --coverage
```

### Using pytest directly

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only  
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_documentation.py -v

# With coverage
pytest tests/unit/ --cov=louieai --cov-report=html
```

### Environment Variables

```bash
# Test mode selection
export LOUIE_TEST_MODE=unit      # Default
export LOUIE_TEST_MODE=integration
export LOUIE_TEST_MODE=all

# Integration test credentials
export GRAPHISTRY_SERVER=your-server.com
export GRAPHISTRY_USERNAME=your-username
export GRAPHISTRY_PASSWORD=your-password
export LOUIE_SERVER=https://louie.your-server.com  # Optional
```

### Using .env file

Create a `.env` file for credentials (git-ignored):

```env
GRAPHISTRY_SERVER=graphistry-dev.grph.xyz
GRAPHISTRY_USERNAME=testuser
GRAPHISTRY_PASSWORD=testpass
LOUIE_SERVER=https://louie-dev.grph.xyz
```

## Test Categories

### Documentation Tests
Test all code examples in documentation:
```bash
pytest tests/unit/test_documentation.py -v
```

### Client Tests
Test LouieClient functionality:
```bash
pytest tests/unit/test_client.py -v
```

### Authentication Tests
Test auth handling and retry logic:
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
    def test_something(self):
        # Use mocks for external dependencies
        with patch('louieai.client.graphistry') as mock_g:
            mock_g.api_token.return_value = "fake-token"
            client = LouieClient()
            # Test your feature
```

### Integration Test Example

```python
import pytest
from conftest import skip_if_no_credentials

@pytest.mark.integration
@skip_if_no_credentials
class TestRealAPI:
    def test_real_query(self, real_client):
        response = real_client.ask("Hello")
        assert response.thread_id.startswith("D_")
```

## CI/CD Integration

Tests run automatically on:
- Every push to main/develop
- Every pull request

The CI pipeline:
1. Runs unit tests for all Python versions
2. Runs integration tests if credentials are available
3. Generates coverage reports
4. Builds documentation

## Mock Objects

The test suite includes comprehensive mocks in `tests/unit/mocks.py`:

- `MockDataFrame`: Simulates pandas DataFrame
- `MockResponse`: Simulates API responses
- `MockThread`: Simulates conversation threads
- `create_mock_client()`: Creates fully mocked client

## Debugging Failed Tests

### Verbose output
```bash
pytest tests/unit/test_client.py::TestLouieClient::test_create_thread -vv
```

### Drop into debugger
```bash
pytest tests/unit/test_client.py --pdb
```

### Print statements
```python
def test_something(self, capsys):
    print("Debug info")
    # ... test code ...
    captured = capsys.readouterr()
    assert "Debug info" in captured.out
```

## Coverage Reports

### Generate HTML coverage report
```bash
pytest tests/unit/ --cov=louieai --cov-report=html
open htmlcov/index.html
```

### Coverage requirements
- Unit tests should maintain >80% coverage
- Focus on testing business logic
- Mock external dependencies

## Best Practices

1. **Keep tests fast**: Unit tests should run in <1 second each
2. **Use fixtures**: Share common setup code
3. **Test one thing**: Each test should verify a single behavior
4. **Clear names**: Test names should describe what they test
5. **Deterministic**: Tests should not depend on timing or order
6. **Isolation**: Tests should not affect each other

## Troubleshooting

### Import errors
- Ensure you're running from project root
- Check PYTHONPATH includes src directory

### Missing credentials
- Integration tests skip when no credentials
- Set environment variables or use .env file

### Flaky tests
- Check for timing dependencies
- Ensure proper mocking
- Use deterministic test data