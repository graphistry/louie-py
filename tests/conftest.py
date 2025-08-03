"""Shared pytest configuration and fixtures."""

import os
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Python version check
MIN_PYTHON_VERSION = (3, 10)
CURRENT_PYTHON_VERSION = sys.version_info[:2]

if CURRENT_PYTHON_VERSION < MIN_PYTHON_VERSION:
    import warnings

    # Get the recommended command based on available tools
    recommended_cmd = None
    if os.path.exists("uv.lock") or os.path.exists("pyproject.toml"):
        recommended_cmd = "./scripts/pytest.sh"
        if not os.path.exists("scripts/pytest.sh"):
            recommended_cmd = "uv run python -m pytest"
    else:
        recommended_cmd = "python3.10 -m pytest"

    current_version = ".".join(map(str, CURRENT_PYTHON_VERSION))
    min_version = ".".join(map(str, MIN_PYTHON_VERSION))
    warning_msg = (
        f"\n⚠️  WARNING: You are using Python {current_version}, "
        f"but this project requires Python {min_version} or higher.\n"
        f"   Recommended: Use '{recommended_cmd}' instead of 'pytest' directly.\n"
        f"   This ensures the correct Python version and dependencies are used.\n"
    )
    warnings.warn(warning_msg, UserWarning, stacklevel=2)

    # Print to stderr for better visibility
    print(warning_msg, file=sys.stderr)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# Pytest markers
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test (no external dependencies)"
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as an integration test (requires credentials)",
    )
    config.addinivalue_line("markers", "slow: mark test as slow running")


# Test mode detection
def get_test_mode() -> str:
    """Get the current test mode from environment."""
    return os.environ.get("LOUIE_TEST_MODE", "unit").lower()


def should_run_integration_tests() -> bool:
    """Check if integration tests should run."""
    # Check explicit test mode
    if get_test_mode() == "integration":
        return True

    # Check if credentials are available
    required_vars = ["GRAPHISTRY_SERVER", "GRAPHISTRY_USERNAME", "GRAPHISTRY_PASSWORD"]
    return all(os.environ.get(var) for var in required_vars)


# Shared fixtures
@pytest.fixture
def mock_graphistry():
    """Mock graphistry module."""
    mock = Mock()
    mock.register = Mock()
    mock.api_token = Mock(return_value="fake-token-123")
    mock.nodes = Mock(return_value=mock)
    mock.edges = Mock(return_value=mock)
    return mock


@pytest.fixture
def mock_client():
    """Create a mock LouieClient for unit tests."""
    from tests.unit.mocks import create_mock_client

    return create_mock_client()


@pytest.fixture
def test_credentials():
    """Load test credentials from environment."""
    from tests.utils import load_test_credentials

    return load_test_credentials()


@pytest.fixture
def real_client(test_credentials):
    """Create a real LouieClient for integration tests."""
    if not test_credentials:
        pytest.skip("No test credentials available")

    import graphistry

    from louieai._client import LouieClient

    # Register with Graphistry
    graphistry.register(
        api=test_credentials.get("api_version", 3),
        server=test_credentials["server"],
        username=test_credentials["username"],
        password=test_credentials["password"],
    )

    # Create Louie client
    louie_server = test_credentials.get("louie_server", "https://louie-dev.grph.xyz")
    return LouieClient(server_url=louie_server)


# Test data fixtures
@pytest.fixture
def sample_dataframe_data():
    """Sample data for DataFrame mocking."""
    return {
        "source_ip": ["192.168.1.1", "10.0.0.1", "172.16.0.1"],
        "user": ["alice", "bob", "charlie"],
        "value": [100, 200, 300],
        "customer_id": ["cust001", "cust002", "cust003"],
        "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03"],
    }


@pytest.fixture
def sample_thread_id():
    """Sample thread ID for testing."""
    return "D_test_thread_001"


# Skip decorators
def skip_if_no_credentials(func):
    """Skip test if no credentials are available."""
    return pytest.mark.skipif(
        not should_run_integration_tests(),
        reason="Integration test credentials not available",
    )(func)


def skip_if_integration_mode(func):
    """Skip test if running in integration mode only."""
    return pytest.mark.skipif(
        get_test_mode() == "integration", reason="Unit test skipped in integration mode"
    )(func)


@pytest.fixture(scope="session", autouse=True)
def prevent_global_cursor_init():
    """Prevent global cursor from making real connections during tests."""
    # Patch the notebook module's _global_cursor to prevent initialization
    import louieai.notebook

    # Save original value
    original_global_cursor = louieai.notebook._global_cursor

    # Set to a mock to prevent real initialization
    mock_cursor = Mock()
    mock_cursor.text = ""
    mock_cursor.df = None
    mock_cursor._client = Mock()
    mock_cursor.__call__ = Mock(return_value=mock_cursor)

    louieai.notebook._global_cursor = mock_cursor

    yield

    # Restore original
    louieai.notebook._global_cursor = original_global_cursor
