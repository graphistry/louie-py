"""Tests for image and binary file upload functionality."""

import io
from unittest.mock import Mock, patch

import pytest

from louieai._client import LouieClient, Response
from louieai._upload import UploadClient


def mock_open_binary(data):
    """Helper to mock open() with binary data."""

    def mock_open(*args, **kwargs):
        m = Mock()
        m.read.return_value = data
        m.__enter__ = Mock(return_value=m)
        m.__exit__ = Mock(return_value=None)
        return m

    return mock_open


def mock_streaming_response(response_lines):
    """Helper to create a mock streaming response context."""
    mock_client_instance = Mock()
    mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
    mock_client_instance.__exit__ = Mock(return_value=None)

    mock_response = Mock()
    mock_response.iter_lines.return_value = iter(response_lines)
    mock_response.raise_for_status = Mock()
    mock_stream_context = Mock()
    mock_stream_context.__enter__ = Mock(return_value=mock_response)
    mock_stream_context.__exit__ = Mock(return_value=None)
    mock_client_instance.stream.return_value = mock_stream_context

    return mock_client_instance


class TestImageUpload:
    """Test image upload functionality."""

    def test_upload_image_from_file_path(self):
        """Test uploading image from file path."""
        # Mock client
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30
        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "test-thread-123",
            "elements": [
                {"type": "TextElement", "content": "This is an image of a sunset."}
            ],
        }

        upload_client = UploadClient(mock_client)

        # Mock file operations
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch(
                "builtins.open",
                mock_open_binary(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"),
            ),
            patch("mimetypes.guess_type", return_value=("image/png", None)),
            patch("httpx.Client") as mock_httpx,
        ):
            # Setup mock streaming response
            mock_httpx.return_value = mock_streaming_response(
                ['{"type": "TextElement", "content": "This is an image"}']
            )

            result = upload_client.upload_image("What's in this image?", "test.png")

            # Verify result
            assert isinstance(result, Response)
            assert result.thread_id == "test-thread-123"

    def test_upload_image_from_bytes(self):
        """Test uploading image from bytes."""
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30
        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "test-thread-456",
            "elements": [{"type": "TextElement", "content": "JPEG image analyzed"}],
        }

        upload_client = UploadClient(mock_client)

        with patch("httpx.Client") as mock_httpx:
            mock_httpx.return_value = mock_streaming_response(
                ['{"type": "TextElement", "content": "JPEG image"}']
            )

            # Test with JPEG bytes
            jpeg_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF"
            result = upload_client.upload_image("Analyze this image", jpeg_bytes)

            assert isinstance(result, Response)
            assert result.thread_id == "test-thread-456"

    def test_image_format_detection(self):
        """Test image format detection from bytes."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Test PNG detection
        png_bytes = b"\x89PNG\r\n\x1a\n"
        _file_data, filename, content_type = upload_client._serialize_image(png_bytes)
        assert filename == "image.png"
        assert content_type == "image/png"

        # Test JPEG detection
        jpeg_bytes = b"\xff\xd8\xff\xe0"
        _file_data, filename, content_type = upload_client._serialize_image(jpeg_bytes)
        assert filename == "image.jpg"
        assert content_type == "image/jpeg"

    def test_upload_image_error_handling(self):
        """Test error handling for invalid image inputs."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Test file not found
        with (
            patch("pathlib.Path.exists", return_value=False),
            pytest.raises(FileNotFoundError),
        ):
            upload_client._serialize_image("nonexistent.png")

        # Test invalid type
        with pytest.raises(TypeError):
            upload_client._serialize_image(123)


class TestBinaryUpload:
    """Test binary file upload functionality."""

    def test_upload_binary_pdf(self):
        """Test uploading PDF file."""
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30
        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "test-thread-789",
            "elements": [{"type": "TextElement", "content": "PDF analyzed"}],
        }

        upload_client = UploadClient(mock_client)

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch(
                "builtins.open",
                mock_open_binary(b"%PDF-1.4\nfake content"),
            ),
            patch("mimetypes.guess_type", return_value=("application/pdf", None)),
            patch("httpx.Client") as mock_httpx,
        ):
            mock_httpx.return_value = mock_streaming_response(
                ['{"type": "TextElement", "content": "PDF processed"}']
            )

            result = upload_client.upload_binary("Summarize this document", "test.pdf")

            assert isinstance(result, Response)
            assert result.thread_id == "test-thread-789"

    def test_binary_format_detection(self):
        """Test binary file format detection."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Test PDF detection
        pdf_bytes = b"%PDF-1.4\nsome content"
        _file_data, filename, content_type = upload_client._serialize_binary(pdf_bytes)
        assert filename == "document.pdf"
        assert content_type == "application/pdf"

        # Test Excel detection - need xl/ pattern in first 1000 bytes
        xl_pattern = b"xl/workbook.xml" + b"\x00" * 980
        excel_bytes = b"PK\x03\x04" + xl_pattern
        _file_data, filename, content_type = upload_client._serialize_binary(
            excel_bytes
        )
        assert filename == "spreadsheet.xlsx"
        assert "spreadsheet" in content_type

    def test_upload_binary_file_like_object(self):
        """Test uploading from file-like object."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Create BytesIO with PDF data
        pdf_data = io.BytesIO(b"%PDF-1.4\nfake content")
        pdf_data.name = "test.pdf"

        _file_data, filename, content_type = upload_client._serialize_binary(pdf_data)
        assert filename == "test.pdf"
        assert content_type == "application/pdf"

    def test_upload_binary_error_handling(self):
        """Test error handling for invalid binary inputs."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Test file not found
        with (
            patch("pathlib.Path.exists", return_value=False),
            pytest.raises(FileNotFoundError),
        ):
            upload_client._serialize_binary("nonexistent.pdf")

        # Test invalid type
        with pytest.raises(TypeError):
            upload_client._serialize_binary(123)


class TestLouieClientIntegration:
    """Test LouieClient integration with upload methods."""

    def test_client_upload_image_method(self):
        """Test LouieClient.upload_image method."""
        with patch("louieai._upload.UploadClient") as mock_upload_class:
            mock_upload_instance = Mock()
            mock_response = Response("test-thread", [])
            mock_upload_instance.upload_image.return_value = mock_response
            mock_upload_class.return_value = mock_upload_instance

            client = LouieClient(server_url="https://test.louie.ai")
            result = client.upload_image("Test prompt", "image.jpg")

            mock_upload_class.assert_called_once_with(client)
            mock_upload_instance.upload_image.assert_called_once()
            assert result == mock_response

    def test_client_upload_binary_method(self):
        """Test LouieClient.upload_binary method."""
        with patch("louieai._upload.UploadClient") as mock_upload_class:
            mock_upload_instance = Mock()
            mock_response = Response("test-thread", [])
            mock_upload_instance.upload_binary.return_value = mock_response
            mock_upload_class.return_value = mock_upload_instance

            client = LouieClient(server_url="https://test.louie.ai")
            result = client.upload_binary("Test prompt", "document.pdf")

            mock_upload_class.assert_called_once_with(client)
            mock_upload_instance.upload_binary.assert_called_once()
            assert result == mock_response
