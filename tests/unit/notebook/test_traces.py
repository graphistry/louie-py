"""Tests for trace control and configuration."""

from unittest.mock import Mock, patch

from louieai import Response
from louieai.notebook.cursor import Cursor


class TestTraceControl:
    """Test trace control functionality."""

    def test_traces_default_off(self):
        """Test traces are off by default."""
        cursor = Cursor()
        assert cursor.traces is False

    def test_traces_setter(self):
        """Test setting traces for session."""
        cursor = Cursor()

        # Enable traces
        cursor.traces = True
        assert cursor.traces is True

        # Disable traces
        cursor.traces = False
        assert cursor.traces is False

    def test_traces_passed_to_client(self):
        """Test traces setting is passed to client.add_cell."""
        mock_client = Mock()
        mock_response = Mock(spec=Response, thread_id="test-thread")
        mock_response.text_elements = []
        mock_response.dataframe_elements = []
        mock_client.add_cell.return_value = mock_response

        cursor = Cursor(client=mock_client)

        # Default traces off
        cursor("Test query")
        mock_client.add_cell.assert_called_once()
        call_kwargs = mock_client.add_cell.call_args[1]
        assert call_kwargs["traces"] is False

        # Enable traces for session
        cursor.traces = True
        cursor("Test query 2")
        assert mock_client.add_cell.call_count == 2
        call_kwargs = mock_client.add_cell.call_args[1]
        assert call_kwargs["traces"] is True

    def test_per_query_trace_override(self):
        """Test per-query trace override."""
        mock_client = Mock()
        mock_response = Mock(spec=Response, thread_id="test-thread")
        mock_response.text_elements = []
        mock_response.dataframe_elements = []
        mock_client.add_cell.return_value = mock_response

        cursor = Cursor(client=mock_client)

        # Session default off, override on
        cursor("Test query", traces=True)
        call_kwargs = mock_client.add_cell.call_args[1]
        assert call_kwargs["traces"] is True

        # Session still off
        assert cursor.traces is False

        # Session default off, no override
        cursor("Test query 2")
        call_kwargs = mock_client.add_cell.call_args[1]
        assert call_kwargs["traces"] is False

        # Enable session traces, override off
        cursor.traces = True
        cursor("Test query 3", traces=False)
        call_kwargs = mock_client.add_cell.call_args[1]
        assert call_kwargs["traces"] is False

    def test_traces_with_lui_proxy(self):
        """Test traces work through lui proxy."""
        with patch("louieai.notebook.cursor.LouieClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_response = Mock(spec=Response, thread_id="test-123")
            mock_response.text_elements = []
            mock_response.dataframe_elements = []
            mock_client.add_cell.return_value = mock_response

            # Reset singleton
            import louieai.notebook

            louieai.notebook._global_cursor = None

            # Import lui
            from louieai.globals import lui

            # Test setting traces
            lui.traces = True
            assert lui.traces is True

            # Query with traces enabled
            lui("Test query")
            call_kwargs = mock_client.add_cell.call_args[1]
            assert call_kwargs["traces"] is True

            # Query with override
            lui("Test query 2", traces=False)
            call_kwargs = mock_client.add_cell.call_args[1]
            assert call_kwargs["traces"] is False

    def test_no_ignore_traces_hardcoded(self):
        """Test that ignore_traces is not hardcoded anymore."""
        # Check that client.py doesn't have hardcoded ignore_traces
        import inspect

        import louieai._client

        # Get source of add_cell method
        source = inspect.getsource(louieai._client.LouieClient.add_cell)

        # Should not have hardcoded "true"
        assert '"ignore_traces": "true"' not in source

        # Should use traces parameter
        assert "traces" in source
        assert "str(not traces).lower()" in source
