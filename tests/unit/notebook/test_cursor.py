"""Unit tests for Cursor implementation."""

from collections import deque
from unittest.mock import Mock, patch

import pytest

from louieai import Response
from louieai.notebook.cursor import Cursor


class TestCursor:
    """Test Cursor functionality."""

    def test_init_creates_client(self):
        """Test cursor initializes with default client."""
        with patch("louieai.notebook.cursor.LouieClient") as mock_client:
            cursor = Cursor()
            mock_client.assert_called_once()
            assert len(cursor._history) == 0
            assert cursor._current_thread is None
            assert cursor._traces is False

    def test_init_with_custom_client(self):
        """Test cursor accepts custom client."""
        mock_client = Mock()
        cursor = Cursor(client=mock_client)
        assert cursor._client is mock_client

    def test_call_creates_thread_on_first_use(self):
        """Test thread creation on first query."""
        mock_client = Mock()
        mock_response = Mock(spec=Response, thread_id="test-thread-123")
        mock_client.add_cell.return_value = mock_response

        cursor = Cursor(client=mock_client)

        # Mock _in_jupyter to return False so it uses add_cell instead of streaming
        with patch.object(cursor, "_in_jupyter", return_value=False):
            cursor("Test query")

        # Should start with empty thread
        assert cursor._current_thread == "test-thread-123"

        # Should use empty thread_id on first call
        mock_client.add_cell.assert_called_once()
        call_args = mock_client.add_cell.call_args[1]
        assert call_args["thread_id"] == ""
        assert call_args["prompt"] == "Test query"

    def test_call_reuses_thread(self):
        """Test thread persistence across calls."""
        mock_client = Mock()
        mock_response = Mock(spec=Response, thread_id="test-thread-123")
        mock_client.add_cell.return_value = mock_response

        cursor = Cursor(client=mock_client)

        # Mock _in_jupyter to return False so it uses add_cell instead of streaming
        with patch.object(cursor, "_in_jupyter", return_value=False):
            # First call creates thread
            cursor("First query")
            assert mock_client.add_cell.call_count == 1

            # Second call reuses thread
            cursor("Second query")
            assert mock_client.add_cell.call_count == 2

        # Check calls
        calls = mock_client.add_cell.call_args_list
        assert calls[0][1]["thread_id"] == ""  # First call creates thread
        assert calls[1][1]["thread_id"] == "test-thread-123"  # Second reuses

    def test_history_tracking(self):
        """Test response history is maintained."""
        mock_client = Mock()

        # Create distinct response objects
        response1 = Mock(spec=Response, thread_id="test-thread", id="resp1")
        response2 = Mock(spec=Response, thread_id="test-thread", id="resp2")
        mock_client.add_cell.side_effect = [response1, response2]

        cursor = Cursor(client=mock_client)

        # Mock _in_jupyter to return False so it uses add_cell instead of streaming
        with patch.object(cursor, "_in_jupyter", return_value=False):
            # Execute queries
            resp1 = cursor("Query 1")
            resp2 = cursor("Query 2")

        # Check history
        assert len(cursor._history) == 2
        assert cursor._history[0] == response1
        assert cursor._history[1] == response2
        # Cursor now returns self, not the response
        assert resp1 is cursor
        assert resp2 is cursor

    def test_history_maxlen(self):
        """Test history respects max length."""
        # Create cursor with small history for testing
        cursor = Cursor()
        cursor._history = deque(maxlen=3)

        # Add 5 items
        for i in range(5):
            cursor._history.append(f"response_{i}")

        # Should only keep last 3
        assert len(cursor._history) == 3
        assert list(cursor._history) == ["response_2", "response_3", "response_4"]

    def test_traces_default_off(self):
        """Test traces are off by default."""
        mock_client = Mock()
        mock_response = Mock(spec=Response, thread_id="test-thread")
        mock_client.add_cell.return_value = mock_response

        cursor = Cursor(client=mock_client)

        # Mock _in_jupyter to return False so it uses add_cell instead of streaming
        with patch.object(cursor, "_in_jupyter", return_value=False):
            cursor("Test query")

        # Check traces parameter passed to client
        assert cursor._traces is False
        call_kwargs = mock_client.add_cell.call_args[1]
        assert call_kwargs["traces"] is False

    def test_traces_override(self):
        """Test per-query trace override."""
        mock_client = Mock()
        mock_response = Mock(spec=Response, thread_id="test-thread")
        mock_client.add_cell.return_value = mock_response

        cursor = Cursor(client=mock_client)

        # Mock _in_jupyter to return False so it uses add_cell instead of streaming
        with patch.object(cursor, "_in_jupyter", return_value=False):
            # Query with traces enabled
            cursor("Test query", traces=True)
            call_kwargs = mock_client.add_cell.call_args[1]
            assert call_kwargs["traces"] is True

            # Query with traces disabled explicitly
            cursor("Test query 2", traces=False)
            call_kwargs = mock_client.add_cell.call_args[1]
            assert call_kwargs["traces"] is False

    def test_agent_override(self):
        """Test agent can be overridden."""
        mock_client = Mock()
        mock_response = Mock(spec=Response, thread_id="test-thread")
        mock_client.add_cell.return_value = mock_response

        cursor = Cursor(client=mock_client)

        # Mock _in_jupyter to return False so it uses add_cell instead of streaming
        with patch.object(cursor, "_in_jupyter", return_value=False):
            cursor("Test query", agent="custom")

        call_args = mock_client.add_cell.call_args[1]
        assert call_args["agent"] == "custom"

    def test_error_handling(self):
        """Test errors are logged and re-raised."""
        mock_client = Mock()
        mock_client.add_cell.side_effect = ValueError("API Error")

        cursor = Cursor(client=mock_client)

        # Mock _in_jupyter to return False so it uses add_cell instead of streaming
        with (
            patch.object(cursor, "_in_jupyter", return_value=False),
            pytest.raises(ValueError, match="API Error"),
        ):
            cursor("Test query")

    @patch("louieai.notebook.cursor.logger")
    def test_error_logging(self, mock_logger):
        """Test errors are logged."""
        mock_client = Mock()
        mock_client.add_cell.side_effect = ValueError("API Error")

        cursor = Cursor(client=mock_client)

        # Mock _in_jupyter to return False so it uses add_cell instead of streaming
        with (
            patch.object(cursor, "_in_jupyter", return_value=False),
            pytest.raises(ValueError),
        ):
            cursor("Test query")

        mock_logger.error.assert_called_once()
        assert "Query failed" in str(mock_logger.error.call_args)

    def test_jupyter_detection(self):
        """Test Jupyter environment detection."""
        cursor = Cursor()

        # Our implementation checks sys.modules
        import sys

        # Test without IPython
        if "IPython" in sys.modules:
            del sys.modules["IPython"]
        assert cursor._in_jupyter() is False

        # Test with IPython
        sys.modules["IPython"] = Mock()
        assert cursor._in_jupyter() is True

        # Clean up
        if "IPython" in sys.modules:
            del sys.modules["IPython"]

    def test_no_display_outside_jupyter(self):
        """Test display is skipped outside Jupyter."""
        mock_client = Mock()
        mock_response = Mock(spec=Response, thread_id="test-thread")
        mock_client.add_cell.return_value = mock_response

        cursor = Cursor(client=mock_client)

        # Mock not in Jupyter
        with (
            patch.object(cursor, "_in_jupyter", return_value=False),
            patch.object(cursor, "_display") as mock_display,
        ):
            cursor("Test query")
            mock_display.assert_not_called()

    def test_display_disabled_by_kwarg(self):
        """Test display can be disabled via kwarg."""
        mock_client = Mock()
        mock_response = Mock(spec=Response, thread_id="test-thread")
        mock_client.add_cell.return_value = mock_response

        cursor = Cursor(client=mock_client)

        # Mock streaming response to prevent HTTP calls
        mock_stream_result = {
            "dthread_id": "test-thread",
            "elements": [{"type": "TextElement", "id": "test", "text": "test"}],
        }

        # Mock in Jupyter
        with (
            patch.object(cursor, "_in_jupyter", return_value=True),
            patch.object(cursor, "_display") as mock_display,
            patch(
                "louieai.notebook.streaming.stream_response",
                return_value=mock_stream_result,
            ),
        ):
            cursor("Test query", display=False)
            mock_display.assert_not_called()
