"""Integration tests for Arrow dataframe fetching."""

from io import BytesIO
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pyarrow as pa
import pyarrow.ipc as ipc
import pytest

from louieai import louie


class TestArrowDataFrameIntegration:
    """Test Arrow dataframe fetching in notebook context."""

    def create_arrow_response(self, df):
        """Helper to create Arrow format response."""
        # Convert to Arrow table
        table = pa.Table.from_pandas(df)

        # Serialize to Arrow IPC format
        sink = BytesIO()
        with ipc.new_stream(sink, table.schema) as writer:
            writer.write_table(table)

        # Get the bytes
        arrow_bytes = sink.getvalue()

        # Create mock response
        mock_response = Mock()
        mock_response.content = arrow_bytes
        mock_response.raise_for_status = Mock()

        return mock_response

    def test_notebook_with_arrow_dataframe(self):
        """Test complete notebook workflow with Arrow dataframe fetching."""
        # Create test dataframe
        test_df = pd.DataFrame(
            {
                "user_id": ["u1", "u2", "u3", "u4", "u5"],
                "score": [100, 85, 92, 78, 95],
                "status": ["active", "active", "pending", "active", "inactive"],
            }
        )

        # Mock the streaming response
        mock_stream_response = Mock()
        mock_stream_response.raise_for_status = Mock()
        mock_stream_response.iter_lines.return_value = iter(
            [
                '{"dthread_id": "D_test123"}',
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Here is your data analysis:"}}',
                '{"payload": {"id": "B_002", "type": "DfElement", '
                '"df_id": "df_456", "metadata": {"shape": [5, 3]}}}',
            ]
        )

        # Create Arrow response
        arrow_response = self.create_arrow_response(test_df)

        # Mock client setup
        MagicMock()

        # Create cursor
        lui = louie(graphistry_client=MagicMock())

        with patch("louieai._client.httpx.Client") as mock_httpx:
            # Setup streaming mock
            mock_stream_cm = Mock()
            mock_stream_cm.__enter__ = Mock(return_value=mock_stream_response)
            mock_stream_cm.__exit__ = Mock(return_value=None)

            mock_httpx_instance = Mock()
            mock_httpx_instance.stream.return_value = mock_stream_cm
            mock_httpx_instance.get.return_value = arrow_response
            mock_httpx.return_value.__enter__.return_value = mock_httpx_instance

            # Patch the client's _client attribute
            with patch.object(lui._client, "_client", mock_httpx_instance):
                # Make the query
                result = lui("Analyze the user data")

        # Verify cursor behavior
        assert result is lui
        assert lui.text == "Here is your data analysis:"

        # Verify dataframe was fetched and is accessible
        assert lui.df is not None
        pd.testing.assert_frame_equal(lui.df, test_df)

        # Verify dfs property
        assert len(lui.dfs) == 1
        pd.testing.assert_frame_equal(lui.dfs[0], test_df)

        # Verify Arrow endpoint was called
        mock_httpx_instance.get.assert_called_once()
        call_args = mock_httpx_instance.get.call_args
        assert "/api/dthread/D_test123/df/block/df_456/arrow" in call_args[0][0]

    def test_multiple_dataframes_in_response(self):
        """Test handling multiple dataframes with Arrow fetching."""
        # Create multiple test dataframes
        df1 = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        df2 = pd.DataFrame({"c": [4, 5, 6], "d": ["p", "q", "r"]})

        # Mock streaming response with multiple DfElements
        mock_stream_response = Mock()
        mock_stream_response.raise_for_status = Mock()
        mock_stream_response.iter_lines.return_value = iter(
            [
                '{"dthread_id": "D_test123"}',
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Analysis with multiple datasets:"}}',
                '{"payload": {"id": "B_002", "type": "DfElement", '
                '"df_id": "df_111", "metadata": {"shape": [3, 2]}}}',
                '{"payload": {"id": "B_003", "type": "DfElement", '
                '"df_id": "df_222", "metadata": {"shape": [3, 2]}}}',
            ]
        )

        # Create Arrow responses
        arrow_response1 = self.create_arrow_response(df1)
        arrow_response2 = self.create_arrow_response(df2)

        # Create cursor
        lui = louie(graphistry_client=MagicMock())

        with patch("louieai._client.httpx.Client") as mock_httpx:
            # Setup streaming mock
            mock_stream_cm = Mock()
            mock_stream_cm.__enter__ = Mock(return_value=mock_stream_response)
            mock_stream_cm.__exit__ = Mock(return_value=None)

            mock_httpx_instance = Mock()
            mock_httpx_instance.stream.return_value = mock_stream_cm
            # Return different responses for each df_id
            mock_httpx_instance.get.side_effect = [arrow_response1, arrow_response2]
            mock_httpx.return_value.__enter__.return_value = mock_httpx_instance

            # Patch the client's _client attribute
            with patch.object(lui._client, "_client", mock_httpx_instance):
                # Make the query
                lui("Show me multiple datasets")

        # Verify both dataframes were fetched
        assert len(lui.dfs) == 2
        pd.testing.assert_frame_equal(lui.dfs[0], df1)
        pd.testing.assert_frame_equal(lui.dfs[1], df2)

        # Verify df property returns last dataframe
        pd.testing.assert_frame_equal(lui.df, df2)

        # Verify both Arrow endpoints were called
        assert mock_httpx_instance.get.call_count == 2
        calls = mock_httpx_instance.get.call_args_list
        assert "/api/dthread/D_test123/df/block/df_111/arrow" in calls[0][0][0]
        assert "/api/dthread/D_test123/df/block/df_222/arrow" in calls[1][0][0]

    def test_arrow_fetch_failure_handling(self):
        """Test graceful handling when Arrow fetch fails."""
        # Mock streaming response with DfElement
        mock_stream_response = Mock()
        mock_stream_response.raise_for_status = Mock()
        mock_stream_response.iter_lines.return_value = iter(
            [
                '{"dthread_id": "D_test123"}',
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Data analysis:"}}',
                '{"payload": {"id": "B_002", "type": "DfElement", '
                '"df_id": "df_bad", "metadata": {"shape": [5, 3]}}}',
            ]
        )

        # Create cursor
        lui = louie(graphistry_client=MagicMock())

        with patch("louieai._client.httpx.Client") as mock_httpx:
            # Setup streaming mock
            mock_stream_cm = Mock()
            mock_stream_cm.__enter__ = Mock(return_value=mock_stream_response)
            mock_stream_cm.__exit__ = Mock(return_value=None)

            mock_httpx_instance = Mock()
            mock_httpx_instance.stream.return_value = mock_stream_cm
            # Make Arrow fetch fail
            mock_httpx_instance.get.side_effect = Exception("Network error")
            mock_httpx.return_value.__enter__.return_value = mock_httpx_instance

            # Patch the client's _client attribute
            with (
                patch.object(lui._client, "_client", mock_httpx_instance),
                pytest.warns(RuntimeWarning, match="Failed to fetch dataframe"),
            ):
                result = lui("Show data that will fail to fetch")

        # Should still return cursor
        assert result is lui
        assert lui.text == "Data analysis:"

        # But dataframe should be None
        assert lui.df is None
        assert lui.dfs == []

        # Elements should still contain DfElement but without table
        df_elements = lui._history[-1].dataframe_elements
        assert len(df_elements) == 1
        assert "table" not in df_elements[0]

    def test_block_id_instead_of_df_id(self):
        """Test that block_id is also recognized for Arrow fetching."""
        test_df = pd.DataFrame({"x": [1, 2, 3]})

        # Mock streaming response using block_id instead of df_id
        mock_stream_response = Mock()
        mock_stream_response.raise_for_status = Mock()
        mock_stream_response.iter_lines.return_value = iter(
            [
                '{"dthread_id": "D_test123"}',
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Data with block_id:"}}',
                '{"payload": {"id": "B_002", "type": "DfElement", '
                '"block_id": "block_789", "metadata": {"shape": [3, 1]}}}',
            ]
        )

        arrow_response = self.create_arrow_response(test_df)

        lui = louie(graphistry_client=MagicMock())

        with patch("louieai._client.httpx.Client") as mock_httpx:
            mock_stream_cm = Mock()
            mock_stream_cm.__enter__ = Mock(return_value=mock_stream_response)
            mock_stream_cm.__exit__ = Mock(return_value=None)

            mock_httpx_instance = Mock()
            mock_httpx_instance.stream.return_value = mock_stream_cm
            mock_httpx_instance.get.return_value = arrow_response
            mock_httpx.return_value.__enter__.return_value = mock_httpx_instance

            with patch.object(lui._client, "_client", mock_httpx_instance):
                lui("Show data with block_id")

        # Verify dataframe was fetched using block_id
        assert lui.df is not None
        pd.testing.assert_frame_equal(lui.df, test_df)

        # Verify correct endpoint was called with block_id
        mock_httpx_instance.get.assert_called_once()
        call_args = mock_httpx_instance.get.call_args
        assert "/api/dthread/D_test123/df/block/block_789/arrow" in call_args[0][0]


