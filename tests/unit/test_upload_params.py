"""Tests for upload method optional parameters."""

import json
from unittest.mock import Mock, patch

import pandas as pd

from louieai._upload import UploadClient


class TestUploadOptionalParams:
    """Test optional parameters in upload methods."""

    def test_upload_dataframe_with_name(self):
        """Test upload with custom name parameter."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1
        mock_client._parse_jsonl_response = Mock(
            return_value={"dthread_id": "D_123", "elements": []}
        )

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines = Mock(return_value=['{"dthread_id": "D_123"}'])

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            # Call with name parameter
            response = upload_client.upload_dataframe(
                "test query", df, name="My Analysis"
            )

            # Verify name was included in the request
            call_args = mock_stream_client.stream.call_args
            assert call_args[1]["data"]["name"] == "My Analysis"
            assert response.thread_id == "D_123"

    def test_upload_dataframe_with_parsing_options(self):
        """Test upload with custom parsing options."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1
        mock_client._parse_jsonl_response = Mock(
            return_value={"dthread_id": "D_456", "elements": []}
        )

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines = Mock(return_value=['{"dthread_id": "D_456"}'])

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            # Call with parsing options
            parsing_opts = {"delimiter": ";", "header": True}
            upload_client.upload_dataframe(
                "test", df, format="csv", parsing_options=parsing_opts
            )

            # Verify parsing options were included
            call_args = mock_stream_client.stream.call_args
            assert "parsing_options" in call_args[1]["data"]
            parsed_opts = json.loads(call_args[1]["data"]["parsing_options"])
            assert parsed_opts[0] == parsing_opts

    def test_upload_image_with_name_and_thread(self):
        """Test image upload with name parameter."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1
        mock_client._parse_jsonl_response = Mock(
            return_value={"dthread_id": "D_789", "elements": []}
        )

        upload_client = UploadClient(mock_client)
        image_data = b"\x89PNG\r\n\x1a\n" + b"test_image"

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines = Mock(return_value=['{"dthread_id": "D_789"}'])

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            # Call with name and thread_id
            upload_client.upload_image(
                "What's this?", image_data, thread_id="T_123", name="Image Analysis"
            )

            # Verify both were included
            call_args = mock_stream_client.stream.call_args
            assert call_args[1]["data"]["name"] == "Image Analysis"
            assert call_args[1]["data"]["dthread_id"] == "T_123"

    def test_upload_binary_with_name(self):
        """Test binary upload with name parameter."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1
        mock_client._parse_jsonl_response = Mock(
            return_value={"dthread_id": "D_999", "elements": []}
        )

        upload_client = UploadClient(mock_client)
        pdf_data = b"%PDF-1.4\n" + b"test_pdf"

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines = Mock(return_value=['{"dthread_id": "D_999"}'])

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            # Call with name
            upload_client.upload_binary("Summarize", pdf_data, name="Document Summary")

            # Verify name was included
            call_args = mock_stream_client.stream.call_args
            assert call_args[1]["data"]["name"] == "Document Summary"

    def test_serialize_binary_mime_type_fallback(self):
        """Test binary serialization when mime type can't be determined."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Create a mock Path with unknown extension
        from pathlib import Path

        test_file = Path("/tmp/test.unknown_ext")

        # Write some content
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_file", return_value=True),
            patch("builtins.open", create=True) as mock_open,
            patch("mimetypes.guess_type", return_value=(None, None)),
        ):
            mock_open.return_value.__enter__.return_value.read.return_value = (
                b"unknown content"
            )
            _, filename, content_type = upload_client._serialize_binary(test_file)

            # Should fallback to application/octet-stream
            assert filename == "test.unknown_ext"
            assert content_type == "application/octet-stream"

    def test_serialize_binary_json_detection(self):
        """Test JSON detection in binary serialization."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # JSON bytes without proper extension
        json_bytes = b'{"key": "value", "data": [1, 2, 3]}'

        _, filename, content_type = upload_client._serialize_binary(json_bytes)

        # Should detect as JSON
        assert filename == "data.json"
        assert content_type == "application/json"

    def test_share_mode_parameter(self):
        """Test share_mode parameter handling."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1
        mock_client._parse_jsonl_response = Mock(
            return_value={"dthread_id": "D_share", "elements": []}
        )

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines = Mock(return_value=['{"dthread_id": "D_share"}'])

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            # Test different share modes
            for share_mode in ["Private", "Organization", "Public"]:
                upload_client.upload_dataframe("test", df, share_mode=share_mode)

                # Verify share_mode was included
                call_args = mock_stream_client.stream.call_args
                assert call_args[1]["data"]["share_mode"] == share_mode
