"""Test LouieClient callable functionality."""

from unittest.mock import Mock, patch

from louieai import Response
from louieai._client import LouieClient


class TestClientCallable:
    """Test that LouieClient instances are callable."""

    def test_client_is_callable(self):
        """Test that LouieClient instances can be called."""
        client = LouieClient()
        assert callable(client), "LouieClient instance should be callable"

    @patch("louieai._client.httpx.Client")
    @patch("louieai._client.AuthManager")
    def test_call_creates_new_thread(self, mock_auth_manager_class, mock_httpx_class):
        """Test that calling client without thread_id creates new thread."""
        # Setup mocks
        mock_auth_manager = Mock()
        mock_auth_manager_class.return_value = mock_auth_manager
        mock_auth_manager.get_headers.return_value = {"Authorization": "Bearer test"}

        mock_httpx = Mock()
        mock_httpx_class.return_value = mock_httpx

        # Mock the response
        mock_response = Mock()
        mock_response.text = '{"elements": [], "dthread_id": "new_thread_123"}'
        mock_response.raise_for_status = Mock()
        mock_httpx.post.return_value = mock_response

        # Create client and call it
        client = LouieClient()
        response = client("Hello, world!")

        # Verify
        assert isinstance(response, Response)
        assert response.thread_id == "new_thread_123"

        # Check that empty thread_id was passed (for new thread)
        call_args = mock_httpx.post.call_args
        assert "dthread_id" not in call_args[1]["params"]

    @patch("louieai._client.httpx.Client")
    @patch("louieai._client.AuthManager")
    def test_call_maintains_thread_context(
        self, mock_auth_manager_class, mock_httpx_class
    ):
        """Test that subsequent calls maintain thread context."""
        # Setup mocks
        mock_auth_manager = Mock()
        mock_auth_manager_class.return_value = mock_auth_manager
        mock_auth_manager.get_headers.return_value = {"Authorization": "Bearer test"}

        mock_httpx = Mock()
        mock_httpx_class.return_value = mock_httpx

        # Mock first response (creates thread)
        mock_response1 = Mock()
        mock_response1.text = '{"elements": [], "dthread_id": "thread_123"}'
        mock_response1.raise_for_status = Mock()

        # Mock second response (uses same thread)
        mock_response2 = Mock()
        mock_response2.text = '{"elements": [], "dthread_id": "thread_123"}'
        mock_response2.raise_for_status = Mock()

        mock_httpx.post.side_effect = [mock_response1, mock_response2]

        # Create client and make two calls
        client = LouieClient()
        response1 = client("First query")
        response2 = client("Second query")

        # Verify both responses have same thread
        assert response1.thread_id == "thread_123"
        assert response2.thread_id == "thread_123"

        # Check second call used the thread_id
        second_call_args = mock_httpx.post.call_args_list[1]
        assert second_call_args[1]["params"]["dthread_id"] == "thread_123"

    @patch("louieai._client.httpx.Client")
    @patch("louieai._client.AuthManager")
    def test_call_with_explicit_thread_id(
        self, mock_auth_manager_class, mock_httpx_class
    ):
        """Test calling with explicit thread_id."""
        # Setup mocks
        mock_auth_manager = Mock()
        mock_auth_manager_class.return_value = mock_auth_manager
        mock_auth_manager.get_headers.return_value = {"Authorization": "Bearer test"}

        mock_httpx = Mock()
        mock_httpx_class.return_value = mock_httpx

        # Mock response
        mock_response = Mock()
        mock_response.text = '{"elements": [], "dthread_id": "custom_thread"}'
        mock_response.raise_for_status = Mock()
        mock_httpx.post.return_value = mock_response

        # Create client and call with thread_id
        client = LouieClient()
        response = client("Query", thread_id="custom_thread")

        # Verify
        assert response.thread_id == "custom_thread"
        call_args = mock_httpx.post.call_args
        assert call_args[1]["params"]["dthread_id"] == "custom_thread"

    @patch("louieai._client.httpx.Client")
    @patch("louieai._client.AuthManager")
    def test_call_with_traces(self, mock_auth_manager_class, mock_httpx_class):
        """Test calling with traces enabled."""
        # Setup mocks
        mock_auth_manager = Mock()
        mock_auth_manager_class.return_value = mock_auth_manager
        mock_auth_manager.get_headers.return_value = {"Authorization": "Bearer test"}

        mock_httpx = Mock()
        mock_httpx_class.return_value = mock_httpx

        # Mock response
        mock_response = Mock()
        mock_response.text = '{"elements": [], "dthread_id": "thread_123"}'
        mock_response.raise_for_status = Mock()
        mock_httpx.post.return_value = mock_response

        # Create client and call with traces
        client = LouieClient()
        client("Complex query", traces=True)

        # Verify traces parameter
        call_args = mock_httpx.post.call_args
        assert call_args[1]["params"]["ignore_traces"] == "false"

    @patch("louieai._client.httpx.Client")
    @patch("louieai._client.AuthManager")
    def test_call_with_custom_agent(self, mock_auth_manager_class, mock_httpx_class):
        """Test calling with custom agent."""
        # Setup mocks
        mock_auth_manager = Mock()
        mock_auth_manager_class.return_value = mock_auth_manager
        mock_auth_manager.get_headers.return_value = {"Authorization": "Bearer test"}

        mock_httpx = Mock()
        mock_httpx_class.return_value = mock_httpx

        # Mock response
        mock_response = Mock()
        mock_response.text = '{"elements": [], "dthread_id": "thread_123"}'
        mock_response.raise_for_status = Mock()
        mock_httpx.post.return_value = mock_response

        # Create client and call with custom agent
        client = LouieClient()
        client("Query", agent="CustomAgent")

        # Verify agent parameter
        call_args = mock_httpx.post.call_args
        assert call_args[1]["params"]["agent"] == "CustomAgent"

    def test_call_signature_matches_add_cell(self):
        """Test that __call__ signature is compatible with add_cell."""
        client = LouieClient()

        # Should accept same parameters
        # client("prompt") - basic usage
        # client("prompt", traces=True) - with traces
        # client("prompt", thread_id="123") - with thread
        # client("prompt", agent="CustomAgent") - with agent

        # All of these should work without errors (won't actually make requests)
        assert callable(client)
        assert callable(getattr(client, "add_cell", None))
