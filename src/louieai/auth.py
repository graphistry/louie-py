"""Authentication handling for LouieAI client."""

from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

import httpx
from graphistry.pygraphistry import GraphistryClient

# TypeVar for decorator type preservation
F = TypeVar("F", bound=Callable[..., Any])


def get_anonymous_token(server_url: str, timeout: float = 20.0) -> str:
    """Request an anonymous token from a Louie desktop server.

    Args:
        server_url: Base URL for the Louie server (Tornado/Streamlit port)
        timeout: Request timeout in seconds

    Returns:
        Anonymous bearer token

    Raises:
        RuntimeError: If the endpoint is unavailable or returns an error
    """
    url = f"{server_url.rstrip('/')}/auth/anonymous"
    try:
        response = httpx.post(url, timeout=timeout)
    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Failed to request anonymous token from {url}: {exc}"
        ) from exc

    if response.status_code != 200:
        hint = ""
        if response.status_code in {401, 403, 404}:
            hint = " Anonymous auth may be disabled on this server."
        detail = response.text.strip()
        status = response.status_code
        msg = f"Anonymous auth request failed with status {status} at {url}.{hint}"
        if detail:
            msg += f" Response: {detail}"
        raise RuntimeError(msg)

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"Anonymous auth response was not valid JSON from {url}."
        ) from exc

    if not data.get("success"):
        raise RuntimeError(f"Anonymous auth failed: {data}")

    token = data.get("token")
    if not token:
        raise RuntimeError(f"Anonymous auth response missing token: {data}")

    return str(token)


class AuthManager:
    """Manages authentication and token refresh for Louie client."""

    def __init__(
        self,
        graphistry_client: Any | None = None,
        username: str | None = None,
        password: str | None = None,
        api_key: str | None = None,
        personal_key_id: str | None = None,
        personal_key_secret: str | None = None,
        org_name: str | None = None,
        api: int = 3,
        server: str | None = None,
        graphistry_server: str | None = None,
        token: str | None = None,
        anonymous: bool = False,
        anonymous_timeout: float = 20.0,
        anonymous_server_url: str | None = None,
    ):
        """Initialize auth manager.

        Args:
            graphistry_client: Existing Graphistry client to use for auth
            username: Username for direct authentication
            password: Password for direct authentication
            api_key: API key for direct authentication (legacy)
            personal_key_id: Personal key ID for service account authentication
            personal_key_secret: Personal key secret for service account authentication
            org_name: Organization name (optional for all auth methods)
            api: API version (default: 3)
            graphistry_server: Graphistry server URL for direct authentication
            token: Optional pre-fetched bearer token (anonymous or Graphistry)
            anonymous: Use anonymous auth via /auth/anonymous (local desktop only)
            anonymous_timeout: Timeout for /auth/anonymous in seconds
            anonymous_server_url: Server URL for anonymous auth (Tornado/Streamlit)
        """
        if server is not None:
            raise ValueError(
                "server is no longer supported; use graphistry_server instead."
            )
        self._anonymous_enabled = anonymous
        self._token = token
        self._anonymous_timeout = anonymous_timeout
        self._anonymous_server_url = (
            anonymous_server_url.rstrip("/") if anonymous_server_url else None
        )
        if self._anonymous_enabled:
            if any(
                [
                    graphistry_client is not None,
                    username,
                    password,
                    api_key,
                    personal_key_id,
                    personal_key_secret,
                    graphistry_server,
                ]
            ):
                raise ValueError(
                    "Anonymous auth cannot be combined with Graphistry credentials."
                )
            if self._token is None and not self._anonymous_server_url:
                raise ValueError("Anonymous auth requires a server URL or a token.")
        elif self._token is not None and any(
            [
                graphistry_client is not None,
                username,
                password,
                api_key,
                personal_key_id,
                personal_key_secret,
                graphistry_server,
            ]
        ):
            raise ValueError(
                "Token auth cannot be combined with Graphistry credentials."
            )

        # Create GraphistryClient instance if none provided
        self._graphistry_client = graphistry_client or GraphistryClient()
        self._credentials = {
            "username": username,
            "password": password,
            "api_key": api_key,
            "personal_key_id": personal_key_id,
            "personal_key_secret": personal_key_secret,
            "org_name": org_name,
            "api": api,
            "graphistry_server": graphistry_server,
        }
        self._last_auth_time: float = 0.0
        self._token_lifetime = 3600  # Default 1 hour, will be updated from response

    @property
    def is_anonymous(self) -> bool:
        """Return True if auth manager is in anonymous mode."""
        return self._anonymous_enabled

    def register(self, **kwargs: Any) -> None:
        """Register authentication credentials (passthrough to graphistry)."""
        if self._anonymous_enabled:
            raise RuntimeError("Anonymous auth does not support register().")
        if self._token is not None:
            raise RuntimeError("Token auth does not support register().")
        self._graphistry_client.register(**kwargs)
        self._last_auth_time = time.time()

    def get_token(self) -> str:
        """Get current auth token, refreshing if needed.

        Returns:
            Valid authentication token

        Raises:
            RuntimeError: If authentication fails
        """
        if self._anonymous_enabled:
            if not self._token:
                if not self._anonymous_server_url:
                    raise RuntimeError(
                        "Anonymous auth requires a server URL to refresh tokens."
                    )
                self._token = get_anonymous_token(
                    self._anonymous_server_url, timeout=self._anonymous_timeout
                )
            return str(self._token)
        if self._token is not None:
            return str(self._token)

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
        if self._anonymous_enabled:
            if not self._anonymous_server_url:
                raise RuntimeError(
                    "Anonymous auth requires a server URL to refresh tokens."
                )
            self._token = get_anonymous_token(
                self._anonymous_server_url, timeout=self._anonymous_timeout
            )
            return
        if self._token is not None:
            raise RuntimeError("Token auth does not support refresh().")
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
        if self._anonymous_enabled:
            return
        if not any(self._credentials.values()):
            return  # No credentials stored

        # Build register kwargs with proper types
        register_kwargs: dict[str, Any] = {}

        # Handle different authentication methods
        pkey_id = self._credentials["personal_key_id"]
        pkey_secret = self._credentials["personal_key_secret"]
        if pkey_id and pkey_secret:
            # Personal key authentication takes precedence
            register_kwargs["personal_key_id"] = pkey_id
            register_kwargs["personal_key_secret"] = pkey_secret
        elif self._credentials["api_key"]:
            # API key authentication (legacy)
            register_kwargs["key"] = self._credentials["api_key"]
        elif self._credentials["username"] and self._credentials["password"]:
            # Username/password authentication
            register_kwargs["username"] = self._credentials["username"]
            register_kwargs["password"] = self._credentials["password"]

        # Add common parameters
        if self._credentials["org_name"]:
            register_kwargs["org_name"] = self._credentials["org_name"]
        if self._credentials["api"]:
            register_kwargs["api"] = self._credentials["api"]
        if self._credentials["graphistry_server"]:
            register_kwargs["server"] = self._credentials["graphistry_server"]

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


def auto_retry_auth(func: F) -> F:
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
