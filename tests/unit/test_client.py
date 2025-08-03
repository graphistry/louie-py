"""Unit tests for LouieClient."""

from unittest.mock import Mock, patch

import httpx
import pytest

from louieai._client import LouieClient, Response


def mock_streaming_response(lines):
    """Helper to create a mock streaming response."""
    mock_stream_response = Mock()
    mock_stream_response.raise_for_status = Mock()
    mock_stream_response.iter_lines.return_value = iter(lines)

    mock_stream_cm = Mock()
    mock_stream_cm.__enter__ = Mock(return_value=mock_stream_response)
    mock_stream_cm.__exit__ = Mock(return_value=None)

    return mock_stream_cm


# Import from same directory when running tests
# (mocks are not used in this test file)


@pytest.mark.unit
class TestLouieClient:
    """Test LouieClient functionality with mocks."""

    @pytest.fixture
    def mock_graphistry_client(self):
        """Mock GraphistryClient instance."""
        mock = Mock()
        mock.api_token = Mock(return_value="fake-token-123")
        mock.register = Mock()
        mock.refresh = Mock()
        return mock

    @pytest.fixture
    def mock_httpx_client(self):
        """Mock httpx client."""
        return Mock(spec=httpx.Client)

    @pytest.fixture
    def client(self, mock_graphistry_client):
        """Create LouieClient with mocked GraphistryClient."""
        client = LouieClient(
            server_url="https://test.louie.ai", graphistry_client=mock_graphistry_client
        )
        return client

    def test_client_initialization(self, mock_graphistry_client):
        """Test client initializes correctly."""
        client = LouieClient(
            server_url="https://test.louie.ai", graphistry_client=mock_graphistry_client
        )

        assert client.server_url == "https://test.louie.ai"
        assert client.auth_manager is not None

    def test_client_initialization_with_graphistry_client_object(self):
        """Test client works with GraphistryClient objects (not just plottables)."""
        # Mock a GraphistryClient object (what graphistry.client() returns)
        mock_client = Mock()
        mock_client.api_token = Mock(return_value="test-token")
        mock_client.register = Mock()
        mock_client.refresh = Mock()

        client = LouieClient(graphistry_client=mock_client)

        assert client.auth_manager is not None
        assert client.auth_manager._graphistry_client is mock_client

    def test_multiple_clients_with_distinct_graphistry_clients(self):
        """Test multiple LouieClient instances with distinct GraphistryClients."""
        # Create two distinct GraphistryClient mocks
        alice_g = Mock()
        alice_g.api_token = Mock(return_value="alice-token")
        alice_g.register = Mock()
        alice_g.refresh = Mock()

        bob_g = Mock()
        bob_g.api_token = Mock(return_value="bob-token")
        bob_g.register = Mock()
        bob_g.refresh = Mock()

        # Create two LouieClients with distinct GraphistryClients
        alice_client = LouieClient(graphistry_client=alice_g)
        bob_client = LouieClient(graphistry_client=bob_g)

        # Verify they use different GraphistryClient objects
        assert alice_client.auth_manager._graphistry_client is alice_g
        assert bob_client.auth_manager._graphistry_client is bob_g
        assert (
            alice_client.auth_manager._graphistry_client
            is not bob_client.auth_manager._graphistry_client
        )

        # Verify they have separate auth managers
        assert alice_client.auth_manager is not bob_client.auth_manager

    def test_client_isolation_no_confused_deputy(self):
        """Test that separate clients don't interfere (no confused deputy)."""
        # Create two clients with different tokens
        alice_g = Mock()
        alice_g.api_token = Mock(return_value="alice-token-123")
        alice_g.register = Mock()
        alice_g.refresh = Mock()

        bob_g = Mock()
        bob_g.api_token = Mock(return_value="bob-token-456")
        bob_g.register = Mock()
        bob_g.refresh = Mock()

        alice_client = LouieClient(graphistry_client=alice_g)
        bob_client = LouieClient(graphistry_client=bob_g)

        # Get tokens from each client
        alice_token = alice_client.auth_manager.get_token()
        bob_token = bob_client.auth_manager.get_token()

        # Verify each client gets its own token
        assert alice_token == "alice-token-123"
        assert bob_token == "bob-token-456"
        assert alice_token != bob_token

        # Verify the right mock was called
        alice_g.api_token.assert_called()
        bob_g.api_token.assert_called()

    def test_create_thread_with_initial_prompt(self, client):
        """Test thread creation with initial prompt."""
        mock_stream_cm = mock_streaming_response(
            [
                '{"dthread_id": "D_test001"}',
                '{"payload": {"id": "B_001", "type": "TextElement", "text": "Hello!"}}',
            ]
        )

        # Mock the httpx client's stream method
        mock_httpx_client = Mock()
        mock_httpx_client.stream.return_value = mock_stream_cm

        # Patch httpx.Client to return our mock
        with patch("louieai._client.httpx.Client") as mock_client_class:
            # Handle both direct instantiation and context manager usage
            mock_client_instance = Mock()
            mock_client_instance.stream.return_value = mock_stream_cm
            mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
            mock_client_instance.__exit__ = Mock(return_value=None)
            mock_client_class.return_value = mock_client_instance

            thread = client.create_thread(
                name="Test Thread", initial_prompt="Say hello"
            )

        assert thread.id == "D_test001"
        assert thread.name == "Test Thread"

    def test_create_thread_without_initial_prompt(self, client):
        """Test thread creation without initial prompt."""
        thread = client.create_thread(name="Empty Thread")

        # Should create thread with empty ID (will be assigned on first query)
        assert thread.id == ""
        assert thread.name == "Empty Thread"

    def test_add_cell_to_existing_thread(self, client):
        """Test adding a cell to an existing thread."""
        mock_stream_cm = mock_streaming_response(
            [
                '{"dthread_id": "D_test001"}',
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Response text"}}',
            ]
        )

        mock_httpx_client = Mock()
        mock_httpx_client.stream.return_value = mock_stream_cm

        with patch("louieai._client.httpx.Client") as mock_client_class:
            # Handle both direct instantiation and context manager usage
            mock_client_instance = Mock()
            mock_client_instance.stream.return_value = mock_stream_cm
            mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
            mock_client_instance.__exit__ = Mock(return_value=None)
            mock_client_class.return_value = mock_client_instance

            response = client.add_cell("D_test001", "What is 2+2?")

        assert response.thread_id == "D_test001"
        assert len(response.elements) == 1
        assert response.elements[0]["type"] == "TextElement"
        assert response.elements[0]["text"] == "Response text"

    def test_add_cell_creates_new_thread(self, client):
        """Test adding a cell without thread ID creates new thread."""
        mock_stream_cm = mock_streaming_response(
            [
                '{"dthread_id": "D_new001"}',
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "New thread!"}}',
            ]
        )

        mock_httpx_client = Mock()
        mock_httpx_client.stream.return_value = mock_stream_cm

        with patch("louieai._client.httpx.Client") as mock_client_class:
            # Handle both direct instantiation and context manager usage
            mock_client_instance = Mock()
            mock_client_instance.stream.return_value = mock_stream_cm
            mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
            mock_client_instance.__exit__ = Mock(return_value=None)
            mock_client_class.return_value = mock_client_instance
            response = client.add_cell("", "Create new thread")

        assert response.thread_id == "D_new001"

    def test_list_threads(self, client, mock_httpx_client):
        """Test listing threads."""
        # Mock response
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "items": [
                    {"id": "D_001", "name": "Thread 1"},
                    {"id": "D_002", "name": "Thread 2"},
                ]
            }
        )
        mock_response.raise_for_status = Mock()
        mock_httpx_client.get.return_value = mock_response

        with patch.object(client, "_client", mock_httpx_client):
            threads = client.list_threads(page=1, page_size=10)

        assert len(threads) == 2
        assert threads[0].id == "D_001"
        assert threads[1].name == "Thread 2"

        # Verify API call
        mock_httpx_client.get.assert_called_once()
        call_args = mock_httpx_client.get.call_args
        assert "api/dthreads" in call_args[0][0]

    def test_get_thread(self, client, mock_httpx_client):
        """Test getting a specific thread."""
        # Mock response
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "id": "D_test001",
                "name": "Test Thread",
                "created_at": "2024-01-01T00:00:00Z",
            }
        )
        mock_response.raise_for_status = Mock()
        mock_httpx_client.get.return_value = mock_response

        with patch.object(client, "_client", mock_httpx_client):
            thread = client.get_thread("D_test001")

        assert thread.id == "D_test001"
        assert thread.name == "Test Thread"

    def test_response_parsing_multiple_elements(self, client):
        """Test parsing response with multiple elements."""
        mock_stream_cm = mock_streaming_response(
            [
                '{"dthread_id": "D_001"}',
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Processing..."}}',
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Processing...\\nAnalyzing..."}}',
                '{"payload": {"id": "B_002", "type": "DfElement", "df_id": "df_123", '
                '"metadata": {"shape": [10, 3]}}}',
            ]
        )

        mock_httpx_client = Mock()
        mock_httpx_client.stream.return_value = mock_stream_cm

        with patch("louieai._client.httpx.Client") as mock_client_class:
            # Handle both direct instantiation and context manager usage
            mock_client_instance = Mock()
            mock_client_instance.stream.return_value = mock_stream_cm
            mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
            mock_client_instance.__exit__ = Mock(return_value=None)
            mock_client_class.return_value = mock_client_instance
            # Mock the _fetch_dataframe_arrow method to prevent actual network calls
            with patch.object(client, "_fetch_dataframe_arrow", return_value=None):
                response = client.add_cell("D_001", "Query data and analyze")

        assert response.thread_id == "D_001"
        # The streaming now continues to read all elements
        assert len(response.elements) == 2

        # Check text element (should have the latest update)
        text_elem = response.elements[0]
        assert text_elem["type"] == "TextElement"
        assert text_elem["text"] == "Processing...\nAnalyzing..."

        # Check dataframe element
        df_elem = response.elements[1]
        assert df_elem["type"] == "DfElement"
        assert df_elem["df_id"] == "df_123"

    def test_error_handling(self, client):
        """Test error handling for API failures."""
        # Mock error response
        mock_httpx_client = Mock()
        mock_httpx_client.stream.side_effect = httpx.HTTPStatusError(
            "Server error",
            request=Mock(),
            response=Mock(status_code=500, text="Internal Server Error"),
        )

        with (
            patch("louieai._client.httpx.Client") as mock_client_class,
            pytest.raises(httpx.HTTPStatusError),
        ):
            # Handle both direct instantiation and context manager usage
            mock_client_instance = Mock()
            mock_client_instance.stream.side_effect = (
                mock_httpx_client.stream.side_effect
            )
            mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
            mock_client_instance.__exit__ = Mock(return_value=None)
            mock_client_class.return_value = mock_client_instance
            client.add_cell("D_001", "This will fail")

    def test_auth_header_included(self, client):
        """Test that auth header is included in requests."""
        mock_stream_cm = mock_streaming_response(
            [
                '{"dthread_id": "D_001"}',
                '{"payload": {"id": "B_001", "type": "TextElement", "text": "OK"}}',
            ]
        )

        mock_httpx_client = Mock()
        mock_httpx_client.stream.return_value = mock_stream_cm

        # Store mock_client_instance outside the with block
        mock_client_instance = None

        with patch("louieai._client.httpx.Client") as mock_client_class:
            # Handle both direct instantiation and context manager usage
            mock_client_instance = Mock()
            mock_client_instance.stream.return_value = mock_stream_cm
            mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
            mock_client_instance.__exit__ = Mock(return_value=None)
            mock_client_class.return_value = mock_client_instance
            client.add_cell("D_001", "Test auth")

        # Check auth header was included
        call_args = mock_client_instance.stream.call_args
        headers = call_args[1]["headers"]
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer fake-token-123"

    def test_response_convenience_methods(self):
        """Test Response convenience methods."""
        elements = [
            {"type": "TextElement", "text": "Hello"},
            {"type": "DfElement", "df_id": "df_123"},
            {"type": "GraphElement", "dataset_id": "graph_456"},
        ]
        response = Response(thread_id="D_001", elements=elements)

        # Test text elements
        text_elements = response.text_elements
        assert len(text_elements) == 1
        assert text_elements[0]["text"] == "Hello"

        # Test dataframe elements
        df_elements = response.dataframe_elements
        assert len(df_elements) == 1
        assert df_elements[0]["df_id"] == "df_123"

        # Test graph elements
        graph_elements = response.graph_elements
        assert len(graph_elements) == 1
        assert graph_elements[0]["dataset_id"] == "graph_456"

        # Test has methods
        assert response.has_dataframes
        assert response.has_graphs
        assert not response.has_errors

    def test_client_init_with_direct_credentials(self, mock_graphistry_client):
        """Test LouieClient.__init__ with direct credentials (lines 128-141)."""
        # Mock register method on the client
        mock_graphistry_client.register = Mock()

        # Test initialization with various credential combinations
        # When multiple auth types are provided, personal key takes priority,
        # then API key, then username/password
        client = LouieClient(
            server_url="https://test.louie.ai",
            graphistry_client=mock_graphistry_client,
            username="test_user",
            password="test_pass",
            api_key="test-key",
            api=3,
            server="test.server.com",
        )

        # Should call register with API key (since no personal key provided)
        # Username/password are lower priority than API key
        client._auth_manager._graphistry_client.register.assert_called_once_with(
            key="test-key",  # api_key becomes 'key'
            api=3,
            server="test.server.com",
        )

    def test_client_init_no_credentials(self, mock_graphistry_client):
        """Test LouieClient.__init__ with no credentials."""
        LouieClient(
            server_url="https://test.louie.ai", graphistry_client=mock_graphistry_client
        )

        # Should not call register when no credentials provided
        mock_graphistry_client.register.assert_not_called()

    def test_register_method(self, mock_graphistry_client):
        """Test register method passthrough (lines 161-162)."""
        client = LouieClient(
            server_url="https://test.louie.ai", graphistry_client=mock_graphistry_client
        )

        # Test register method
        result = client.register(username="user", password="pass", api=3)

        # Should call through to graphistry client
        mock_graphistry_client.register.assert_called_once_with(
            username="user", password="pass", api=3
        )

        # Should return self for chaining
        assert result is client

    def test_parse_jsonl_response_malformed_json(self, client):
        """Test _parse_jsonl_response with malformed JSON (lines 183, 199-200)."""
        # Test with completely malformed JSON
        malformed_response = (
            '{"dthread_id": "D_test"}\n{invalid json here}\n{"payload": {"id": "B_1"}}'
        )

        result = client._parse_jsonl_response(malformed_response)

        # Should handle malformed JSON gracefully
        assert result["dthread_id"] == "D_test"
        assert len(result["elements"]) == 1  # Only valid JSON should be processed
        assert result["elements"][0]["id"] == "B_1"

    def test_parse_jsonl_response_empty_lines(self, client):
        """Test _parse_jsonl_response with empty lines."""
        response_with_empty_lines = """{"dthread_id": "D_test"}

{"payload": {"id": "B_1", "type": "TextElement"}}

"""

        result = client._parse_jsonl_response(response_with_empty_lines)

        # Should handle empty lines gracefully
        assert result["dthread_id"] == "D_test"
        assert len(result["elements"]) == 1

    def test_context_manager_usage(self, mock_graphistry_client):
        """Test context manager methods (lines 337, 341)."""
        # Test __enter__ and __exit__
        with LouieClient(
            server_url="https://test.louie.ai", graphistry_client=mock_graphistry_client
        ) as client:
            # Should return self from __enter__
            assert isinstance(client, LouieClient)
            assert client.server_url == "https://test.louie.ai"

        # __exit__ should close the HTTP client (tested by not raising exception)
