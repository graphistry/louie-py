"""Authentication handling for LouieAI client."""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, cast

import httpx
from graphistry.pygraphistry import GraphistryClient


class AuthManager:
    """Manages authentication and token refresh for Louie client."""

    def __init__(
        self,
        graphistry_client: Any | None = None,
        username: str | None = None,
        password: str | None = None,
        api_key: str | None = None,
        api: int = 3,
        server: str | None = None,
    ):
        """Initialize auth manager.

        Args:
            graphistry_client: Existing Graphistry client to use for auth
            username: Username for direct authentication
            password: Password for direct authentication
            api_key: API key for direct authentication
            api: API version (default: 3)
            server: Server URL for direct authentication
        """
        # Create GraphistryClient instance if none provided
        self._graphistry_client = graphistry_client or GraphistryClient()
        self._credentials = {
            "username": username,
            "password": password,
            "api_key": api_key,
            "api": api,
            "server": server,
        }
        self._last_auth_time: float = 0.0
        self._token_lifetime = 3600  # Default 1 hour, will be updated from response

    def get_token(self) -> str:
        """Get current auth token, refreshing if needed.

        Returns:
            Valid authentication token

        Raises:
            RuntimeError: If authentication fails
        """
        # Get token from our graphistry client instance
        token = self._graphistry_client.api_token()
        if not token and hasattr(self._graphistry_client, "refresh"):
            # Try to refresh using client's refresh method if available
            self._graphistry_client.refresh()
            token = self._graphistry_client.api_token()
        if not token:
            raise RuntimeError(
                "Failed to get authentication token from graphistry client"
            )
        return str(token)

    def get_auth_header(self) -> dict[str, str]:
        """Get authorization header with current token.

        Returns:
            Dictionary with Authorization header
        """
        token = self.get_token()
        return {"Authorization": f"Bearer {token}"}

    def refresh_token(self) -> None:
        """Force refresh the authentication token."""
        # Try the client's refresh method if available
        if hasattr(self._graphistry_client, "refresh"):
            self._graphistry_client.refresh()
        else:
            # Fall back to re-authentication using stored credentials
            self._refresh_auth()

    def _should_refresh_token(self) -> bool:
        """Check if token should be refreshed based on age."""
        if self._last_auth_time == 0:
            return False  # Never authenticated through us

        # Refresh if 90% of lifetime has passed
        elapsed = time.time() - self._last_auth_time
        return elapsed > (self._token_lifetime * 0.9)

    def _refresh_auth(self) -> None:
        """Refresh authentication using stored credentials."""
        if not any(self._credentials.values()):
            return  # No credentials stored

        # Build register kwargs with proper types
        register_kwargs: dict[str, Any] = {}
        if self._credentials["username"]:
            register_kwargs["username"] = self._credentials["username"]
        if self._credentials["password"]:
            register_kwargs["password"] = self._credentials["password"]
        if self._credentials["api_key"]:
            # graphistry uses 'key' parameter
            register_kwargs["key"] = self._credentials["api_key"]
        if self._credentials["api"]:
            register_kwargs["api"] = self._credentials["api"]
        if self._credentials["server"]:
            register_kwargs["server"] = self._credentials["server"]

        if register_kwargs:
            self._graphistry_client.register(**register_kwargs)
            self._last_auth_time = time.time()

    def _is_jwt_error(self, message: str) -> bool:
        """Check if error message indicates a JWT authentication error.

        Args:
            message: Error message to check

        Returns:
            True if this is a JWT-related error
        """
        if not message:
            return False

        message_lower = message.lower()
        jwt_indicators = ["jwt", "token expired", "authentication credentials"]

        return any(indicator in message_lower for indicator in jwt_indicators)

    def handle_auth_error(self, error: Exception) -> bool:
        """Handle authentication errors by attempting to re-authenticate.

        Args:
            error: The error that occurred

        Returns:
            True if re-authentication succeeded and should retry, False otherwise
        """
        # Only handle HTTPStatusError with 401 status
        if not isinstance(error, httpx.HTTPStatusError):
            return False

        if (
            not hasattr(error.response, "status_code")
            or error.response.status_code != 401
        ):
            return False

        # Check if this is specifically a JWT error
        error_detail = ""
        try:
            if hasattr(error.response, "text"):
                import json

                error_data = json.loads(error.response.text)
                error_detail = error_data.get("detail", "")
        except Exception:
            error_detail = str(error)

        if not self._is_jwt_error(error_detail):
            return False  # Not a JWT error, don't retry

        try:
            # Force refresh for JWT errors
            self.refresh_token()
            return True
        except Exception:
            return False


def auto_retry_auth[F: Callable[..., Any]](func: F) -> F:
    """Decorator to automatically retry on auth failures.

    This decorator will catch auth errors and attempt to refresh
    the token once before retrying the operation.
    """

    @wraps(func)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        try:
            return func(self, *args, **kwargs)
        except (httpx.HTTPStatusError, RuntimeError) as e:
            # Check if this might be an auth error
            if hasattr(self, "auth_manager") and self.auth_manager.handle_auth_error(e):
                # Auth refreshed, try once more
                return func(self, *args, **kwargs)
            else:
                # Not an auth error or refresh failed
                raise

    return cast(F, wrapper)
