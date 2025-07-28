"""Test utilities for Louie.ai client."""

import os

from dotenv import load_dotenv


def load_test_credentials() -> dict[str, str] | None:
    """Load test credentials from environment variables.

    Returns:
        Dictionary with server, username, and password if all are set.
        None if any required credential is missing.
    """
    # Load from .env file if it exists
    load_dotenv()

    # Get credentials from environment
    server = os.getenv("GRAPHISTRY_SERVER")
    username = os.getenv("GRAPHISTRY_USERNAME")
    password = os.getenv("GRAPHISTRY_PASSWORD")
    api_version = os.getenv("GRAPHISTRY_API_VERSION", "3")

    # Check if all required credentials are present
    if not all([server, username, password]):
        return None

    return {
        "server": server,
        "username": username,
        "password": password,
        "api_version": int(api_version),
    }


def skip_if_no_credentials(test_func):
    """Decorator to skip tests if credentials are not available.

    Use this for integration tests that require real Louie instance access.
    """
    import pytest

    def wrapper(*args, **kwargs):
        if load_test_credentials() is None:
            pytest.skip(
                "Test credentials not configured. "
                "Set GRAPHISTRY_SERVER, GRAPHISTRY_USERNAME, "
                "and GRAPHISTRY_PASSWORD environment variables."
            )
        return test_func(*args, **kwargs)

    return wrapper
