"""Test dataframe fetching via Arrow API."""

from io import BytesIO
from unittest.mock import Mock, patch

import pandas as pd
import pyarrow as pa
import pyarrow.ipc as ipc
import pytest

from louieai._client import LouieClient


@pytest.mark.unit
class TestDataFrameFetching:
    """Test Arrow dataframe fetching functionality."""

    @pytest.fixture
    def mock_graphistry_client(self):
        """Mock GraphistryClient instance."""
        mock = Mock()
        mock.api_token = Mock(return_value="fake-token-123")
        mock.register = Mock()
        mock.refresh = Mock()
        return mock

    @pytest.fixture
    def client(self, mock_graphistry_client):
        """Create LouieClient with mocked GraphistryClient."""
        client = LouieClient(
            server_url="https://test.louie.ai", graphistry_client=mock_graphistry_client
        )
        return client

    @pytest.fixture
    def mock_arrow_response(self):
        """Create a mock Arrow response with a simple dataframe."""
        # Create a simple dataframe
        df = pd.DataFrame(
            {
                "user_id": ["u1", "u2", "u3"],
                "score": [100, 85, 92],
                "status": ["active", "active", "pending"],
            }
        )

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

        return mock_response, df

    def test_fetch_dataframe_arrow_success(self, client, mock_arrow_response):
        """Test successful Arrow dataframe fetch."""
        mock_response, expected_df = mock_arrow_response

        with patch.object(client._client, "get", return_value=mock_response):
            # Fetch dataframe
            result_df = client._fetch_dataframe_arrow("D_test123", "df_456")

            # Verify result
            assert result_df is not None
            pd.testing.assert_frame_equal(result_df, expected_df)

            # Verify correct URL was called
            client._client.get.assert_called_once()
            call_args = client._client.get.call_args
            assert "/api/dthread/D_test123/df/block/df_456/arrow" in call_args[0][0]

    def test_fetch_dataframe_arrow_failure(self, client):
        """Test handling of Arrow fetch failures."""
        # Mock a failed response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("Server error")

        with patch.object(client._client, "get", return_value=mock_response):
            # Should return None and warn
            with pytest.warns(RuntimeWarning, match="Failed to fetch dataframe"):
                result = client._fetch_dataframe_arrow("D_test123", "df_456")

            assert result is None

    def test_add_cell_with_dataframe_fetching(self, client, mock_arrow_response):
        """Test that add_cell fetches dataframes automatically."""
        mock_arrow_response_obj, expected_df = mock_arrow_response

        # Mock streaming response with DfElement
        mock_stream_response = Mock()
        mock_stream_response.raise_for_status = Mock()
        mock_stream_response.iter_lines.return_value = iter(
            [
                '{"dthread_id": "D_test123"}',
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Analysis complete"}}',
                '{"payload": {"id": "B_002", "type": "DfElement", '
                '"df_id": "df_456", "metadata": {"shape": [3, 3]}}}',
            ]
        )

        # Mock both the streaming response and Arrow fetch
        with (
            patch("louieai._client.httpx.Client") as mock_httpx,
            patch.object(client._client, "get", return_value=mock_arrow_response_obj),
        ):
            # Setup streaming mock
            mock_stream_cm = Mock()
            mock_stream_cm.__enter__ = Mock(return_value=mock_stream_response)
            mock_stream_cm.__exit__ = Mock(return_value=None)

            # Handle both direct instantiation and context manager usage
            mock_httpx_instance = Mock()
            mock_httpx_instance.stream.return_value = mock_stream_cm
            mock_httpx_instance.__enter__ = Mock(return_value=mock_httpx_instance)
            mock_httpx_instance.__exit__ = Mock(return_value=None)
            mock_httpx.return_value = mock_httpx_instance

            # Make the call
            response = client.add_cell("", "Create a dataframe")

            # Verify response
            assert response.thread_id == "D_test123"
            assert len(response.elements) == 2

            # Check text element
            assert response.text_elements[0]["text"] == "Analysis complete"

            # Check dataframe element has the fetched table
            df_elements = response.dataframe_elements
            assert len(df_elements) == 1
            assert "table" in df_elements[0]
            pd.testing.assert_frame_equal(df_elements[0]["table"], expected_df)

            # Verify Arrow fetch was called
            client._client.get.assert_called_once()
            assert (
                "/api/dthread/D_test123/df/block/df_456/arrow"
                in client._client.get.call_args[0][0]
            )

    def test_add_cell_without_df_id(self, client):
        """Test that elements without df_id don't trigger Arrow fetch."""
        # Mock streaming response without df_id
        mock_stream_response = Mock()
        mock_stream_response.raise_for_status = Mock()
        mock_stream_response.iter_lines.return_value = iter(
            [
                '{"dthread_id": "D_test123"}',
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "No dataframe here"}}',
                '{"payload": {"id": "B_002", "type": "DfElement", '
                '"metadata": {"empty": true}}}',  # Has id but no df_id or block_id
            ]
        )

        with patch("louieai._client.httpx.Client") as mock_httpx:
            # Setup streaming mock
            mock_stream_cm = Mock()
            mock_stream_cm.__enter__ = Mock(return_value=mock_stream_response)
            mock_stream_cm.__exit__ = Mock(return_value=None)

            # Handle both direct instantiation and context manager usage
            mock_httpx_instance = Mock()
            mock_httpx_instance.stream.return_value = mock_stream_cm
            mock_httpx_instance.__enter__ = Mock(return_value=mock_httpx_instance)
            mock_httpx_instance.__exit__ = Mock(return_value=None)
            mock_httpx.return_value = mock_httpx_instance

            # Spy on _fetch_dataframe_arrow - return None to simulate failed fetch
            with patch.object(
                client, "_fetch_dataframe_arrow", return_value=None
            ) as mock_fetch:
                response = client.add_cell("", "Test query")

                # Should have tried to fetch but got None
                mock_fetch.assert_called_once_with("D_test123", "B_002")

                # DfElement should still be in response but without table
                df_elements = response.dataframe_elements
                assert len(df_elements) == 1
                assert "table" not in df_elements[0]
