"""Tests for user-friendly error handling."""

from unittest.mock import Mock, patch

import pytest

from louieai import Response
from louieai.notebook.cursor import Cursor
from louieai.notebook.exceptions import (
    AuthenticationError,
    NoDataFrameError,
    NoResponseError,
    SessionExpiredError,
)
from louieai.notebook.exceptions import ConnectionError as NotebookConnectionError


class TestErrorMessages:
    """Test user-friendly error messages."""

    def test_no_dataframe_error(self):
        """Test NoDataFrameError has helpful message."""
        error = NoDataFrameError()

        assert "No dataframe in the latest response" in str(error)
        assert "Try:" in str(error)
        assert "show the data as a table" in str(error)
        assert error.suggestion is not None

    def test_no_response_error(self):
        """Test NoResponseError guides user."""
        error = NoResponseError()

        assert "No responses yet" in str(error)
        assert "Make a query first" in str(error)
        assert "lui('your question here')" in str(error)

    def test_session_expired_error(self):
        """Test SessionExpiredError is reassuring."""
        error = SessionExpiredError()

        assert "Session expired" in str(error)
        assert "new session will be created automatically" in str(error)

    def test_authentication_error(self):
        """Test AuthenticationError provides guidance."""
        error = AuthenticationError()

        assert "Authentication failed" in str(error)
        assert "GRAPHISTRY_USERNAME" in str(error)
        assert "GRAPHISTRY_PASSWORD" in str(error)

    def test_connection_error(self):
        """Test ConnectionError with server info."""
        error = NotebookConnectionError("test.server.com")

        assert "Could not connect to server: test.server.com" in str(error)
        assert "Check your internet connection" in str(error)


class TestErrorHandlingIntegration:
    """Test error handling in the cursor."""

    def test_graceful_error_on_client_failure(self):
        """Test cursor handles client errors gracefully."""
        mock_client = Mock()
        mock_client.add_cell.side_effect = ValueError("API Error")

        cursor = Cursor(client=mock_client)

        # Should re-raise but log
        with pytest.raises(ValueError, match="API Error"):
            cursor("Test query")

    def test_properties_return_none_not_errors(self):
        """Test properties return None/empty instead of raising."""
        cursor = Cursor()

        # No responses yet
        assert cursor.df is None
        assert cursor.dfs == []
        assert cursor.text is None
        assert cursor.texts == []
        assert cursor.elements == []

        # History access out of bounds
        assert cursor[-1].df is None
        assert cursor[99].text is None

    @patch("louieai.notebook.cursor.logger")
    def test_errors_are_logged(self, mock_logger):
        """Test errors are logged with context."""
        mock_client = Mock()
        error = RuntimeError("Test error")
        mock_client.add_cell.side_effect = error

        cursor = Cursor(client=mock_client)

        with pytest.raises(RuntimeError):
            cursor("Test query")

        # Check error was logged
        mock_logger.error.assert_called_once()
        log_message = str(mock_logger.error.call_args)
        assert "Query failed" in log_message

    def test_empty_dataframe_elements_handled(self):
        """Test handling of malformed dataframe elements."""
        cursor = Cursor()

        # Mock response with bad dataframe elements
        mock_response = Mock(spec=Response)
        mock_response.dataframe_elements = [
            {},  # Missing 'table' key
            {"table": "not a dataframe"},  # Wrong type
            {"type": "DfElement"},  # Missing 'table'
        ]

        cursor._history.append(mock_response)

        # Should not raise, just return empty
        assert cursor.df is None
        assert cursor.dfs == []

    def test_missing_attributes_handled(self):
        """Test handling of responses missing expected attributes."""
        cursor = Cursor()

        # Create a mock response that truly doesn't have the attributes
        mock_response = Mock(spec=["thread_id"])  # Only has thread_id

        cursor._history.append(mock_response)

        # Should handle gracefully with hasattr checks
        assert cursor.text is None
        assert cursor.texts == []
        assert cursor.df is None
        assert cursor.dfs == []
