"""Tests for DataFrame access properties."""

from unittest.mock import Mock

import pandas as pd

from louieai import Response
from louieai.notebook.cursor import Cursor, ResponseProxy


class TestDataFrameAccess:
    """Test DataFrame access properties."""

    def test_df_returns_none_when_no_dataframe(self):
        """Test df returns None when no dataframe in response."""
        cursor = Cursor()
        assert cursor.df is None

        # Add response without dataframes
        mock_response = Mock(spec=Response)
        mock_response.dataframe_elements = []
        mock_response.text_elements = [{"type": "TextElement", "content": "Hello"}]
        cursor._history.append(mock_response)

        assert cursor.df is None

    def test_df_returns_last_dataframe(self):
        """Test df returns last dataframe when available."""
        cursor = Cursor()

        # Create test dataframes
        df1 = pd.DataFrame({"a": [1, 2, 3]})
        df2 = pd.DataFrame({"b": [4, 5, 6]})

        # Mock response with dataframes
        mock_response = Mock(spec=Response)
        mock_response.dataframe_elements = [
            {"type": "DfElement", "table": df1},
            {"type": "DfElement", "table": df2},
        ]
        cursor._history.append(mock_response)

        # Should return last dataframe
        result = cursor.df
        assert result is not None
        pd.testing.assert_frame_equal(result, df2)

    def test_dfs_returns_empty_list_when_none(self):
        """Test dfs returns empty list when no dataframes."""
        cursor = Cursor()
        assert cursor.dfs == []

        # Add response without dataframes
        mock_response = Mock(spec=Response)
        mock_response.dataframe_elements = []
        cursor._history.append(mock_response)

        assert cursor.dfs == []

    def test_dfs_returns_all_dataframes(self):
        """Test dfs returns all dataframes."""
        cursor = Cursor()

        # Create test dataframes
        df1 = pd.DataFrame({"a": [1, 2, 3]})
        df2 = pd.DataFrame({"b": [4, 5, 6]})

        # Mock response
        mock_response = Mock(spec=Response)
        mock_response.dataframe_elements = [
            {"type": "DfElement", "table": df1},
            {"type": "DfElement", "table": df2},
        ]
        cursor._history.append(mock_response)

        dfs = cursor.dfs
        assert len(dfs) == 2
        pd.testing.assert_frame_equal(dfs[0], df1)
        pd.testing.assert_frame_equal(dfs[1], df2)

    def test_text_returns_none_when_no_text(self):
        """Test text returns None when no text elements."""
        cursor = Cursor()
        assert cursor.text is None

        # Add response without text
        mock_response = Mock(spec=Response)
        mock_response.text_elements = []
        cursor._history.append(mock_response)

        assert cursor.text is None

    def test_text_returns_last_text(self):
        """Test text returns last text element."""
        cursor = Cursor()

        mock_response = Mock(spec=Response)
        mock_response.text_elements = [
            {"type": "TextElement", "content": "First text"},
            {"type": "TextElement", "content": "Second text"},
        ]
        cursor._history.append(mock_response)

        assert cursor.text == "Second text"

    def test_texts_returns_all_text_elements(self):
        """Test texts returns all text elements."""
        cursor = Cursor()

        mock_response = Mock(spec=Response)
        mock_response.text_elements = [
            {"type": "TextElement", "content": "First text"},
            {"type": "TextElement", "content": "Second text"},
        ]
        cursor._history.append(mock_response)

        texts = cursor.texts
        assert texts == ["First text", "Second text"]

    def test_elements_returns_all_typed_elements(self):
        """Test elements returns all elements with type tags."""
        cursor = Cursor()

        # Create mixed response
        df1 = pd.DataFrame({"a": [1, 2, 3]})

        mock_response = Mock(spec=Response)
        mock_response.text_elements = [{"type": "TextElement", "content": "Some text"}]
        mock_response.dataframe_elements = [{"type": "DfElement", "table": df1}]
        mock_response.graph_elements = []
        cursor._history.append(mock_response)

        elements = cursor.elements
        assert len(elements) == 2

        # Check text element
        assert elements[0]["type"] == "text"
        assert elements[0]["value"] == "Some text"

        # Check dataframe element
        assert elements[1]["type"] == "dataframe"
        pd.testing.assert_frame_equal(elements[1]["value"], df1)

    def test_history_access_with_getitem(self):
        """Test accessing history with lui[-1] syntax."""
        cursor = Cursor()

        # Add multiple responses
        df1 = pd.DataFrame({"a": [1, 2, 3]})
        df2 = pd.DataFrame({"b": [4, 5, 6]})

        response1 = Mock(spec=Response)
        response1.dataframe_elements = [{"type": "DfElement", "table": df1}]
        response1.text_elements = [{"type": "TextElement", "content": "First"}]
        response1.graph_elements = []

        response2 = Mock(spec=Response)
        response2.dataframe_elements = [{"type": "DfElement", "table": df2}]
        response2.text_elements = [{"type": "TextElement", "content": "Second"}]
        response2.graph_elements = []

        cursor._history.extend([response1, response2])

        # Test negative indexing
        assert cursor[-1].text == "Second"
        assert cursor[-2].text == "First"

        # Test dataframe access - now returns last df from each response
        pd.testing.assert_frame_equal(cursor[-1].df, df2)
        pd.testing.assert_frame_equal(cursor[-2].df, df1)

    def test_history_access_out_of_bounds(self):
        """Test history access with invalid index returns empty proxy."""
        cursor = Cursor()

        # Empty history
        proxy = cursor[-1]
        assert proxy.df is None
        assert proxy.text is None
        assert proxy.dfs == []
        assert proxy.texts == []
        assert proxy.elements == []

        # Add one response
        response = Mock(spec=Response)
        response.text_elements = [{"type": "TextElement", "content": "Test"}]
        response.dataframe_elements = []
        response.graph_elements = []
        cursor._history.append(response)

        # Out of bounds
        proxy = cursor[-10]
        assert proxy.df is None
        assert proxy.text is None

    def test_charts_and_images_empty(self):
        """Test charts and images return empty lists (not implemented yet)."""
        cursor = Cursor()

        # Even with response
        response = Mock(spec=Response)
        cursor._history.append(response)

        assert cursor.charts == []
        assert cursor.images == []

    def test_dataframe_without_table_key(self):
        """Test handling dataframe elements without 'table' key."""
        cursor = Cursor()

        mock_response = Mock(spec=Response)
        mock_response.dataframe_elements = [
            {"type": "DfElement"},  # Missing 'table' key
            {"type": "DfElement", "table": "not a dataframe"},  # Wrong type
        ]
        cursor._history.append(mock_response)

        assert cursor.df is None
        assert cursor.dfs == []

    def test_multiple_responses_returns_last(self):
        """Test that df/text/g properties return last item from multiple results."""
        cursor = Cursor()

        # Create test data with 3 of each type
        df1 = pd.DataFrame({"col": [1]})
        df2 = pd.DataFrame({"col": [2]})
        df3 = pd.DataFrame({"col": [3]})

        mock_response = Mock(spec=Response)
        mock_response.dataframe_elements = [
            {"type": "DfElement", "table": df1},
            {"type": "DfElement", "table": df2},
            {"type": "DfElement", "table": df3},
        ]
        mock_response.text_elements = [
            {"type": "TextElement", "content": "First"},
            {"type": "TextElement", "content": "Middle"},
            {"type": "TextElement", "content": "Last"},
        ]
        mock_response.graph_elements = [
            {"type": "GraphElement", "id": "graph1"},
            {"type": "GraphElement", "id": "graph2"},
            {"type": "GraphElement", "id": "graph3"},
        ]
        cursor._history.append(mock_response)

        # Verify properties return last items
        pd.testing.assert_frame_equal(cursor.df, df3)
        assert cursor.text == "Last"
        assert cursor.g["id"] == "graph3"

        # Verify all items are still accessible
        assert len(cursor.dfs) == 3
        assert len(cursor.texts) == 3
        assert len(cursor.gs) == 3