@pytest.mark.integration
class TestArrowDataFrameRealIntegration:
    """Integration tests with real Louie instance (requires credentials)."""

    @pytest.fixture
    def real_client(self):
        """Create a real Louie client if credentials are available."""
        from ..utils import load_test_credentials

        creds = load_test_credentials()
        if not creds:
            pytest.skip("Test credentials not available")

        import graphistry

        graphistry_client = graphistry.register(
            api=creds["api_version"],
            server=creds["server"],
            username=creds["username"],
            password=creds["password"],
        )

        from louieai._client import LouieClient

        return LouieClient(
            server_url="https://louie-dev.grph.xyz", graphistry_client=graphistry_client
        )

    def test_real_arrow_dataframe_fetch(self, real_client):
        """Test fetching real dataframe via Arrow API."""
        # Create a query that should return a dataframe
        response = real_client.add_cell(
            "",
            "Create a sample dataframe with 5 rows containing user_id, score, "
            "and status columns",
        )

        # Check if we got dataframes
        if response.has_dataframes:
            df_elements = response.dataframe_elements

            # Verify at least one has a table (fetched via Arrow)
            tables = [elem.get("table") for elem in df_elements if "table" in elem]
            assert len(tables) > 0, "No dataframes were fetched via Arrow API"

            # Verify it's a pandas DataFrame
            for table in tables:
                assert isinstance(table, pd.DataFrame)
                print(f"Fetched dataframe shape: {table.shape}")
                print(f"Columns: {list(table.columns)}")
