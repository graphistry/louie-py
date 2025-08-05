"""Comprehensive tests for df/text/g last item behavior across multiple scenarios."""

from unittest.mock import Mock

import pandas as pd

from louieai import Response
from louieai.notebook.cursor import Cursor


class TestMultipleSequentialCalls:
    """Test behavior when multiple lui() calls are made sequentially."""

    def test_three_sequential_calls_with_single_df_each(self):
        """Test 3 sequential lui() calls, each returning 1 df."""
        cursor = Cursor()

        # First call returns df with value 1
        df1 = pd.DataFrame({"value": [1]})
        response1 = Mock(spec=Response)
        response1.dataframe_elements = [{"type": "DfElement", "table": df1}]
        response1.text_elements = []
        response1.graph_elements = []
        cursor._history.append(response1)

        # After first call
        assert cursor.df is not None
        pd.testing.assert_frame_equal(cursor.df, df1)
        assert len(cursor.dfs) == 1
        pd.testing.assert_frame_equal(cursor.dfs[0], df1)

        # Second call returns df with value 2
        df2 = pd.DataFrame({"value": [2]})
        response2 = Mock(spec=Response)
        response2.dataframe_elements = [{"type": "DfElement", "table": df2}]
        response2.text_elements = []
        response2.graph_elements = []
        cursor._history.append(response2)

        # After second call - should return df2 (from latest response)
        assert cursor.df is not None
        pd.testing.assert_frame_equal(cursor.df, df2)
        assert len(cursor.dfs) == 1  # Only from latest response
        pd.testing.assert_frame_equal(cursor.dfs[0], df2)

        # Third call returns df with value 3
        df3 = pd.DataFrame({"value": [3]})
        response3 = Mock(spec=Response)
        response3.dataframe_elements = [{"type": "DfElement", "table": df3}]
        response3.text_elements = []
        response3.graph_elements = []
        cursor._history.append(response3)

        # After third call - should return df3 (from latest response)
        assert cursor.df is not None
        pd.testing.assert_frame_equal(cursor.df, df3)
        assert len(cursor.dfs) == 1  # Only from latest response
        pd.testing.assert_frame_equal(cursor.dfs[0], df3)

        # Verify we can still access history
        pd.testing.assert_frame_equal(cursor[-3].df, df1)
        pd.testing.assert_frame_equal(cursor[-2].df, df2)
        pd.testing.assert_frame_equal(cursor[-1].df, df3)

    def test_three_sequential_calls_with_single_text_each(self):
        """Test 3 sequential lui() calls, each returning 1 text."""
        cursor = Cursor()

        # First call
        response1 = Mock(spec=Response)
        response1.dataframe_elements = []
        response1.text_elements = [{"type": "TextElement", "content": "Text 1"}]
        response1.graph_elements = []
        cursor._history.append(response1)

        assert cursor.text == "Text 1"
        assert cursor.texts == ["Text 1"]

        # Second call
        response2 = Mock(spec=Response)
        response2.dataframe_elements = []
        response2.text_elements = [{"type": "TextElement", "content": "Text 2"}]
        response2.graph_elements = []
        cursor._history.append(response2)

        assert cursor.text == "Text 2"
        assert cursor.texts == ["Text 2"]  # Only from latest response

        # Third call
        response3 = Mock(spec=Response)
        response3.dataframe_elements = []
        response3.text_elements = [{"type": "TextElement", "content": "Text 3"}]
        response3.graph_elements = []
        cursor._history.append(response3)

        assert cursor.text == "Text 3"
        assert cursor.texts == ["Text 3"]  # Only from latest response

        # Verify history access
        assert cursor[-3].text == "Text 1"
        assert cursor[-2].text == "Text 2"
        assert cursor[-1].text == "Text 3"

    def test_three_sequential_calls_with_single_graph_each(self):
        """Test 3 sequential lui() calls, each returning 1 graph."""
        cursor = Cursor()

        # First call
        response1 = Mock(spec=Response)
        response1.dataframe_elements = []
        response1.text_elements = []
        response1.graph_elements = [{"type": "GraphElement", "id": "graph1"}]
        cursor._history.append(response1)

        assert cursor.g == {"type": "GraphElement", "id": "graph1"}
        assert len(cursor.gs) == 1

        # Second call
        response2 = Mock(spec=Response)
        response2.dataframe_elements = []
        response2.text_elements = []
        response2.graph_elements = [{"type": "GraphElement", "id": "graph2"}]
        cursor._history.append(response2)

        assert cursor.g == {"type": "GraphElement", "id": "graph2"}
        assert len(cursor.gs) == 1  # Only from latest response

        # Third call
        response3 = Mock(spec=Response)
        response3.dataframe_elements = []
        response3.text_elements = []
        response3.graph_elements = [{"type": "GraphElement", "id": "graph3"}]
        cursor._history.append(response3)

        assert cursor.g == {"type": "GraphElement", "id": "graph3"}
        assert len(cursor.gs) == 1  # Only from latest response

        # Verify history access
        assert cursor[-3].g == {"type": "GraphElement", "id": "graph1"}
        assert cursor[-2].g == {"type": "GraphElement", "id": "graph2"}
        assert cursor[-1].g == {"type": "GraphElement", "id": "graph3"}


