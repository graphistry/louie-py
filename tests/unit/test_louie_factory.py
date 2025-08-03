"""Test louie() factory function."""

from unittest.mock import Mock, patch

import louieai
from louieai import Cursor, louie

# lui is no longer exported from notebook


class TestLouieFactory:
    """Test the louie() factory function."""

    def test_louie_no_args_returns_cursor(self):
        """Test that louie() with no args returns a new cursor."""
        result = louie()
        assert isinstance(result, Cursor)
        # Should create a new cursor each time
        result2 = louie()
        assert result is not result2

    @patch("louieai._client.LouieClient")
    def test_louie_with_graphistry_client(self, mock_client_class):
        """Test louie() with PyGraphistry client."""
        # Mock graphistry client
        mock_graphistry = Mock()
        mock_graphistry.api_token = Mock(return_value="test_token")

        # Mock LouieClient
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create cursor
        result = louie(mock_graphistry)

        # Verify
        assert isinstance(result, Cursor)
        # The call might include org_name extracted from graphistry client
        call_args = mock_client_class.call_args
        assert call_args[1]["graphistry_client"] == mock_graphistry

    @patch("louieai._client.LouieClient")
    def test_louie_with_username_password(self, mock_client_class):
        """Test louie() with username/password."""
        # Mock LouieClient
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create cursor with credentials
        result = louie(username="testuser", password="testpass")

        # Verify
        assert isinstance(result, Cursor)
        mock_client_class.assert_called_once_with(
            username="testuser", password="testpass"
        )

    @patch("louieai._client.LouieClient")
    def test_louie_with_personal_keys(self, mock_client_class):
        """Test louie() with personal key authentication."""
        # Mock LouieClient
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create cursor with personal keys
        result = louie(
            personal_key_id="pk_123", personal_key_secret="sk_456", org_name="test-org"
        )

        # Verify
        assert isinstance(result, Cursor)
        mock_client_class.assert_called_once_with(
            personal_key_id="pk_123", personal_key_secret="sk_456", org_name="test-org"
        )

    @patch("louieai._client.LouieClient")
    def test_louie_with_api_key(self, mock_client_class):
        """Test louie() with API key."""
        # Mock LouieClient
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create cursor with API key
        result = louie(api_key="test_api_key_123")

        # Verify
        assert isinstance(result, Cursor)
        mock_client_class.assert_called_once_with(api_key="test_api_key_123")

    @patch("louieai._client.LouieClient")
    def test_louie_with_custom_server(self, mock_client_class):
        """Test louie() with custom server URL."""
        # Mock LouieClient
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create cursor with custom server
        result = louie(
            server_url="https://custom.louie.ai", server="custom.graphistry.com"
        )

        # Verify
        assert isinstance(result, Cursor)
        mock_client_class.assert_called_once_with(
            server_url="https://custom.louie.ai", server="custom.graphistry.com"
        )

    @patch("louieai._client.LouieClient")
    def test_louie_cursor_is_callable(self, mock_client_class):
        """Test that returned cursor is callable."""
        # Mock LouieClient
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create cursor
        cursor = louie(username="test", password="test")

        # Verify it's callable
        assert callable(cursor)
        assert callable(cursor)

    def test_louie_factory_examples(self):
        """Test that the documented examples would work."""
        # Example 1: Default cursor
        cursor1 = louie()
        assert callable(cursor1)

        # Example 2: With mock graphistry client
        mock_gc = Mock()
        cursor2 = louie(mock_gc)
        assert isinstance(cursor2, Cursor)

        # Example 3: With credentials
        with patch("louieai._client.LouieClient"):
            cursor3 = louie(username="user", password="pass")
            assert isinstance(cursor3, Cursor)

    def test_louie_available_at_package_level(self):
        """Test that louie is exported at package level."""
        assert hasattr(louieai, "louie")
        assert louieai.louie is louie
        assert "louie" in louieai.__all__
