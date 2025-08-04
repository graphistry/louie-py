"""Test that dataframe elements include metadata like block_id."""

import pandas as pd

from louieai._client import Response
from louieai.notebook.cursor import ResponseProxy


class TestDataframeElementMetadata:
    """Test that dataframe elements preserve metadata."""

    def test_dataframe_element_includes_metadata(self):
        """Test that dataframe elements include id, df_id, block_id."""
        # Create a response with a dataframe element that has metadata
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

        response = Response(
            thread_id="D_test",
            elements=[
                {
                    "id": "B_001",
                    "type": "DfElement",
                    "df_id": "databricks_result_456",
                    "block_id": "block_789",
                    "table": df,
                }
            ],
        )

        proxy = ResponseProxy(response)
        elements = proxy.elements

        # Should have one dataframe element
        df_elements = [e for e in elements if e["type"] == "dataframe"]
        assert len(df_elements) == 1

        df_elem = df_elements[0]

        # Check it has both value and df (same DataFrame)
        assert "value" in df_elem
        assert "df" in df_elem
        assert df_elem["value"] is df_elem["df"]
        pd.testing.assert_frame_equal(df_elem["value"], df)
        pd.testing.assert_frame_equal(df_elem["df"], df)

        # Check metadata is preserved
        assert df_elem["id"] == "B_001"
        assert df_elem["df_id"] == "databricks_result_456"
        assert df_elem["block_id"] == "block_789"

    def test_dataframe_element_missing_metadata(self):
        """Test dataframe element when some metadata is missing."""
        df = pd.DataFrame({"data": [1, 2]})

        response = Response(
            thread_id="D_test",
            elements=[
                {
                    "id": "B_002",  # Only has id, no df_id/block_id
                    "type": "DfElement",
                    "table": df,
                }
            ],
        )

        proxy = ResponseProxy(response)
        elements = proxy.elements

        df_elem = next(e for e in elements if e["type"] == "dataframe")

        # Should have id but not df_id/block_id
        assert df_elem["id"] == "B_002"
        assert "df_id" not in df_elem
        assert "block_id" not in df_elem

        # DataFrame should still be accessible
        pd.testing.assert_frame_equal(df_elem["df"], df)

    def test_dataframe_element_backward_compatibility(self):
        """Test that 'value' field is preserved for backward compatibility."""
        df = pd.DataFrame({"test": [1]})

        response = Response(
            thread_id="D_test",
            elements=[{"id": "B_003", "type": "DfElement", "table": df}],
        )

        proxy = ResponseProxy(response)
        elements = proxy.elements

        df_elem = next(e for e in elements if e["type"] == "dataframe")

        # Both value and df should work
        assert "value" in df_elem
        assert "df" in df_elem

        # Should be the same DataFrame object
        assert df_elem["value"] is df_elem["df"]

    def test_usage_example(self):
        """Test realistic usage example."""
        df = pd.DataFrame(
            {
                "ClientIP": ["107.77.213.173", "40.97.148.181"],
                "Operation": ["FileAccessed", "SearchQueryPerformed"],
            }
        )

        response = Response(
            thread_id="D_databricks_123",
            elements=[
                {"id": "B_001", "type": "TextElement", "text": "Query executed"},
                {
                    "id": "B_002",
                    "type": "DfElement",
                    "df_id": "databricks_result_456",
                    "table": df,
                },
            ],
        )

        proxy = ResponseProxy(response)

        # User can now access both the DataFrame and its metadata
        df_elements = [e for e in proxy.elements if e["type"] == "dataframe"]

        if df_elements:
            df_elem = df_elements[0]

            # Get the DataFrame
            dataframe = df_elem["df"]  # or df_elem["value"]

            # Get the block ID for other operations
            block_id = (
                df_elem.get("df_id") or df_elem.get("block_id") or df_elem.get("id")
            )

            # Verify
            assert isinstance(dataframe, pd.DataFrame)
            assert dataframe.shape == (2, 2)
            assert block_id == "databricks_result_456"
