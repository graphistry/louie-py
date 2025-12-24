"""Unit tests for authentication functionality."""

from unittest.mock import Mock, patch

import httpx
import pytest

from louieai.auth import AuthManager, auto_retry_auth, get_anonymous_token


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

    def test_get_token_with_direct_token(self):
        """Test direct token auth returns provided token."""
        auth_manager = AuthManager(token="direct-token-123")

        assert auth_manager.get_token() == "direct-token-123"

    def test_direct_token_refresh_unsupported(self):
        """Test direct token auth does not support refresh."""
        auth_manager = AuthManager(token="direct-token-123")

        with pytest.raises(RuntimeError, match="Token auth does not support refresh"):
            auth_manager.refresh_token()

    def test_direct_token_conflicts_with_credentials(self):
        """Test direct token cannot be combined with Graphistry credentials."""
        with pytest.raises(ValueError, match="Token auth cannot be combined"):
            AuthManager(token="direct-token-123", username="test_user")

    def test_legacy_server_alias_rejected(self):
        """Test server alias is rejected in AuthManager."""
        with pytest.raises(ValueError, match="server is no longer supported"):
            AuthManager(server="hub.graphistry.com")

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

    def test_is_jwt_error_empty_message(self, auth_manager):
        """Test JWT error detection with empty message (line 127)."""
        assert auth_manager._is_jwt_error("") is False
        assert auth_manager._is_jwt_error(None) is False

    def test_get_token_no_token_available(self, mock_graphistry_client):
        """Test get_token when no token is available (lines 59-60, 62)."""
        # Mock client that returns no token
        mock_graphistry_client.api_token.return_value = None
        mock_graphistry_client.refresh = Mock()

        auth_manager = AuthManager(graphistry_client=mock_graphistry_client)

        with pytest.raises(RuntimeError, match="Failed to get authentication token"):
            auth_manager.get_token()

        # Should try refresh if available
        mock_graphistry_client.refresh.assert_called_once()
        # Should call api_token twice (before and after refresh)
        assert mock_graphistry_client.api_token.call_count == 2

    def test_get_token_no_refresh_method(self, mock_graphistry_client):
        """Test get_token when client has no refresh method."""
        # Mock client that returns no token and has no refresh method
        mock_graphistry_client.api_token.return_value = None
        # Remove refresh method
        if hasattr(mock_graphistry_client, "refresh"):
            delattr(mock_graphistry_client, "refresh")

        auth_manager = AuthManager(graphistry_client=mock_graphistry_client)

        with pytest.raises(RuntimeError, match="Failed to get authentication token"):
            auth_manager.get_token()

        # Should only call api_token once (no refresh available)
        mock_graphistry_client.api_token.assert_called_once()

    def test_refresh_token_no_refresh_method(self, mock_graphistry_client):
        """Test refresh_token when client has no refresh method (line 83)."""
        # Create AuthManager with credentials to test _refresh_auth fallback
        auth_manager = AuthManager(
            graphistry_client=mock_graphistry_client,
            username="test_user",
            password="test_pass",
        )

        # Remove refresh method to force fallback
        delattr(mock_graphistry_client, "refresh")

        # Should not raise error, should fall back to _refresh_auth
        auth_manager.refresh_token()

        # Should call register with stored credentials
        mock_graphistry_client.register.assert_called_once()

    def test_should_refresh_token_logic(self, mock_graphistry_client):
        """Test _should_refresh_token timing logic (lines 87-92)."""
        auth_manager = AuthManager(graphistry_client=mock_graphistry_client)

        # Test when never authenticated
        assert auth_manager._should_refresh_token() is False

        # Test when recently authenticated (within 90% of lifetime)
        import time

        auth_manager._last_auth_time = time.time()
        auth_manager._token_lifetime = 3600  # 1 hour
        assert auth_manager._should_refresh_token() is False

        # Test when token is old (past 90% of lifetime)
        auth_manager._last_auth_time = time.time() - 3300  # 55 minutes ago
        auth_manager._token_lifetime = 3600  # 1 hour (90% = 54 minutes)
        assert auth_manager._should_refresh_token() is True

    def test_refresh_auth_no_credentials(self, mock_graphistry_client):
        """Test _refresh_auth with no credentials (line 96-97)."""
        # Create AuthManager with explicitly no credentials (api=None to avoid default)
        auth_manager = AuthManager(graphistry_client=mock_graphistry_client, api=None)

        # Should not call register when no credentials (including api=None)
        auth_manager._refresh_auth()
        mock_graphistry_client.register.assert_not_called()

    def test_refresh_auth_various_credential_combinations(self, mock_graphistry_client):
        """Test _refresh_auth with different credential combinations (lines 98-115)."""
        # Test with username/password
        auth_manager = AuthManager(
            graphistry_client=mock_graphistry_client,
            username="test_user",
            password="test_pass",
            graphistry_server="test.server.com",
        )
        auth_manager._refresh_auth()
        mock_graphistry_client.register.assert_called_with(
            username="test_user",
            password="test_pass",
            api=3,  # Default api value is always included
            server="test.server.com",
        )

        mock_graphistry_client.register.reset_mock()

        # Test with API key
        auth_manager = AuthManager(
            graphistry_client=mock_graphistry_client, api_key="test-key-123", api=3
        )
        auth_manager._refresh_auth()
        mock_graphistry_client.register.assert_called_with(
            key="test-key-123",  # Note: 'key' parameter for graphistry
            api=3,
        )

    def test_handle_auth_error_json_parse_error(self, mock_graphistry_client):
        """Test handle_auth_error with malformed JSON (lines 161-162)."""
        auth_manager = AuthManager(graphistry_client=mock_graphistry_client)

        # Create error with malformed JSON response but error message contains JWT
        error = httpx.HTTPStatusError(
            "JWT expired",  # Error message that contains JWT keyword
            request=Mock(),
            response=Mock(status_code=401, text="Invalid JSON {"),
        )

        # Should handle JSON parse error gracefully and use str(error) fallback
        result = auth_manager.handle_auth_error(error)

        # Should return True because str(error) contains "JWT"
        assert result is True
        mock_graphistry_client.refresh.assert_called_once()

    def test_handle_auth_error_exception_in_refresh(self, mock_graphistry_client):
        """Test handle_auth_error when refresh fails (lines 171-172)."""
        auth_manager = AuthManager(graphistry_client=mock_graphistry_client)

        # Make refresh raise an exception
        mock_graphistry_client.refresh.side_effect = Exception("Refresh failed")

        error = httpx.HTTPStatusError(
            "Unauthorized",
            request=Mock(),
            response=Mock(status_code=401, text='{"detail": "JWT token has expired"}'),
        )

        # Should return False when refresh fails
        result = auth_manager.handle_auth_error(error)
        assert result is False

    def test_get_anonymous_token_success(self):
        """Test successful anonymous token fetch."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"success": True, "token": "anon-token-123"}

        with patch("louieai.auth.httpx.post", return_value=response) as mock_post:
            token = get_anonymous_token("http://localhost:8513")

        assert token == "anon-token-123"
        mock_post.assert_called_once_with(
            "http://localhost:8513/auth/anonymous", timeout=20.0
        )

    def test_get_anonymous_token_disabled(self):
        """Test anonymous auth disabled error handling."""
        response = Mock()
        response.status_code = 404
        response.text = "Not Found"

        with (
            patch("louieai.auth.httpx.post", return_value=response),
            pytest.raises(RuntimeError, match="Anonymous auth may be disabled"),
        ):
            get_anonymous_token("http://localhost:8513")

    def test_auth_manager_anonymous_refresh(self):
        """Test anonymous auth refresh flow."""
        with patch(
            "louieai.auth.get_anonymous_token",
            side_effect=["anon-token-456", "anon-token-789"],
        ) as mock_get:
            auth_manager = AuthManager(
                anonymous=True,
                anonymous_server_url="http://localhost:8513",
            )
            assert auth_manager.get_token() == "anon-token-456"
            auth_manager.refresh_token()
            assert auth_manager.get_token() == "anon-token-789"
            assert mock_get.call_count == 2


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
