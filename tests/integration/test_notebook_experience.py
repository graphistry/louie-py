"""Integration tests for notebook user experience."""

import os
import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from louieai import louie
from louieai._client import Response


class TestNotebookExperience:
    """Test the complete notebook experience."""

    def _create_mock_client(self):
        """Create a properly configured mock client."""
        mock_client = MagicMock()
        mock_client.server_url = "https://test.louie.ai"
        return mock_client

    def test_basic_notebook_workflow(self):
        """Test the basic notebook workflow from import to results."""
        # Mock client that returns predictable responses
        mock_client = self._create_mock_client()

        # First response - text only
        mock_response1 = Response(
            thread_id="test-thread",
            elements=[
                {
                    "type": "TextElement",
                    "content": "Here's a song for you:\n\nTwinkle twinkle little star",
                }
            ],
        )

        # Second response - with dataframe
        test_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        mock_response2 = Response(
            thread_id="test-thread",
            elements=[
                {"type": "TextElement", "content": "Here's your data analysis:"},
                {"type": "DfElement", "table": test_df},
            ],
        )

        mock_client.add_cell.side_effect = [mock_response1, mock_response2]

        # Create cursor with our mock client
        from louieai.notebook.cursor import Cursor

        lui = Cursor(client=mock_client)

        # Mock to avoid streaming in tests
        with patch.object(lui, "_in_jupyter", return_value=False):
            # First query - returns cursor, not Response
            result1 = lui("sing me a song")
            assert result1 is lui
            assert isinstance(result1, type(lui))

            # Can access text directly
            assert lui.text == "Here's a song for you:\n\nTwinkle twinkle little star"
            assert lui.df is None

            # Second query with data
            result2 = lui("show me some data")
            assert result2 is lui

        # Can access both text and dataframe
        assert lui.text == "Here's your data analysis:"
        assert lui.df is not None
        assert isinstance(lui.df, pd.DataFrame)
        assert len(lui.df) == 3

        # History access works
        # lui[-1] gives ResponseProxy for the latest response
        assert lui[-1].text == "Here's your data analysis:"
        assert lui[-2].text == ("Here's a song for you:\n\nTwinkle twinkle little star")

    def test_notebook_display_modes(self):
        """Test different display scenarios in notebooks."""
        # Test with IPython available
        mock_ipython = MagicMock()
        mock_display = MagicMock()
        mock_markdown = MagicMock()
        mock_html = MagicMock()

        mock_ipython.display = MagicMock(
            display=mock_display, Markdown=mock_markdown, HTML=mock_html
        )

        with patch.dict(
            sys.modules,
            {"IPython": mock_ipython, "IPython.display": mock_ipython.display},
        ):
            # Create cursor
            mock_client = self._create_mock_client()
            mock_response = Response(
                thread_id="test-thread",
                elements=[
                    {
                        "type": "TextElement",
                        "content": "# Markdown Header\n\nSome **bold** text",
                    }
                ],
            )
            mock_client.add_cell.return_value = mock_response

            lui = louie(graphistry_client=MagicMock())
            lui._client = mock_client

            # Query without streaming
            with patch.object(lui, "_in_jupyter", return_value=False):
                result = lui("test markdown")

            # Should return cursor
            assert result is lui

            # Should have content ready for display
            assert lui.text == "# Markdown Header\n\nSome **bold** text"

            # Test that display would work if in Jupyter
            from louieai.notebook.cursor import _render_response_html

            html = _render_response_html(lui._history[-1])
            assert "Markdown Header" in html

    def test_notebook_error_handling(self):
        """Test error display in notebooks."""
        mock_client = self._create_mock_client()

        # Response with errors
        mock_response = Response(
            thread_id="test-thread",
            elements=[
                {"type": "TextElement", "content": "Processing your request..."},
                {
                    "type": "ExceptionElement",
                    "message": "API rate limit exceeded",
                    "error_type": "RateLimitError",
                },
            ],
        )
        mock_client.add_cell.return_value = mock_response

        # Create cursor with our mock client
        from louieai.notebook.cursor import Cursor

        lui = Cursor(client=mock_client)

        # Mock to avoid streaming in tests
        with patch.object(lui, "_in_jupyter", return_value=False):
            # Query with error
            result = lui("complex query")

        # Should still return cursor
        assert result is lui

        # Can check for errors
        assert lui.has_errors
        assert len(lui.errors) == 1
        assert lui.errors[0]["message"] == "API rate limit exceeded"

        # HTML representation should show errors
        html = lui._repr_html_()
        assert "Latest Response Contains Errors" in html
        assert "API rate limit exceeded" in html

    def test_notebook_repr_formats(self):
        """Test both plain and HTML representations."""
        mock_client = self._create_mock_client()
        mock_response = Response(
            thread_id="test-thread",
            elements=[
                {
                    "type": "TextElement",
                    "content": "Test content with <html> tags & symbols",
                },
                {"type": "DfElement", "table": pd.DataFrame({"a": [1, 2]})},
            ],
        )
        mock_client.add_cell.return_value = mock_response

        lui = louie(graphistry_client=MagicMock())
        lui._client = mock_client

        # Mock to avoid streaming
        with patch.object(lui, "_in_jupyter", return_value=False):
            lui("test")

        # Plain repr
        plain = repr(lui)
        assert "LouieAI Notebook Interface" in plain
        assert "Session: Active" in plain
        assert "1 text, 1 dataframe" in plain

        # HTML repr
        html = lui._repr_html_()
        assert "🤖 LouieAI Session" in html  # Changed from Response to Session
        # Note: Content is no longer shown in _repr_html_ to avoid double display
        # So HTML escaping tests are no longer relevant here
        assert "1 dataframe(s) - access with" in html

    def test_environment_variable_initialization(self):
        """Test initialization with environment variables."""
        # Set environment variables
        test_env = {
            "GRAPHISTRY_USERNAME": "test_user",
            "GRAPHISTRY_PASSWORD": "test_pass",
            "GRAPHISTRY_SERVER": "test.graphistry.com",
            "LOUIE_URL": "https://test.louie.ai",
        }

        with (
            patch.dict(os.environ, test_env),
            patch("louieai.notebook.cursor.LouieClient") as mock_client_class,
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.server_url = "https://test.louie.ai"
            mock_client_class.return_value = mock_client_instance

            # Import fresh to pick up env vars
            from louieai.notebook.cursor import Cursor

            # Create cursor without arguments
            Cursor()

            # Should have created client with env vars
            mock_client_class.assert_called_once()
            call_kwargs = mock_client_class.call_args[1]
            assert call_kwargs["server_url"] == "https://test.louie.ai"
            assert call_kwargs["username"] == "test_user"
            assert call_kwargs["password"] == "test_pass"
            assert call_kwargs["server"] == "test.graphistry.com"

    @pytest.mark.parametrize(
        "query,expected_text",
        [
            ("simple query", "Simple response"),
            ("query with\nnewlines", "Response with\nmultiple\nlines"),
            ("", "Empty query response"),
        ],
    )
    def test_various_query_responses(self, query, expected_text):
        """Test handling various types of responses."""
        mock_client = self._create_mock_client()
        mock_response = Response(
            thread_id="test-thread",
            elements=[{"type": "TextElement", "content": expected_text}],
        )
        mock_client.add_cell.return_value = mock_response

        lui = louie(graphistry_client=MagicMock())
        lui._client = mock_client

        # Mock to avoid streaming
        with patch.object(lui, "_in_jupyter", return_value=False):
            result = lui(query)

        assert result is lui
        assert lui.text == expected_text

        # HTML should preserve newlines as <br> in the response content
        if "\n" in expected_text:
            # The response content is in the history, not the session display
            response_html = lui[-1]._repr_html_()
            assert "<br>" in response_html

    def test_chaining_queries(self):
        """Test that queries can be chained since cursor returns self."""
        mock_client = self._create_mock_client()
        responses = [
            Response("thread1", [{"type": "TextElement", "content": f"Response {i}"}])
            for i in range(3)
        ]
        mock_client.add_cell.side_effect = responses

        lui = louie(graphistry_client=MagicMock())
        lui._client = mock_client

        # Mock to avoid streaming
        with patch.object(lui, "_in_jupyter", return_value=False):
            # Should be able to chain calls
            result = lui("query1")("query2")("query3")

        # All should return same cursor
        assert result is lui

        # Should have all responses in history
        assert len(lui._history) == 3
        assert lui.text == "Response 2"  # Latest
        assert lui[-3].text == "Response 0"  # First
        assert lui[-2].text == "Response 1"  # Second
        assert lui[-1].text == "Response 2"  # Third (latest)
