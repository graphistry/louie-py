"""Unit tests for DataFrame upload functionality."""

import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from louieai._client import LouieClient, Response
from louieai._upload import UploadClient


class TestUploadClient:
    """Test the UploadClient class."""

    def test_serialize_dataframe_parquet(self):
        """Test DataFrame serialization to Parquet format."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        client = MagicMock()
        upload_client = UploadClient(client)

        data, filename, content_type = upload_client._serialize_dataframe(df, "parquet")

        assert isinstance(data, bytes)
        assert filename == "data.parquet"
        assert content_type == "application/octet-stream"
        assert len(data) > 0

    def test_serialize_dataframe_csv(self):
        """Test DataFrame serialization to CSV format."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        client = MagicMock()
        upload_client = UploadClient(client)

        data, filename, content_type = upload_client._serialize_dataframe(df, "csv")

        assert isinstance(data, bytes)
        assert filename == "data.csv"
        assert content_type == "text/csv"
        # Check CSV content
        assert b"a,b" in data  # Header
        assert b"1,4" in data  # First row

    def test_serialize_dataframe_json(self):
        """Test DataFrame serialization to JSON format."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        client = MagicMock()
        upload_client = UploadClient(client)

        data, filename, content_type = upload_client._serialize_dataframe(df, "json")

        assert isinstance(data, bytes)
        assert filename == "data.jsonl"
        assert content_type == "application/x-ndjson"
        # Check JSON content
        lines = data.decode().strip().split("\n")
        assert len(lines) == 3  # 3 rows
        first_row = json.loads(lines[0])
        assert first_row == {"a": 1, "b": 4}

    def test_serialize_dataframe_arrow(self):
        """Test DataFrame serialization to Arrow format."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        client = MagicMock()
        upload_client = UploadClient(client)

        data, filename, content_type = upload_client._serialize_dataframe(df, "arrow")

        assert isinstance(data, bytes)
        assert filename == "data.arrow"
        assert content_type == "application/octet-stream"
        assert len(data) > 0

    def test_serialize_dataframe_invalid_format(self):
        """Test that invalid format raises an error."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        client = MagicMock()
        upload_client = UploadClient(client)

        with pytest.raises(ValueError, match="Unsupported format"):
            upload_client._serialize_dataframe(df, "invalid")

    def test_get_default_parsing_options(self):
        """Test default parsing options for different formats."""
        client = MagicMock()
        upload_client = UploadClient(client)

        # CSV
        csv_opts = upload_client._get_default_parsing_options("csv")
        assert csv_opts["type"] == "CSVParsingOptions"
        assert csv_opts["header"] == "infer"
        assert csv_opts["sep"] == ","

        # JSON
        json_opts = upload_client._get_default_parsing_options("json")
        assert json_opts["type"] == "JSONParsingOptions"
        assert json_opts["lines"] is True
        assert json_opts["orient"] == "records"

        # Parquet
        parquet_opts = upload_client._get_default_parsing_options("parquet")
        assert parquet_opts["type"] == "ParquetParsingOptions"
        assert parquet_opts["use_pandas_metadata"] is True

        # Arrow
        arrow_opts = upload_client._get_default_parsing_options("arrow")
        assert arrow_opts["type"] == "ArrowParsingOptions"
        assert arrow_opts["use_threads"] is True

        # Unknown format
        unknown_opts = upload_client._get_default_parsing_options("unknown")
        assert unknown_opts is None

    @patch("louieai._upload.httpx.Client")
    def test_upload_dataframe_success(self, mock_httpx):
        """Test successful DataFrame upload."""
        # Setup mocks
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        mock_client = MagicMock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 300
        mock_client._streaming_timeout = 120
        mock_client._get_headers.return_value = {"Authorization": "Bearer test"}

        # Mock JSONL response
        jsonl_response = (
            '{"dthread_id": "thread-123"}\n'
            '{"payload": {"id": "elem-1", "type": "TextElement", '
            '"text": "Analysis complete"}}'
        )
        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "thread-123",
            "elements": [
                {"id": "elem-1", "type": "TextElement", "text": "Analysis complete"}
            ],
        }

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = jsonl_response.split("\n")
        mock_response.raise_for_status = MagicMock()

        mock_stream_client = MagicMock()
        mock_stream_client.stream.return_value.__enter__.return_value = mock_response
        mock_httpx.return_value = mock_stream_client

        # Execute upload
        upload_client = UploadClient(mock_client)
        response = upload_client.upload_dataframe(
            prompt="Analyze this data",
            df=df,
            thread_id="",
            format="parquet",
        )

        # Verify response
        assert isinstance(response, Response)
        assert response.thread_id == "thread-123"
        assert len(response.elements) == 1
        assert response.elements[0]["text"] == "Analysis complete"

        # Verify HTTP call
        mock_stream_client.stream.assert_called_once()
        call_args = mock_stream_client.stream.call_args
        assert call_args[0][0] == "POST"
        assert "/api/chat_upload/" in call_args[0][1]
        assert "data" in call_args[1]
        assert "files" in call_args[1]


class TestLouieClientUpload:
    """Test the LouieClient upload_dataframe method."""

    @patch("louieai._upload.UploadClient")
    def test_upload_dataframe_delegates_to_upload_client(self, mock_upload_class):
        """Test that upload_dataframe delegates to UploadClient."""
        # Setup
        df = pd.DataFrame({"a": [1, 2, 3]})
        mock_upload_instance = MagicMock()
        mock_upload_class.return_value = mock_upload_instance

        mock_response = MagicMock(spec=Response)
        mock_upload_instance.upload_dataframe.return_value = mock_response

        client = LouieClient()

        # Execute
        response = client.upload_dataframe("Test prompt", df, format="csv")

        # Verify
        mock_upload_class.assert_called_once_with(client)
        mock_upload_instance.upload_dataframe.assert_called_once_with(
            prompt="Test prompt",
            df=df,
            thread_id="",
            format="csv",
            agent="UploadPassthroughAgent",
            traces=False,
            share_mode="Private",
            name=None,
            parsing_options=None,
        )
        assert response == mock_response


class TestCursorUpload:
    """Test the Cursor class DataFrame upload support."""

    def test_cursor_call_with_dataframe(self):
        """Test calling cursor with DataFrame."""
        mock_client = MagicMock()
        mock_response = MagicMock(spec=Response)
        mock_response.thread_id = "thread-123"
        mock_response.elements = []
        mock_client.upload_dataframe.return_value = mock_response

        from louieai.notebook import Cursor

        cursor = Cursor(mock_client)

        df = pd.DataFrame({"a": [1, 2, 3]})
        result = cursor("Analyze this", df)

        # Verify upload_dataframe was called
        mock_client.upload_dataframe.assert_called_once()
        call_args = mock_client.upload_dataframe.call_args
        assert call_args[1]["prompt"] == "Analyze this"
        assert call_args[1]["df"].equals(df)
        assert result == cursor  # Returns self for chaining

    def test_cursor_call_dataframe_first_argument(self):
        """Test calling cursor with DataFrame as first argument."""
        mock_client = MagicMock()
        mock_response = MagicMock(spec=Response)
        mock_response.thread_id = "thread-123"
        mock_response.elements = []
        mock_client.upload_dataframe.return_value = mock_response

        from louieai.notebook import Cursor

        cursor = Cursor(mock_client)

        df = pd.DataFrame({"a": [1, 2, 3]})
        cursor(df, "Analyze this")  # Returns self, not using result

        # Verify upload_dataframe was called with swapped arguments
        mock_client.upload_dataframe.assert_called_once()
        call_args = mock_client.upload_dataframe.call_args
        assert call_args[1]["prompt"] == "Analyze this"
        assert call_args[1]["df"].equals(df)

    def test_cursor_call_without_dataframe(self):
        """Test calling cursor without DataFrame uses add_cell."""
        mock_client = MagicMock()
        mock_response = MagicMock(spec=Response)
        mock_response.thread_id = "thread-123"
        mock_response.elements = []
        mock_client.add_cell.return_value = mock_response

        from louieai.notebook import Cursor

        cursor = Cursor(mock_client)

        cursor("Just a query")  # Returns self, not using result

        # Verify add_cell was called, not upload_dataframe
        mock_client.add_cell.assert_called_once()
        mock_client.upload_dataframe.assert_not_called()
        call_args = mock_client.add_cell.call_args
        assert call_args[1]["prompt"] == "Just a query"

    def test_cursor_invalid_dataframe_argument(self):
        """Test that invalid DataFrame argument raises error."""
        mock_client = MagicMock()
        from louieai.notebook import Cursor

        cursor = Cursor(mock_client)

        df = pd.DataFrame({"a": [1, 2, 3]})

        # If first arg is DataFrame, second must be string
        with pytest.raises(ValueError, match="second must be a string prompt"):
            cursor(df, 123)  # Invalid: second arg not a string
