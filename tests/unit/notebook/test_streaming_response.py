"""Test streaming response handling."""

from unittest.mock import MagicMock, patch

from louieai._client import LouieClient


class TestStreamingResponse:
    """Test that streaming responses are fully consumed."""

    def test_client_reads_all_elements(self):
        """Test that client doesn't stop after first text element."""
        # Mock response that simulates streaming multiple elements
        mock_lines = [
            '{"dthread_id": "test-thread-123"}',
            '{"payload": {"id": "1", "type": "TextElement", '
            '"content": "Creating dataframe..."}}',
            '{"payload": {"id": "2", "type": "DfElement", '
            '"table": {"data": [1, 2, 3]}}}',
        ]

        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(mock_lines)
        mock_response.raise_for_status = MagicMock()

        mock_stream_client = MagicMock()
        mock_stream_client.stream.return_value.__enter__.return_value = mock_response

        with patch("httpx.Client") as mock_httpx:
            # Handle both direct instantiation and context manager usage
            mock_client_instance = MagicMock()
            mock_stream = mock_client_instance.stream.return_value
            mock_stream.__enter__.return_value = mock_response
            mock_client_instance.__enter__ = MagicMock(
                return_value=mock_client_instance
            )
            mock_client_instance.__exit__ = MagicMock(return_value=None)
            mock_httpx.return_value = mock_client_instance

            client = LouieClient()
            client._auth_manager = MagicMock()
            client._auth_manager.get_token.return_value = "test-token"

            response = client.add_cell("", "Create a dataframe")

            # Should have both text and dataframe elements
            assert len(response.elements) == 2
            assert response.elements[0]["type"] == "TextElement"
            assert response.elements[1]["type"] == "DfElement"

    def test_client_handles_delayed_dataframe(self):
        """Test that client waits for dataframe even if it comes later."""
        # Simulate a response where dataframe comes after multiple text updates
        mock_lines = [
            '{"dthread_id": "test-thread-456"}',
            '{"payload": {"id": "1", "type": "TextElement", '
            '"content": "Let me create a dataframe..."}}',
            '{"payload": {"id": "1", "type": "TextElement", '
            '"content": "Let me create a dataframe...\\nGenerating data..."}}',
            '{"payload": {"id": "1", "type": "TextElement", '
            '"content": "Let me create a dataframe...\\nGenerating data...\\n'
            'Here it is:"}}',
            '{"payload": {"id": "2", "type": "DfElement", '
            '"table": {"cols": ["A", "B"], "data": [[1, 2], [3, 4]]}}}',
        ]

        mock_response = MagicMock()
        mock_response.iter_lines.return_value = iter(mock_lines)
        mock_response.raise_for_status = MagicMock()

        mock_stream_client = MagicMock()
        mock_stream_client.stream.return_value.__enter__.return_value = mock_response

        with patch("httpx.Client") as mock_httpx:
            # Handle both direct instantiation and context manager usage
            mock_client_instance = MagicMock()
            mock_stream = mock_client_instance.stream.return_value
            mock_stream.__enter__.return_value = mock_response
            mock_client_instance.__enter__ = MagicMock(
                return_value=mock_client_instance
            )
            mock_client_instance.__exit__ = MagicMock(return_value=None)
            mock_httpx.return_value = mock_client_instance

            client = LouieClient()
            client._auth_manager = MagicMock()
            client._auth_manager.get_token.return_value = "test-token"

            response = client.add_cell("", "Create a dataframe")

            # Should have both elements
            assert len(response.elements) == 2

            # Text element should have the final content
            assert response.elements[0]["type"] == "TextElement"
            assert "Here it is:" in response.elements[0]["content"]

            # Dataframe should be present
            assert response.elements[1]["type"] == "DfElement"
            assert "table" in response.elements[1]
