"""Tests for help and discovery features."""

from unittest.mock import Mock, patch

from louieai import Response
from louieai.notebook.cursor import Cursor


class TestHelpDiscovery:
    """Test help and discovery functionality."""

    def test_cursor_has_docstring(self):
        """Test Cursor has comprehensive docstring."""
        cursor = Cursor()
        assert cursor.__doc__ is not None
        assert "Quick Start:" in cursor.__doc__
        assert "lui(" in cursor.__doc__
        assert "Session Management:" in cursor.__doc__
        assert "Trace Control:" in cursor.__doc__
        assert "Data Access:" in cursor.__doc__

    def test_cursor_repr_empty(self):
        """Test repr when no queries made."""
        cursor = Cursor()
        repr_str = repr(cursor)

        assert "<LouieAI Notebook Interface" in repr_str
        assert "Session: Not started" in repr_str
        assert "History: 0 responses" in repr_str
        assert "Traces: Disabled" in repr_str

    def test_cursor_repr_with_data(self):
        """Test repr with response history."""
        cursor = Cursor()

        # Mock response
        mock_response = Mock(spec=Response)
        mock_response.text_elements = [{"type": "TextElement", "content": "Hello"}]
        mock_response.dataframe_elements = [{"type": "DfElement", "table": Mock()}]

        cursor._history.append(mock_response)
        cursor._current_thread = "test-123"
        cursor._traces = True

        repr_str = repr(cursor)

        assert "Session: Active" in repr_str
        assert "History: 1 responses" in repr_str
        assert "Traces: Enabled" in repr_str
        assert "Latest: 1 text, 1 dataframe" in repr_str

    def test_cursor_repr_html_empty(self):
        """Test HTML repr for Jupyter."""
        cursor = Cursor()
        html = cursor._repr_html_()

        assert "<h4" in html
        assert "LouieAI Session" in html  # Changed from Response to Session
        assert "Session:</b> Not started" in html
        assert "lui('your query')" in html
        assert "<details>" in html  # Quick help section

    def test_cursor_repr_html_with_data(self):
        """Test HTML repr with data."""
        cursor = Cursor()

        # Mock response
        mock_response = Mock(spec=Response)
        mock_response.text_elements = [{"type": "TextElement", "content": "Hello"}]
        mock_response.dataframe_elements = []

        cursor._history.append(mock_response)
        cursor._current_thread = "test-123"

        html = cursor._repr_html_()

        assert "✅" in html  # Active session
        assert "History:</b> 1 responses" in html
        assert "lui[-1]" in html
        assert "1 text element(s)" in html
        assert "lui.text" in html

    def test_lui_proxy_repr(self):
        """Test lui proxy delegates repr correctly."""
        with patch("louieai.notebook.cursor.LouieClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Reset singleton
            import louieai.notebook

            louieai.notebook._global_cursor = None

            from louieai.globals import lui

            # Test repr delegation
            repr_str = repr(lui)
            assert "<LouieAI Notebook Interface" in repr_str

            # Test _repr_html_ delegation
            html = lui._repr_html_()
            assert "LouieAI Session" in html  # Changed from Response to Session

    def test_help_function_works(self):
        """Test Python's help() function provides useful info."""
        cursor = Cursor()

        # help() uses __doc__ attribute
        assert hasattr(cursor, "__doc__")
        assert len(cursor.__doc__) > 100  # Should have substantial docs

        # Test main method has docs
        assert hasattr(cursor.__call__, "__doc__")
        assert "Execute a query" in cursor.__call__.__doc__

    def test_quick_help_in_html(self):
        """Test quick help section in HTML repr."""
        cursor = Cursor()
        html = cursor._repr_html_()

        # Check for collapsible help section
        assert "<details>" in html
        assert "Quick Help" in html

        # Check for example code
        assert "lui('Show me sales data" in html
        assert "df = lui.df" in html
        assert "lui.traces = True" in html
        assert "lui[-1].df" in html
