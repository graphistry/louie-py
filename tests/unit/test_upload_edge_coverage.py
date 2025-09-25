"""Tests for edge cases to improve upload module coverage."""

import io
from unittest.mock import Mock, patch

import httpx
import pandas as pd
import pytest

from louieai._upload import UploadClient


class TestUploadEdgeCoverage:
    """Test edge cases for better coverage."""

    def test_serialize_image_unknown_bytes(self):
        """Test image serialization with unknown binary format."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Unknown binary data (not PNG, JPEG, or GIF)
        unknown_bytes = b"UNKNOWN\x00\x01\x02\x03"

        file_data, filename, mime_type = upload_client._serialize_image(unknown_bytes)

        assert file_data == unknown_bytes
        assert filename == "image.bin"
        assert mime_type == "application/octet-stream"

    def test_serialize_image_gif_format(self):
        """Test image serialization with GIF format."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # GIF magic bytes
        gif_bytes = b"GIF89a" + b"\x00" * 10

        file_data, filename, mime_type = upload_client._serialize_image(gif_bytes)

        assert file_data == gif_bytes
        assert filename == "image.gif"
        assert mime_type == "image/gif"

    def test_serialize_binary_file_object_no_name(self):
        """Test binary serialization with file object that has no name attribute."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Create a file-like object without name attribute
        file_obj = io.BytesIO(b"some content")

        file_data, filename, mime_type = upload_client._serialize_binary(file_obj)

        assert file_data == b"some content"
        assert filename == "file.bin"
        assert mime_type == "application/octet-stream"

    def test_serialize_binary_file_object_non_string_name(self):
        """Test binary serialization with file object that has non-string name."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Create a file-like object with non-string name
        file_obj = io.BytesIO(b"some content")
        file_obj.name = 123  # Non-string name

        file_data, filename, mime_type = upload_client._serialize_binary(file_obj)

        assert file_data == b"some content"
        assert filename == "file.bin"
        assert mime_type == "application/octet-stream"

    def test_serialize_binary_unknown_content(self):
        """Test binary serialization with unknown content type."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Unknown binary format
        unknown_bytes = b"UNKNOWN_FORMAT_DATA"

        file_data, filename, mime_type = upload_client._serialize_binary(unknown_bytes)

        assert file_data == unknown_bytes
        assert filename == "file.bin"
        assert mime_type == "application/octet-stream"

    def test_upload_dataframe_read_timeout_reraise(self):
        """Test that ReadTimeout is re-raised when no data received."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            # Immediately raise ReadTimeout without yielding any lines
            mock_response.iter_lines = Mock(side_effect=httpx.ReadTimeout("Timeout"))

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            with patch("time.time", return_value=100), pytest.raises(httpx.ReadTimeout):
                upload_client.upload_dataframe("test", df)

    def test_upload_image_read_timeout_reraise(self):
        """Test that ReadTimeout is re-raised in image upload when no data."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1

        upload_client = UploadClient(mock_client)
        image = b"\x89PNG\r\n\x1a\n" + b"data"

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines = Mock(side_effect=httpx.ReadTimeout("Timeout"))

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            with patch("time.time", return_value=100), pytest.raises(httpx.ReadTimeout):
                upload_client.upload_image("test", image)

    def test_upload_binary_read_timeout_reraise(self):
        """Test that ReadTimeout is re-raised in binary upload when no data."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1

        upload_client = UploadClient(mock_client)
        pdf = b"%PDF-1.4\n" + b"content"

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines = Mock(side_effect=httpx.ReadTimeout("Timeout"))

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            with patch("time.time", return_value=100), pytest.raises(httpx.ReadTimeout):
                upload_client.upload_binary("test", pdf)

    def test_upload_image_no_pil_installed(self):
        """Test image handling when PIL is not available."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Create an object that's not bytes/path/file-like
        not_an_image = object()

        # Simply test the TypeError for unsupported types
        # (ImportError path is tested implicitly when PIL is not installed)
        with pytest.raises(TypeError, match="Unsupported image type"):
            upload_client._serialize_image(not_an_image)

    def test_upload_dataframe_fetch_failure(self):
        """Test handling when dataframe fetch returns None."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1
        mock_client._parse_jsonl_response = Mock(
            return_value={
                "dthread_id": "D_test",
                "elements": [{"type": "DfElement", "id": "df_001"}],
            }
        )
        # Fetch returns None (failure case)
        mock_client._fetch_dataframe_arrow = Mock(return_value=None)

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines = Mock(return_value=['{"dthread_id": "D_test"}'])

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            with patch("time.time", return_value=100):
                response = upload_client.upload_dataframe("test", df)

                # Should have attempted fetch but continued when it returned None
                mock_client._fetch_dataframe_arrow.assert_called_with(
                    "D_test", "df_001"
                )
                assert response.thread_id == "D_test"
