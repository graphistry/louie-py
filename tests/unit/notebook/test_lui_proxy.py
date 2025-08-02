"""Test the lui proxy interface."""

from unittest.mock import Mock, patch

import pandas as pd

from louieai import Response
from louieai.globals import lui


class TestLuiProxy:
    """Test the lui singleton proxy."""

    @patch("louieai.notebook.cursor.LouieClient")
    def test_lui_is_callable(self, mock_client_class):
        """Test lui can be called like a function."""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_response = Mock(spec=Response, thread_id="test-123")
        mock_response.text_elements = []
        mock_response.dataframe_elements = []
        mock_client.add_cell.return_value = mock_response

        # Reset singleton
        import louieai.notebook

        louieai.notebook._global_cursor = None

        # Test calling lui
        result = lui("Test query")

        # Now cursor returns self, not the response
        assert hasattr(result, "text")  # It's a cursor
        assert hasattr(result, "df")
        mock_client.add_cell.assert_called_once()

    @patch("louieai.notebook.cursor.LouieClient")
    def test_lui_has_properties(self, mock_client_class):
        """Test lui has df, text, etc properties."""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        df = pd.DataFrame({"a": [1, 2, 3]})
        mock_response = Mock(spec=Response, thread_id="test-123")
        mock_response.text_elements = [{"type": "TextElement", "content": "Hello"}]
        mock_response.dataframe_elements = [{"type": "DfElement", "table": df}]
        mock_client.add_cell.return_value = mock_response

        # Reset singleton
        import louieai.notebook

        louieai.notebook._global_cursor = None

        # Import and use lui
        lui("Test query")

        # Test properties
        assert lui.text == "Hello"
        pd.testing.assert_frame_equal(lui.df, df)
        assert len(lui.dfs) == 1
        assert lui.texts == ["Hello"]

    @patch("louieai.notebook.cursor.LouieClient")
    def test_lui_supports_indexing(self, mock_client_class):
        """Test lui[-1] syntax works."""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        response1 = Mock(spec=Response, thread_id="test-123")
        response1.text_elements = [{"type": "TextElement", "content": "First"}]
        response1.dataframe_elements = []
        response1.graph_elements = []

        response2 = Mock(spec=Response, thread_id="test-123")
        response2.text_elements = [{"type": "TextElement", "content": "Second"}]
        response2.dataframe_elements = []
        response2.graph_elements = []

        mock_client.add_cell.side_effect = [response1, response2]

        # Reset singleton
        import louieai.notebook

        louieai.notebook._global_cursor = None

        # Use lui
        lui("First query")
        lui("Second query")

        # Test indexing
        assert lui[-1].text == "Second"
        assert lui[-2].text == "First"
        assert lui[0].text == "First"  # Regular indexing
        assert lui[1].text == "Second"
