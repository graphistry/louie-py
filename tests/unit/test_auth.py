"""Unit tests for authentication functionality."""

from unittest.mock import Mock, patch

import httpx
import pytest

from louieai.auth import AuthManager, auto_retry_auth


@pytest.mark.unit
class TestAuthManager:
    """Test AuthManager functionality."""

    @pytest.fixture
    def mock_graphistry_client(self):
        """Mock GraphistryClient instance."""
        mock = Mock()
        mock.api_token = Mock(return_value="fresh-token-456")
        mock.register = Mock()
        mock.refresh = Mock()
        return mock

    @pytest.fixture
    def auth_manager(self, mock_graphistry_client):
        """Create AuthManager with mocked GraphistryClient."""
        return AuthManager(graphistry_client=mock_graphistry_client)

    def test_get_auth_header(self, auth_manager, mock_graphistry_client):
        """Test getting authorization header."""
        header = auth_manager.get_auth_header()

        assert header == {"Authorization": "Bearer fresh-token-456"}
        mock_graphistry_client.api_token.assert_called_once()

    def test_handle_auth_error_jwt_expired(self, auth_manager, mock_graphistry_client):
        """Test handling JWT expiration error."""
        # Mock JWT expiration error
        error = httpx.HTTPStatusError(
            "Unauthorized",
            request=Mock(),
            response=Mock(status_code=401, text='{"detail": "JWT token has expired"}'),
        )

        result = auth_manager.handle_auth_error(error)

        assert result is True  # Should retry
        mock_graphistry_client.refresh.assert_called_once()

    def test_handle_auth_error_jwt_invalid(self, auth_manager, mock_graphistry_client):
        """Test handling invalid JWT error."""
        # Mock invalid JWT error
        error = httpx.HTTPStatusError(
            "Unauthorized",
            request=Mock(),
            response=Mock(
                status_code=401, text='{"detail": "Invalid authentication credentials"}'
            ),
        )

        result = auth_manager.handle_auth_error(error)

        assert result is True  # Should retry
        mock_graphistry_client.refresh.assert_called_once()

    def test_handle_auth_error_other_401(self, auth_manager):
        """Test handling other 401 errors."""
        # Mock non-JWT 401 error
        error = httpx.HTTPStatusError(
            "Unauthorized",
            request=Mock(),
            response=Mock(
                status_code=401, text='{"detail": "Access denied to resource"}'
            ),
        )

        result = auth_manager.handle_auth_error(error)
        assert result is False  # Should not retry

    def test_handle_auth_error_non_401(self, auth_manager):
        """Test handling non-401 errors."""
        # Mock 500 error
        error = httpx.HTTPStatusError(
            "Server Error",
            request=Mock(),
            response=Mock(status_code=500, text="Internal Server Error"),
        )

        result = auth_manager.handle_auth_error(error)
        assert result is False  # Should not retry

    def test_handle_auth_error_non_http(self, auth_manager):
        """Test handling non-HTTP errors."""
        error = ValueError("Not an HTTP error")

        result = auth_manager.handle_auth_error(error)
        assert result is False  # Should not retry

    def test_refresh_token(self, auth_manager, mock_graphistry_client):
        """Test token refresh."""
        auth_manager.refresh_token()

        mock_graphistry_client.refresh.assert_called_once()

    def test_is_jwt_error_various_messages(self, auth_manager):
        """Test JWT error detection with various messages."""
        jwt_errors = [
            "JWT token has expired",
            "jwt expired",
            "Invalid JWT",
            "JWT validation failed",
            "token expired",
            "Invalid authentication credentials",
        ]

        for msg in jwt_errors:
            assert auth_manager._is_jwt_error(msg) is True

        non_jwt_errors = [
            "Access denied",
            "Forbidden resource",
            "User not found",
            "Invalid password",
        ]

        for msg in non_jwt_errors:
            assert auth_manager._is_jwt_error(msg) is False


@pytest.mark.unit
class TestAutoRetryAuthDecorator:
    """Test auto_retry_auth decorator."""

    @pytest.fixture
    def mock_client(self):
        """Create mock client with auth_manager."""
        client = Mock()
        client.auth_manager = Mock()
        client.auth_manager.handle_auth_error = Mock(return_value=True)
        client.auth_manager.refresh_token = Mock()
        return client

    def test_auto_retry_success(self, mock_client):
        """Test successful call without auth errors."""

        @auto_retry_auth
        def api_method(self):
            return "success"

        # Bind method to mock client
        bound_method = api_method.__get__(mock_client, type(mock_client))
        result = bound_method()

        assert result == "success"
        mock_client.auth_manager.handle_auth_error.assert_not_called()

    def test_auto_retry_auth_error_recoverable(self, mock_client):
        """Test retry on recoverable auth error."""
        call_count = 0

        @auto_retry_auth
        def api_method(self):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call fails with auth error
                raise httpx.HTTPStatusError(
                    "Unauthorized",
                    request=Mock(),
                    response=Mock(status_code=401, text='{"detail": "JWT expired"}'),
                )
            return "success after retry"

        # Bind method to mock client
        bound_method = api_method.__get__(mock_client, type(mock_client))
        result = bound_method()

        assert result == "success after retry"
        assert call_count == 2  # Called twice
        mock_client.auth_manager.handle_auth_error.assert_called_once()

    def test_auto_retry_auth_error_not_recoverable(self, mock_client):
        """Test no retry on non-recoverable auth error."""
        mock_client.auth_manager.handle_auth_error.return_value = False

        @auto_retry_auth
        def api_method(self):
            raise httpx.HTTPStatusError(
                "Forbidden",
                request=Mock(),
                response=Mock(status_code=403, text="Forbidden"),
            )

        # Bind method to mock client
        bound_method = api_method.__get__(mock_client, type(mock_client))

        with pytest.raises(httpx.HTTPStatusError):
            bound_method()

        mock_client.auth_manager.handle_auth_error.assert_called_once()

    def test_auto_retry_non_http_error(self, mock_client):
        """Test no retry on non-HTTP errors."""

        @auto_retry_auth
        def api_method(self):
            raise ValueError("Not an HTTP error")

        # Bind method to mock client
        bound_method = api_method.__get__(mock_client, type(mock_client))

        with pytest.raises(ValueError):
            bound_method()

        mock_client.auth_manager.handle_auth_error.assert_not_called()

    def test_auto_retry_persistent_auth_error(self, mock_client):
        """Test giving up after persistent auth error."""
        call_count = 0

        @auto_retry_auth
        def api_method(self):
            nonlocal call_count
            call_count += 1
            # Always fail with auth error
            raise httpx.HTTPStatusError(
                "Unauthorized",
                request=Mock(),
                response=Mock(status_code=401, text='{"detail": "JWT expired"}'),
            )

        # Bind method to mock client
        bound_method = api_method.__get__(mock_client, type(mock_client))

        with pytest.raises(httpx.HTTPStatusError):
            bound_method()

        # Should only retry once
        assert call_count == 2
        mock_client.auth_manager.handle_auth_error.assert_called()
