"""Unit tests for Arrow format parsing."""

from io import BytesIO
from unittest.mock import Mock, patch

import pandas as pd
import pyarrow as pa
import pyarrow.ipc as ipc
import pytest

from louieai._client import LouieClient


class TestArrowFormatParsing:
    """Test Arrow format parsing handles both file and stream formats."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        with patch("louieai._client.AuthManager"):
            client = LouieClient(server_url="https://test.louie.ai")
            client._client = Mock()
            return client

    def create_arrow_file_format(self, df):
        """Create Arrow data in file format."""
        table = pa.Table.from_pandas(df)
        sink = BytesIO()
        with ipc.new_file(sink, table.schema) as writer:
            writer.write_table(table)
        return sink.getvalue()

    def create_arrow_stream_format(self, df):
        """Create Arrow data in stream format."""
        table = pa.Table.from_pandas(df)
        sink = BytesIO()
        with ipc.new_stream(sink, table.schema) as writer:
            writer.write_table(table)
        return sink.getvalue()

    def test_arrow_file_format_parsing(self, client):
        """Test parsing Arrow file format (most common)."""
        # Create test data
        df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]})
        arrow_data = self.create_arrow_file_format(df)

        # Mock response
        mock_response = Mock()
        mock_response.content = arrow_data
        mock_response.raise_for_status = Mock()
        client._client.get.return_value = mock_response

        # Test fetch
        result = client._fetch_dataframe_arrow("thread_123", "block_456")

        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (3, 2)
        assert list(result.columns) == ["name", "age"]
        pd.testing.assert_frame_equal(result, df)

    def test_arrow_stream_format_parsing(self, client):
        """Test parsing Arrow stream format (fallback)."""
        # Create test data
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        arrow_data = self.create_arrow_stream_format(df)

        # Mock response
        mock_response = Mock()
        mock_response.content = arrow_data
        mock_response.raise_for_status = Mock()
        client._client.get.return_value = mock_response

        # Test fetch
        result = client._fetch_dataframe_arrow("thread_123", "block_456")

        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (3, 2)
        assert list(result.columns) == ["x", "y"]
        pd.testing.assert_frame_equal(result, df)

    def test_arrow_format_detection(self, client):
        """Test that file format is tried first, then stream format."""
        # Create data that's valid as stream but not file
        df = pd.DataFrame({"a": [1, 2, 3]})
        arrow_data = self.create_arrow_stream_format(df)

        # Mock response
        mock_response = Mock()
        mock_response.content = arrow_data
        mock_response.raise_for_status = Mock()
        client._client.get.return_value = mock_response

        # Patch the Arrow functions to track call order
        file_called = False
        stream_called = False

        original_open_stream = pa.ipc.open_stream

        def mock_open_file(data):
            nonlocal file_called
            file_called = True
            # This should fail for stream format
            raise Exception("Not file format")

        def mock_open_stream(data):
            nonlocal stream_called
            stream_called = True
            return original_open_stream(data)

        with (
            patch("pyarrow.ipc.open_file", side_effect=mock_open_file),
            patch("pyarrow.ipc.open_stream", side_effect=mock_open_stream),
        ):
            result = client._fetch_dataframe_arrow("thread_123", "block_456")

        # Verify file was tried first, then stream
        assert file_called
        assert stream_called
        assert result is not None

    def test_invalid_arrow_data(self, client):
        """Test handling of invalid Arrow data."""
        # Mock response with invalid data
        mock_response = Mock()
        mock_response.content = b"Not Arrow format data"
        mock_response.raise_for_status = Mock()
        client._client.get.return_value = mock_response

        # Should return None and warn
        with pytest.warns(RuntimeWarning, match="Failed to fetch dataframe"):
            result = client._fetch_dataframe_arrow("thread_123", "block_456")

        assert result is None

    def test_empty_arrow_data(self, client):
        """Test handling of empty Arrow data."""
        # Create empty dataframe
        df = pd.DataFrame()
        arrow_data = self.create_arrow_file_format(df)

        # Mock response
        mock_response = Mock()
        mock_response.content = arrow_data
        mock_response.raise_for_status = Mock()
        client._client.get.return_value = mock_response

        # Test fetch
        result = client._fetch_dataframe_arrow("thread_123", "block_456")

        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (0, 0)
        assert result.empty

    def test_large_arrow_data(self, client):
        """Test handling of larger Arrow datasets."""
        # Create larger dataset
        df = pd.DataFrame(
            {
                "id": range(1000),
                "value": [f"value_{i}" for i in range(1000)],
                "score": [i * 0.1 for i in range(1000)],
            }
        )
        arrow_data = self.create_arrow_file_format(df)

        # Mock response
        mock_response = Mock()
        mock_response.content = arrow_data
        mock_response.raise_for_status = Mock()
        client._client.get.return_value = mock_response

        # Test fetch
        result = client._fetch_dataframe_arrow("thread_123", "block_456")

        assert result is not None
        assert result.shape == (1000, 3)
        pd.testing.assert_frame_equal(result, df)