class TestResponseProxy:
    """Test ResponseProxy for historical access."""

    def test_proxy_with_none_response(self):
        """Test proxy handles None response gracefully."""
        proxy = ResponseProxy(None)

        assert proxy.df is None
        assert proxy.dfs == []
        assert proxy.text is None
        assert proxy.texts == []
        assert proxy.elements == []

    def test_proxy_delegates_to_response(self):
        """Test proxy correctly delegates to underlying response."""
        df = pd.DataFrame({"x": [1, 2, 3]})

        response = Mock(spec=Response)
        response.text_elements = [{"type": "TextElement", "content": "Hello"}]
        response.dataframe_elements = [{"type": "DfElement", "table": df}]
        response.graph_elements = []

        proxy = ResponseProxy(response)

        assert proxy.text == "Hello"
        pd.testing.assert_frame_equal(proxy.df, df)
        assert len(proxy.elements) == 2

    def test_proxy_returns_last_items(self):
        """Test proxy returns last items from multiple results."""
        df1 = pd.DataFrame({"a": [1]})
        df2 = pd.DataFrame({"b": [2]})
        df3 = pd.DataFrame({"c": [3]})

        response = Mock(spec=Response)
        response.dataframe_elements = [
            {"type": "DfElement", "table": df1},
            {"type": "DfElement", "table": df2},
            {"type": "DfElement", "table": df3},
        ]
        response.text_elements = [
            {"type": "TextElement", "content": "Start"},
            {"type": "TextElement", "content": "End"},
        ]
        response.graph_elements = [
            {"type": "GraphElement", "dataset_id": "g1"},
            {"type": "GraphElement", "dataset_id": "g2"},
        ]

        proxy = ResponseProxy(response)

        # Verify last items are returned
        pd.testing.assert_frame_equal(proxy.df, df3)
        assert proxy.text == "End"
        assert proxy.g["dataset_id"] == "g2"