class TestSingleCallMultipleResults:
    """Test behavior when a single lui() call returns multiple results."""

    def test_single_call_with_three_dfs(self):
        """Test single lui() call returning 3 dataframes."""
        cursor = Cursor()

        # Single call returns 3 dataframes
        df1 = pd.DataFrame({"value": [1]})
        df2 = pd.DataFrame({"value": [2]})
        df3 = pd.DataFrame({"value": [3]})

        response = Mock(spec=Response)
        response.dataframe_elements = [
            {"type": "DfElement", "table": df1},
            {"type": "DfElement", "table": df2},
            {"type": "DfElement", "table": df3},
        ]
        response.text_elements = []
        response.graph_elements = []
        cursor._history.append(response)

        # df should return the LAST dataframe (df3)
        assert cursor.df is not None
        pd.testing.assert_frame_equal(cursor.df, df3)

        # dfs should return all three in order
        assert len(cursor.dfs) == 3
        pd.testing.assert_frame_equal(cursor.dfs[0], df1)
        pd.testing.assert_frame_equal(cursor.dfs[1], df2)
        pd.testing.assert_frame_equal(cursor.dfs[2], df3)

    def test_single_call_with_three_texts(self):
        """Test single lui() call returning 3 text elements."""
        cursor = Cursor()

        response = Mock(spec=Response)
        response.dataframe_elements = []
        response.text_elements = [
            {"type": "TextElement", "content": "First"},
            {"type": "TextElement", "content": "Middle"},
            {"type": "TextElement", "content": "Last"},
        ]
        response.graph_elements = []
        cursor._history.append(response)

        # text should return the LAST text
        assert cursor.text == "Last"

        # texts should return all three in order
        assert cursor.texts == ["First", "Middle", "Last"]

    def test_single_call_with_three_graphs(self):
        """Test single lui() call returning 3 graph elements."""
        cursor = Cursor()

        response = Mock(spec=Response)
        response.dataframe_elements = []
        response.text_elements = []
        response.graph_elements = [
            {"type": "GraphElement", "id": "graph1", "order": 1},
            {"type": "GraphElement", "id": "graph2", "order": 2},
            {"type": "GraphElement", "id": "graph3", "order": 3},
        ]
        cursor._history.append(response)

        # g should return the LAST graph
        assert cursor.g == {"type": "GraphElement", "id": "graph3", "order": 3}

        # gs should return all three in order
        assert len(cursor.gs) == 3
        assert cursor.gs[0]["id"] == "graph1"
        assert cursor.gs[1]["id"] == "graph2"
        assert cursor.gs[2]["id"] == "graph3"


class TestMixedScenarios:
    """Test mixed scenarios with multiple calls and multiple results."""

    def test_multiple_calls_with_multiple_dfs_each(self):
        """Test multiple lui() calls, each returning multiple dfs."""
        cursor = Cursor()

        # First call returns 2 dfs
        df1_1 = pd.DataFrame({"call": [1], "df": [1]})
        df1_2 = pd.DataFrame({"call": [1], "df": [2]})
        response1 = Mock(spec=Response)
        response1.dataframe_elements = [
            {"type": "DfElement", "table": df1_1},
            {"type": "DfElement", "table": df1_2},
        ]
        response1.text_elements = []
        response1.graph_elements = []
        cursor._history.append(response1)

        # After first call
        pd.testing.assert_frame_equal(cursor.df, df1_2)  # Last df from call
        assert len(cursor.dfs) == 2

        # Second call returns 3 dfs
        df2_1 = pd.DataFrame({"call": [2], "df": [1]})
        df2_2 = pd.DataFrame({"call": [2], "df": [2]})
        df2_3 = pd.DataFrame({"call": [2], "df": [3]})
        response2 = Mock(spec=Response)
        response2.dataframe_elements = [
            {"type": "DfElement", "table": df2_1},
            {"type": "DfElement", "table": df2_2},
            {"type": "DfElement", "table": df2_3},
        ]
        response2.text_elements = []
        response2.graph_elements = []
        cursor._history.append(response2)

        # After second call - should get last df from latest response
        pd.testing.assert_frame_equal(cursor.df, df2_3)
        assert len(cursor.dfs) == 3  # Only from latest response

        # Verify history access
        pd.testing.assert_frame_equal(cursor[-2].df, df1_2)  # Last from first call
        pd.testing.assert_frame_equal(cursor[-1].df, df2_3)  # Last from second call

    def test_edge_cases_empty_responses(self):
        """Test edge cases with empty responses between valid ones."""
        cursor = Cursor()

        # First call with data
        df1 = pd.DataFrame({"value": [1]})
        response1 = Mock(spec=Response)
        response1.dataframe_elements = [{"type": "DfElement", "table": df1}]
        response1.text_elements = [{"type": "TextElement", "content": "Text 1"}]
        response1.graph_elements = [{"type": "GraphElement", "id": "graph1"}]
        cursor._history.append(response1)

        assert cursor.df is not None
        assert cursor.text == "Text 1"
        assert cursor.g["id"] == "graph1"

        # Second call with empty response
        response2 = Mock(spec=Response)
        response2.dataframe_elements = []
        response2.text_elements = []
        response2.graph_elements = []
        cursor._history.append(response2)

        # Should return None since latest response has no data
        assert cursor.df is None
        assert cursor.text is None
        assert cursor.g is None
        assert cursor.dfs == []
        assert cursor.texts == []
        assert cursor.gs == []

        # Third call with new data
        df3 = pd.DataFrame({"value": [3]})
        response3 = Mock(spec=Response)
        response3.dataframe_elements = [{"type": "DfElement", "table": df3}]
        response3.text_elements = [{"type": "TextElement", "content": "Text 3"}]
        response3.graph_elements = [{"type": "GraphElement", "id": "graph3"}]
        cursor._history.append(response3)

        # Should return data from latest response
        pd.testing.assert_frame_equal(cursor.df, df3)
        assert cursor.text == "Text 3"
        assert cursor.g["id"] == "graph3"

        # History still accessible
        pd.testing.assert_frame_equal(cursor[-3].df, df1)
        assert cursor[-2].df is None
        pd.testing.assert_frame_equal(cursor[-1].df, df3)
