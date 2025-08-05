"""Test cursor display functionality in notebooks."""

import sys
from unittest.mock import MagicMock, patch

from louieai._client import Response
from louieai.notebook.cursor import Cursor


class TestCursorDisplay:
    """Test cursor display and representation."""

    def test_cursor_call_returns_self(self):
        """Test that calling cursor returns self, not Response."""
        # Create cursor with mock client
        mock_client = MagicMock()
        mock_response = Response(
            thread_id="test-thread",
            elements=[{"type": "TextElement", "content": "Test response"}],
        )
        mock_client.add_cell.return_value = mock_response

        cursor = Cursor(client=mock_client)

        # Call cursor
        result = cursor("test query")

        # Should return cursor itself, not Response
        assert result is cursor
        assert isinstance(result, Cursor)
        assert not isinstance(result, Response)

        # Should be able to access properties
        assert cursor.text == "Test response"
        assert len(cursor._history) == 1

    def test_repr_shows_useful_info(self):
        """Test __repr__ shows session status."""
        cursor = Cursor(client=MagicMock())

        # Initial state
        repr_str = repr(cursor)
        assert "LouieAI Notebook Interface" in repr_str
        assert "Session: Not started" in repr_str
        assert "History: 0 responses" in repr_str
        assert "Traces: Disabled" in repr_str

        # After a query
        mock_response = Response(
            thread_id="test-thread",
            elements=[
                {"type": "TextElement", "content": "Hello"},
                {"type": "DfElement", "table": MagicMock()},
            ],
        )
        cursor._history.append(mock_response)
        cursor._current_thread = "test-thread"

        repr_str = repr(cursor)
        assert "Session: Active" in repr_str
        assert "History: 1 responses" in repr_str
        assert "Latest: 1 text, 1 dataframe" in repr_str

    def test_repr_html_no_longer_shows_response_content(self):
        """Test _repr_html_ no longer shows response content to avoid double display."""
        cursor = Cursor(client=MagicMock())

        # Add a response
        mock_response = Response(
            thread_id="test-thread",
            elements=[
                {"type": "TextElement", "content": "Here is your song:\n\nLa la la!"}
            ],
        )
        cursor._history.append(mock_response)
        cursor._current_thread = "test-thread"

        html = cursor._repr_html_()

        # Check structure
        assert "<h4" in html
        assert "LouieAI Session" in html  # Changed from "Response"

        # Check content is NOT displayed (to avoid double display)
        assert "Here is your song:" not in html
        assert "La la la!" not in html

        # Check metadata IS still shown
        assert "Session:</b> Active" in html
        assert "History:</b> 1 responses" in html

    def test_repr_html_shows_session_info(self):
        """Test that _repr_html_ shows session information."""
        cursor = Cursor(client=MagicMock())

        # Add response with HTML-like content
        mock_response = Response(
            thread_id="test-thread",
            elements=[
                {"type": "TextElement", "content": "<script>alert('xss')</script>"}
            ],
        )
        cursor._history.append(mock_response)
        cursor._current_thread = "test-thread"

        html = cursor._repr_html_()

        # Should show session info but not content
        assert "Session:</b> Active" in html
        assert "Thread ID:</b> <code>test-thread</code>" in html
        # Content should NOT be displayed (no XSS risk from _repr_html_)
        assert "<script>" not in html
        assert "alert" not in html

    def test_repr_html_shows_dataframe_notice(self):
        """Test that dataframe availability is noted."""
        cursor = Cursor(client=MagicMock())

        # Add response with dataframe
        import pandas as pd

        test_df = pd.DataFrame({"col": [1, 2, 3]})
        mock_response = Response(
            thread_id="test-thread",
            elements=[
                {"type": "TextElement", "content": "Here's your data:"},
                {"type": "DfElement", "table": test_df},
            ],
        )
        cursor._history.append(mock_response)

        html = cursor._repr_html_()

        # Should mention dataframe
        assert "dataframe(s) - access with" in html
        assert "lui.df" in html

    @patch("louieai.notebook.cursor.Cursor._in_jupyter")
    def test_display_called_in_jupyter(self, mock_in_jupyter):
        """Test that _display is called when in Jupyter."""
        mock_in_jupyter.return_value = True

        # Mock IPython display
        mock_display = MagicMock()
        mock_markdown = MagicMock()

        with (
            patch.dict(
                sys.modules,
                {
                    "IPython.display": MagicMock(
                        display=mock_display, Markdown=mock_markdown
                    )
                },
            ),
            patch("louieai.notebook.streaming.stream_response") as mock_stream,
        ):
            # Mock streaming response
            mock_stream.return_value = {
                "dthread_id": "test-thread",
                "elements": [{"type": "TextElement", "content": "Response text"}],
            }

            # Create cursor and make query
            mock_client = MagicMock()
            mock_response = Response(
                thread_id="test-thread",
                elements=[{"type": "TextElement", "content": "Response text"}],
            )
            mock_client.add_cell.return_value = mock_response

            cursor = Cursor(client=mock_client)
            # Set _last_display_id to simulate update scenario (not streaming)
            cursor._last_display_id = "existing_display"
            cursor("test query")

            # Display should have been called
            mock_markdown.assert_called_with("Response text")
            mock_display.assert_called()

    @patch("louieai.notebook.cursor.Cursor._in_jupyter")
    def test_display_not_called_outside_jupyter(self, mock_in_jupyter):
        """Test that _display is not called outside Jupyter."""
        mock_in_jupyter.return_value = False

        # Create cursor and make query
        mock_client = MagicMock()
        mock_response = Response(
            thread_id="test-thread",
            elements=[{"type": "TextElement", "content": "Response text"}],
        )
        mock_client.add_cell.return_value = mock_response

        cursor = Cursor(client=mock_client)

        # Should not raise even without IPython
        result = cursor("test query")
        assert result is cursor

    def test_display_handles_missing_ipython(self):
        """Test that missing IPython doesn't break display."""
        cursor = Cursor(client=MagicMock())
        mock_response = Response(
            thread_id="test-thread",
            elements=[{"type": "TextElement", "content": "Test"}],
        )

        # Remove IPython from modules
        ipython_backup = sys.modules.get("IPython")
        if "IPython" in sys.modules:
            del sys.modules["IPython"]

        try:
            # Should not raise
            cursor._display(mock_response)
        finally:
            # Restore IPython
            if ipython_backup:
                sys.modules["IPython"] = ipython_backup

    def test_cursor_properties_after_call(self):
        """Test that cursor properties work after calling."""
        mock_client = MagicMock()
        mock_client.server_url = "https://den.louie.ai"
        import pandas as pd

        test_df = pd.DataFrame({"data": [1, 2, 3]})
        mock_response = Response(
            thread_id="test-thread-123",
            elements=[
                {"type": "TextElement", "content": "Song lyrics here"},
                {"type": "DfElement", "table": test_df},
            ],
        )
        mock_client.add_cell.return_value = mock_response

        cursor = Cursor(client=mock_client)
        result = cursor("sing me a song")

        # Check we can access properties on returned cursor
        assert result.text == "Song lyrics here"
        assert result.texts == ["Song lyrics here"]
        assert len(result.dfs) == 1
        assert result.df is not None

        # Check thread properties
        assert result.thread_id == "test-thread-123"
        assert result.url == "https://den.louie.ai/?dthread=test-thread-123"
