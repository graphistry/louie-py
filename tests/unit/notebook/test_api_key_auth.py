"""Test API key authentication for notebook API."""

from unittest.mock import Mock, patch

from louieai._client import LouieClient
from louieai.notebook import Cursor


class TestAPIKeyAuthentication:
    """Test different API key authentication methods."""

    def setup_method(self):
        """Reset state before each test."""
        import louieai.notebook

        louieai.notebook._global_cursor = None

    @patch("louieai.notebook.cursor.LouieClient")
    def test_personal_key_authentication(self, mock_client_class):
        """Test personal key ID + secret authentication."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Set environment variables
        import os

        os.environ["GRAPHISTRY_PERSONAL_KEY_ID"] = "TEST_KEY_ID"
        os.environ["GRAPHISTRY_PERSONAL_KEY_SECRET"] = "TEST_KEY_SECRET"
        os.environ["GRAPHISTRY_ORG_NAME"] = "test-org"

        try:
            # Create cursor without explicit client
            Cursor()

            # Verify client was created with personal key params
            mock_client_class.assert_called_once()
            call_kwargs = mock_client_class.call_args[1]
            assert call_kwargs["personal_key_id"] == "TEST_KEY_ID"
            assert call_kwargs["personal_key_secret"] == "TEST_KEY_SECRET"
            assert call_kwargs["org_name"] == "test-org"
        finally:
            # Clean up env vars
            os.environ.pop("GRAPHISTRY_PERSONAL_KEY_ID", None)
            os.environ.pop("GRAPHISTRY_PERSONAL_KEY_SECRET", None)
            os.environ.pop("GRAPHISTRY_ORG_NAME", None)

    @patch("louieai.notebook.cursor.LouieClient")
    def test_api_key_authentication(self, mock_client_class):
        """Test legacy API key authentication."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Set environment variables
        import os

        os.environ["GRAPHISTRY_API_KEY"] = "TEST_API_KEY"

        try:
            # Create cursor without explicit client
            Cursor()

            # Verify client was created with API key
            mock_client_class.assert_called_once()
            call_kwargs = mock_client_class.call_args[1]
            assert call_kwargs["api_key"] == "TEST_API_KEY"
        finally:
            # Clean up env vars
            os.environ.pop("GRAPHISTRY_API_KEY", None)

    @patch("louieai.notebook.cursor.LouieClient")
    def test_authentication_priority(self, mock_client_class):
        """Test that personal key takes priority over other auth methods."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Set multiple auth methods
        import os

        os.environ["GRAPHISTRY_PERSONAL_KEY_ID"] = "TEST_KEY_ID"
        os.environ["GRAPHISTRY_PERSONAL_KEY_SECRET"] = "TEST_KEY_SECRET"
        os.environ["GRAPHISTRY_API_KEY"] = "TEST_API_KEY"
        os.environ["GRAPHISTRY_USERNAME"] = "testuser"
        os.environ["GRAPHISTRY_PASSWORD"] = "testpass"

        try:
            # Create cursor
            Cursor()

            # Verify personal key was used (highest priority)
            call_kwargs = mock_client_class.call_args[1]
            assert call_kwargs["personal_key_id"] == "TEST_KEY_ID"
            assert call_kwargs["personal_key_secret"] == "TEST_KEY_SECRET"
            # These should still be passed but won't be used for auth
            assert call_kwargs["api_key"] == "TEST_API_KEY"
            assert call_kwargs["username"] == "testuser"
            assert call_kwargs["password"] == "testpass"
        finally:
            # Clean up env vars
            os.environ.pop("GRAPHISTRY_PERSONAL_KEY_ID", None)
            os.environ.pop("GRAPHISTRY_PERSONAL_KEY_SECRET", None)
            os.environ.pop("GRAPHISTRY_API_KEY", None)
            os.environ.pop("GRAPHISTRY_USERNAME", None)
            os.environ.pop("GRAPHISTRY_PASSWORD", None)

    @patch("louieai.notebook.cursor.LouieClient")
    def test_graphistry_env_vars(self, mock_client_class):
        """Test fallback to GRAPHISTRY_* environment variables."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Set Graphistry env vars
        import os

        os.environ["GRAPHISTRY_PERSONAL_KEY_ID"] = "GRAPH_KEY_ID"
        os.environ["GRAPHISTRY_PERSONAL_KEY_SECRET"] = "GRAPH_KEY_SECRET"
        os.environ["GRAPHISTRY_ORG_NAME"] = "graph-org"

        try:
            # Create cursor
            Cursor()

            # Verify Graphistry vars were used
            call_kwargs = mock_client_class.call_args[1]
            assert call_kwargs["personal_key_id"] == "GRAPH_KEY_ID"
            assert call_kwargs["personal_key_secret"] == "GRAPH_KEY_SECRET"
            assert call_kwargs["org_name"] == "graph-org"
        finally:
            # Clean up env vars
            os.environ.pop("GRAPHISTRY_PERSONAL_KEY_ID", None)
            os.environ.pop("GRAPHISTRY_PERSONAL_KEY_SECRET", None)
            os.environ.pop("GRAPHISTRY_ORG_NAME", None)


class TestClientAPIKeyAuth:
    """Test API key auth at the LouieClient level."""

    @patch("louieai._client.AuthManager")
    @patch("louieai._client.httpx.Client")
    def test_client_personal_key_params(self, mock_httpx, mock_auth_manager_class):
        """Test LouieClient accepts personal key parameters."""
        mock_auth_manager = Mock()
        mock_auth_manager_class.return_value = mock_auth_manager

        # Create client with personal key auth
        LouieClient(
            personal_key_id="MY_KEY_ID",
            personal_key_secret="MY_SECRET",
            org_name="my-org",
            server="hub.graphistry.com",
        )

        # Verify AuthManager received the params
        mock_auth_manager_class.assert_called_once()
        call_kwargs = mock_auth_manager_class.call_args[1]
        assert call_kwargs["personal_key_id"] == "MY_KEY_ID"
        assert call_kwargs["personal_key_secret"] == "MY_SECRET"
        assert call_kwargs["org_name"] == "my-org"

    @patch("louieai.auth.GraphistryClient")
    @patch("louieai._client.httpx.Client")
    def test_client_register_with_personal_key(self, mock_httpx, mock_graphistry_class):
        """Test that client.register is called with personal key params."""
        mock_graphistry = Mock()
        mock_graphistry_class.return_value = mock_graphistry

        # Mock the register method to track calls
        mock_register = Mock()

        with patch.object(LouieClient, "register", mock_register):
            # Create client with personal key auth
            LouieClient(
                personal_key_id="MY_KEY_ID",
                personal_key_secret="MY_SECRET",
                org_name="my-org",
                api=3,
                server="hub.graphistry.com",
            )

            # Verify register was called with correct params
            mock_register.assert_called_once()
            call_kwargs = mock_register.call_args[1]
            assert call_kwargs["personal_key_id"] == "MY_KEY_ID"
            assert call_kwargs["personal_key_secret"] == "MY_SECRET"
            assert call_kwargs["org_name"] == "my-org"
            assert call_kwargs["api"] == 3
            assert call_kwargs["server"] == "hub.graphistry.com"
