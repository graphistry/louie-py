"""Test for the expected behavior of df/text/g properties with history navigation.

Expected behavior:
- lui.df → latest df in latest run
- lui.dfs[-1] → latest df in latest run
- lui[-1].df → latest df in previous run
- lui[-1].dfs[-1] → latest df in previous run
"""

from unittest.mock import Mock

import pandas as pd

from louieai import Response
from louieai.notebook.cursor import Cursor


class TestExpectedDataFrameBehavior:
    """Test the expected behavior for dataframe access patterns."""

    def test_lui_df_returns_latest_df_in_latest_run(self):
        """Test lui.df returns the latest df from the most recent response."""
        cursor = Cursor()

        # First response with 2 dataframes
        df1_1 = pd.DataFrame({"response": [1], "df_index": [0]})
        df1_2 = pd.DataFrame({"response": [1], "df_index": [1]})
        response1 = Mock(spec=Response)
        response1.dataframe_elements = [
            {"type": "DfElement", "table": df1_1},
            {"type": "DfElement", "table": df1_2},
        ]
        response1.text_elements = []
        response1.graph_elements = []
        cursor._history.append(response1)

        # Second response with 3 dataframes
        df2_1 = pd.DataFrame({"response": [2], "df_index": [0]})
        df2_2 = pd.DataFrame({"response": [2], "df_index": [1]})
        df2_3 = pd.DataFrame({"response": [2], "df_index": [2]})
        response2 = Mock(spec=Response)
        response2.dataframe_elements = [
            {"type": "DfElement", "table": df2_1},
            {"type": "DfElement", "table": df2_2},
            {"type": "DfElement", "table": df2_3},
        ]
        response2.text_elements = []
        response2.graph_elements = []
        cursor._history.append(response2)

        # lui.df should return df2_3 (latest df in latest run)
        pd.testing.assert_frame_equal(cursor.df, df2_3)

        # lui.dfs[-1] should also return df2_3
        pd.testing.assert_frame_equal(cursor.dfs[-1], df2_3)

    def test_lui_bracket_minus_one_df_returns_latest_df_in_previous_run(self):
        """Test lui[-1].df returns the latest df from the previous response."""
        cursor = Cursor()

        # First response with 2 dataframes
        df1_1 = pd.DataFrame({"response": [1], "df_index": [0]})
        df1_2 = pd.DataFrame({"response": [1], "df_index": [1]})
        response1 = Mock(spec=Response)
        response1.dataframe_elements = [
            {"type": "DfElement", "table": df1_1},
            {"type": "DfElement", "table": df1_2},
        ]
        response1.text_elements = []
        response1.graph_elements = []
        cursor._history.append(response1)

        # Second response with 3 dataframes
        df2_1 = pd.DataFrame({"response": [2], "df_index": [0]})
        df2_2 = pd.DataFrame({"response": [2], "df_index": [1]})
        df2_3 = pd.DataFrame({"response": [2], "df_index": [2]})
        response2 = Mock(spec=Response)
        response2.dataframe_elements = [
            {"type": "DfElement", "table": df2_1},
            {"type": "DfElement", "table": df2_2},
            {"type": "DfElement", "table": df2_3},
        ]
        response2.text_elements = []
        response2.graph_elements = []
        cursor._history.append(response2)

        # lui[-1].df should return df2_3 (latest df in current/last run)
        pd.testing.assert_frame_equal(cursor[-1].df, df2_3)

        # lui[-1].dfs[-1] should also return df2_3
        pd.testing.assert_frame_equal(cursor[-1].dfs[-1], df2_3)

        # lui[-2].df should return df1_2 (latest df in previous run)
        pd.testing.assert_frame_equal(cursor[-2].df, df1_2)

        # lui[-2].dfs[-1] should also return df1_2
        pd.testing.assert_frame_equal(cursor[-2].dfs[-1], df1_2)

    def test_three_sequential_calls_navigation(self):
        """Test navigation with 3 sequential lui() calls."""
        cursor = Cursor()

        # Call 1: returns 2 dfs
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

        # Call 2: returns 3 dfs
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

        # Call 3: returns 1 df
        df3_1 = pd.DataFrame({"call": [3], "df": [1]})
        response3 = Mock(spec=Response)
        response3.dataframe_elements = [
            {"type": "DfElement", "table": df3_1},
        ]
        response3.text_elements = []
        response3.graph_elements = []
        cursor._history.append(response3)

        # Verify lui.df returns latest df from latest response
        pd.testing.assert_frame_equal(cursor.df, df3_1)
        pd.testing.assert_frame_equal(cursor.dfs[-1], df3_1)

        # Verify lui[-1].df returns latest df from current (last) response
        pd.testing.assert_frame_equal(cursor[-1].df, df3_1)

        # Verify lui[-2].df returns latest df from second response
        pd.testing.assert_frame_equal(cursor[-2].df, df2_3)
        pd.testing.assert_frame_equal(cursor[-2].dfs[-1], df2_3)

        # Verify lui[-3].df returns latest df from first response
        pd.testing.assert_frame_equal(cursor[-3].df, df1_2)
        pd.testing.assert_frame_equal(cursor[-3].dfs[-1], df1_2)

        # Verify we can access all dfs from each response
        assert len(cursor[-3].dfs) == 2
        assert len(cursor[-2].dfs) == 3
        assert len(cursor[-1].dfs) == 1
        assert len(cursor.dfs) == 1  # Same as cursor[-1].dfs

    def test_text_behavior_matches_df_behavior(self):
        """Test that text/texts behave the same way as df/dfs."""
        cursor = Cursor()

        # Response 1: 2 texts
        response1 = Mock(spec=Response)
        response1.dataframe_elements = []
        response1.text_elements = [
            {"type": "TextElement", "content": "Text 1.1"},
            {"type": "TextElement", "content": "Text 1.2"},
        ]
        response1.graph_elements = []
        cursor._history.append(response1)

        # Response 2: 3 texts
        response2 = Mock(spec=Response)
        response2.dataframe_elements = []
        response2.text_elements = [
            {"type": "TextElement", "content": "Text 2.1"},
            {"type": "TextElement", "content": "Text 2.2"},
            {"type": "TextElement", "content": "Text 2.3"},
        ]
        response2.graph_elements = []
        cursor._history.append(response2)

        # lui.text returns latest text from latest response
        assert cursor.text == "Text 2.3"
        assert cursor.texts[-1] == "Text 2.3"

        # lui[-1].text returns latest text from current (last) response
        assert cursor[-1].text == "Text 2.3"
        assert cursor[-1].texts[-1] == "Text 2.3"

        # lui[-2].text returns latest text from previous response
        assert cursor[-2].text == "Text 1.2"
        assert cursor[-2].texts[-1] == "Text 1.2"

    def test_graph_behavior_matches_df_behavior(self):
        """Test that g/gs behave the same way as df/dfs."""
        cursor = Cursor()

        # Response 1: 2 graphs
        response1 = Mock(spec=Response)
        response1.dataframe_elements = []
        response1.text_elements = []
        response1.graph_elements = [
            {"type": "GraphElement", "id": "g1.1"},
            {"type": "GraphElement", "id": "g1.2"},
        ]
        cursor._history.append(response1)

        # Response 2: 3 graphs
        response2 = Mock(spec=Response)
        response2.dataframe_elements = []
        response2.text_elements = []
        response2.graph_elements = [
            {"type": "GraphElement", "id": "g2.1"},
            {"type": "GraphElement", "id": "g2.2"},
            {"type": "GraphElement", "id": "g2.3"},
        ]
        cursor._history.append(response2)

        # lui.g returns latest graph from latest response
        assert cursor.g["id"] == "g2.3"
        assert cursor.gs[-1]["id"] == "g2.3"

        # lui[-1].g returns latest graph from current (last) response
        assert cursor[-1].g["id"] == "g2.3"
        assert cursor[-1].gs[-1]["id"] == "g2.3"

        # lui[-2].g returns latest graph from previous response
        assert cursor[-2].g["id"] == "g1.2"
        assert cursor[-2].gs[-1]["id"] == "g1.2"

    def test_empty_response_behavior(self):
        """Test behavior when latest response has no dataframes."""
        cursor = Cursor()

        # Response 1: has dataframes
        df1 = pd.DataFrame({"data": [1, 2, 3]})
        response1 = Mock(spec=Response)
        response1.dataframe_elements = [{"type": "DfElement", "table": df1}]
        response1.text_elements = [{"type": "TextElement", "content": "Has data"}]
        response1.graph_elements = []
        cursor._history.append(response1)

        # Response 2: no dataframes, just text
        response2 = Mock(spec=Response)
        response2.dataframe_elements = []
        response2.text_elements = [{"type": "TextElement", "content": "No data"}]
        response2.graph_elements = []
        cursor._history.append(response2)

        # lui.df returns None (no df in latest response)
        assert cursor.df is None
        assert cursor.dfs == []

        # lui.text returns text from latest response
        assert cursor.text == "No data"

        # lui[-2].df returns df from first response
        pd.testing.assert_frame_equal(cursor[-2].df, df1)

        # lui[-1].df returns None (no df in this response)
        assert cursor[-1].df is None

    def test_comprehensive_multi_response_scenario(self):
        """Test comprehensive scenario with multiple responses and all elements."""
        cursor = Cursor()

        # Response 1: Mix of elements
        df1_1 = pd.DataFrame({"step": [1], "data": ["initial"]})
        df1_2 = pd.DataFrame({"step": [1], "data": ["refined"]})
        response1 = Mock(spec=Response)
        response1.dataframe_elements = [
            {"type": "DfElement", "table": df1_1},
            {"type": "DfElement", "table": df1_2},
        ]
        response1.text_elements = [
            {"type": "TextElement", "content": "Starting analysis"},
            {"type": "TextElement", "content": "Found initial results"},
        ]
        response1.graph_elements = [
            {"type": "GraphElement", "id": "graph1"},
        ]
        cursor._history.append(response1)

        # Verify state after first response
        pd.testing.assert_frame_equal(cursor.df, df1_2)
        assert cursor.text == "Found initial results"
        assert cursor.g["id"] == "graph1"

        # Response 2: More data
        df2_1 = pd.DataFrame({"step": [2], "data": ["intermediate1"]})
        df2_2 = pd.DataFrame({"step": [2], "data": ["intermediate2"]})
        df2_3 = pd.DataFrame({"step": [2], "data": ["intermediate3"]})
        response2 = Mock(spec=Response)
        response2.dataframe_elements = [
            {"type": "DfElement", "table": df2_1},
            {"type": "DfElement", "table": df2_2},
            {"type": "DfElement", "table": df2_3},
        ]
        response2.text_elements = [
            {"type": "TextElement", "content": "Processing continues"},
        ]
        response2.graph_elements = [
            {"type": "GraphElement", "id": "graph2.1"},
            {"type": "GraphElement", "id": "graph2.2"},
        ]
        cursor._history.append(response2)

        # Verify state after second response
        pd.testing.assert_frame_equal(cursor.df, df2_3)
        assert cursor.text == "Processing continues"
        assert cursor.g["id"] == "graph2.2"

        # Response 3: Final summary (text only)
        response3 = Mock(spec=Response)
        response3.dataframe_elements = []
        response3.text_elements = [
            {"type": "TextElement", "content": "Analysis complete"},
            {"type": "TextElement", "content": "Total records processed: 1000"},
            {"type": "TextElement", "content": "Summary: All good"},
        ]
        response3.graph_elements = []
        cursor._history.append(response3)

        # Current state: latest response has no df
        assert cursor.df is None
        assert cursor.text == "Summary: All good"
        assert cursor.g is None

        # Navigation to previous responses
        pd.testing.assert_frame_equal(cursor[-2].df, df2_3)
        assert cursor[-2].text == "Processing continues"
        assert cursor[-2].g["id"] == "graph2.2"

        pd.testing.assert_frame_equal(cursor[-3].df, df1_2)
        assert cursor[-3].text == "Found initial results"
        assert cursor[-3].g["id"] == "graph1"

        # Verify all elements are accessible through history
        assert len(cursor[-3].dfs) == 2
        assert len(cursor[-3].texts) == 2
        assert len(cursor[-3].gs) == 1

        assert len(cursor[-2].dfs) == 3
        assert len(cursor[-2].texts) == 1
        assert len(cursor[-2].gs) == 2

        assert len(cursor[-1].dfs) == 0
        assert len(cursor[-1].texts) == 3
        assert len(cursor[-1].gs) == 0
