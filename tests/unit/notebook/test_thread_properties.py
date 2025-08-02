"""Test thread_id and url properties."""

from unittest.mock import MagicMock

import pytest

from louieai._client import Response
from louieai.notebook.cursor import Cursor


class TestThreadProperties:
    """Test thread-related properties of the cursor."""

    def test_thread_id_initially_none(self):
        """Test thread_id is None before any queries."""
        cursor = Cursor(client=MagicMock())
        assert cursor.thread_id is None
        assert cursor.url is None

    def test_thread_id_after_query(self):
        """Test thread_id is set after making a query."""
        mock_client = MagicMock()
        mock_client.server_url = "https://den.louie.ai"
        mock_response = Response(
            thread_id="abc123def456",
            elements=[{"type": "TextElement", "content": "Test"}],
        )
        mock_client.add_cell.return_value = mock_response

        cursor = Cursor(client=mock_client)
        cursor("test query")

        assert cursor.thread_id == "abc123def456"
        assert cursor.url == "https://den.louie.ai/?dthread=abc123def456"

    @pytest.mark.parametrize(
        "server_url,thread_id,expected_url",
        [
            # Production server
            ("https://den.louie.ai", "abc123", "https://den.louie.ai/?dthread=abc123"),
            ("https://den.louie.ai/", "abc123", "https://den.louie.ai/?dthread=abc123"),
            # Dev server
            (
                "https://louie-dev.grph.xyz",
                "xyz789",
                "https://louie-dev.grph.xyz/?dthread=xyz789",
            ),
            (
                "https://louie-dev.grph.xyz/",
                "xyz789",
                "https://louie-dev.grph.xyz/?dthread=xyz789",
            ),
            # Custom/enterprise servers
            (
                "https://custom.example.com",
                "test1",
                "https://custom.example.com/?dthread=test1",
            ),
            (
                "https://louie.internal.corp",
                "corp123",
                "https://louie.internal.corp/?dthread=corp123",
            ),
        ],
    )
    def test_url_generation(self, server_url, thread_id, expected_url):
        """Test URL generation for different server configurations."""
        mock_client = MagicMock()
        mock_client.server_url = server_url

        cursor = Cursor(client=mock_client)
        cursor._current_thread = thread_id

        assert cursor.url == expected_url

    def test_url_none_without_thread(self):
        """Test url returns None when no thread exists."""
        mock_client = MagicMock()
        mock_client.server_url = "https://den.louie.ai"

        cursor = Cursor(client=mock_client)
        assert cursor.thread_id is None
        assert cursor.url is None

    def test_thread_persistence(self):
        """Test thread_id persists across multiple queries."""
        mock_client = MagicMock()
        mock_client.server_url = "https://den.louie.ai"

        # First response sets thread
        response1 = Response(
            thread_id="thread-123",
            elements=[{"type": "TextElement", "content": "First"}],
        )
        # Subsequent responses use same thread
        response2 = Response(
            thread_id="thread-123",
            elements=[{"type": "TextElement", "content": "Second"}],
        )

        mock_client.add_cell.side_effect = [response1, response2]

        cursor = Cursor(client=mock_client)

        # First query
        cursor("first query")
        assert cursor.thread_id == "thread-123"
        assert cursor.url == "https://den.louie.ai/?dthread=thread-123"

        # Second query
        cursor("second query")
        assert cursor.thread_id == "thread-123"
        assert cursor.url == "https://den.louie.ai/?dthread=thread-123"  # Same URL
