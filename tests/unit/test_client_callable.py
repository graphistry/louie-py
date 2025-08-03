"""Test LouieClient callable functionality."""

from unittest.mock import Mock, patch

from louieai import Response
from louieai._client import LouieClient


def mock_streaming_response(lines):
    """Helper to create a mock streaming response."""
    mock_stream_response = Mock()
    mock_stream_response.raise_for_status = Mock()
    mock_stream_response.iter_lines.return_value = iter(lines)

    mock_stream_cm = Mock()
    mock_stream_cm.__enter__ = Mock(return_value=mock_stream_response)
    mock_stream_cm.__exit__ = Mock(return_value=None)

    return mock_stream_cm


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
        mock_auth_manager.get_token.return_value = "test-token"

        # Set up credentials as dict so it's subscriptable
        mock_auth_manager._credentials = {
            "org_name": "test_org",
            "username": "test_user",
            "api": 3,
        }

        # Mock streaming response
        mock_stream_cm = mock_streaming_response(
            [
                '{"dthread_id": "new_thread_123"}',
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Response"}}',
            ]
        )

        mock_httpx_client = Mock()
        mock_httpx_client.stream.return_value = mock_stream_cm

        # Make httpx.Client return our mock
        # Handle both direct instantiation and context manager usage
        mock_client_instance = Mock()
        mock_client_instance.stream.return_value = mock_stream_cm
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_httpx_class.return_value = mock_client_instance

        # Create client and call it
        client = LouieClient()
        response = client("Hello, world!")

        # Verify
        assert isinstance(response, Response)
        assert response.thread_id == "new_thread_123"

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
        mock_auth_manager.get_token.return_value = "test-token"

        # Set up credentials as dict so it's subscriptable
        mock_auth_manager._credentials = {
            "org_name": "test_org",
            "username": "test_user",
            "api": 3,
        }

        # Mock first response (creates thread)
        mock_stream_cm1 = mock_streaming_response(
            [
                '{"dthread_id": "thread_123"}',
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Response 1"}}',
            ]
        )

        # Mock second response (uses same thread)
        mock_stream_cm2 = mock_streaming_response(
            [
                '{"dthread_id": "thread_123"}',
                '{"payload": {"id": "B_002", "type": "TextElement", '
                '"text": "Response 2"}}',
            ]
        )

        mock_httpx_client = Mock()
        mock_httpx_client.stream.side_effect = [mock_stream_cm1, mock_stream_cm2]

        # Make httpx.Client return our mock
        # Handle both direct instantiation and context manager usage
        mock_client_instance = Mock()
        mock_client_instance.stream.side_effect = [mock_stream_cm1, mock_stream_cm2]
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_httpx_class.return_value = mock_client_instance

        # Create client and make two calls
        client = LouieClient()
        response1 = client("First query")
        response2 = client("Second query")

        # Verify both responses have same thread
        assert response1.thread_id == "thread_123"
        assert response2.thread_id == "thread_123"

        # Check second call used the thread_id
        second_call_args = mock_client_instance.stream.call_args_list[1]
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
        mock_auth_manager.get_token.return_value = "test-token"

        # Set up credentials as dict so it's subscriptable
        mock_auth_manager._credentials = {
            "org_name": "test_org",
            "username": "test_user",
            "api": 3,
        }

        # Mock response
        mock_stream_cm = mock_streaming_response(
            [
                '{"dthread_id": "custom_thread"}',
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Response"}}',
            ]
        )

        mock_httpx_client = Mock()
        mock_httpx_client.stream.return_value = mock_stream_cm

        # Make httpx.Client return our mock
        # Handle both direct instantiation and context manager usage
        mock_client_instance = Mock()
        mock_client_instance.stream.return_value = mock_stream_cm
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_httpx_class.return_value = mock_client_instance

        # Create client and call with thread_id
        client = LouieClient()
        response = client("Query", thread_id="custom_thread")

        # Verify
        assert response.thread_id == "custom_thread"
        # Get the actual instance that was used
        used_client = mock_httpx_class.return_value
        call_args = used_client.stream.call_args
        assert call_args[1]["params"]["dthread_id"] == "custom_thread"

    @patch("louieai._client.httpx.Client")
    @patch("louieai._client.AuthManager")
    def test_call_with_traces(self, mock_auth_manager_class, mock_httpx_class):
        """Test calling with traces enabled."""
        # Setup mocks
        mock_auth_manager = Mock()
        mock_auth_manager_class.return_value = mock_auth_manager
        mock_auth_manager.get_headers.return_value = {"Authorization": "Bearer test"}
        mock_auth_manager.get_token.return_value = "test-token"

        # Set up credentials as dict so it's subscriptable
        mock_auth_manager._credentials = {
            "org_name": "test_org",
            "username": "test_user",
            "api": 3,
        }

        # Mock response
        mock_stream_cm = mock_streaming_response(
            [
                '{"dthread_id": "thread_123"}',
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Response"}}',
            ]
        )

        mock_httpx_client = Mock()
        mock_httpx_client.stream.return_value = mock_stream_cm

        # Make httpx.Client return our mock
        # Handle both direct instantiation and context manager usage
        mock_client_instance = Mock()
        mock_client_instance.stream.return_value = mock_stream_cm
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_httpx_class.return_value = mock_client_instance

        # Create client and call with traces
        client = LouieClient()
        client("Complex query", traces=True)

        # Verify traces parameter
        # Get the actual instance that was used
        used_client = mock_httpx_class.return_value
        call_args = used_client.stream.call_args
        assert call_args[1]["params"]["ignore_traces"] == "false"

    @patch("louieai._client.httpx.Client")
    @patch("louieai._client.AuthManager")
    def test_call_with_custom_agent(self, mock_auth_manager_class, mock_httpx_class):
        """Test calling with custom agent."""
        # Setup mocks
        mock_auth_manager = Mock()
        mock_auth_manager_class.return_value = mock_auth_manager
        mock_auth_manager.get_headers.return_value = {"Authorization": "Bearer test"}
        mock_auth_manager.get_token.return_value = "test-token"

        # Set up credentials as dict so it's subscriptable
        mock_auth_manager._credentials = {
            "org_name": "test_org",
            "username": "test_user",
            "api": 3,
        }

        # Mock response
        mock_stream_cm = mock_streaming_response(
            [
                '{"dthread_id": "thread_123"}',
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Response"}}',
            ]
        )

        mock_httpx_client = Mock()
        mock_httpx_client.stream.return_value = mock_stream_cm

        # Make httpx.Client return our mock
        # Handle both direct instantiation and context manager usage
        mock_client_instance = Mock()
        mock_client_instance.stream.return_value = mock_stream_cm
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_httpx_class.return_value = mock_client_instance

        # Create client and call with custom agent
        client = LouieClient()
        client("Query", agent="CustomAgent")

        # Verify agent parameter
        # Get the actual instance that was used
        used_client = mock_httpx_class.return_value
        call_args = used_client.stream.call_args
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
