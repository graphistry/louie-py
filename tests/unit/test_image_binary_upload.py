"""Tests for image and binary file upload functionality."""

import io
from unittest.mock import Mock, patch

import pytest

from louieai._client import LouieClient, Response
from louieai._upload import UploadClient


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
            # Mock streaming response
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines.return_value = [
                '{"type": "TextElement", "content": "This is an image"}'
            ]

            mock_stream_client = Mock()
            mock_stream_client.stream.return_value.__enter__.return_value = (
                mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock()
            mock_stream_client.__enter__.return_value = mock_stream_client
            mock_stream_client.__exit__ = Mock()

            mock_httpx.return_value = mock_stream_client

            response = upload_client.upload_image("What's in this image?", "test.png")

            assert isinstance(response, Response)
            assert response.thread_id == "test-thread-123"

    def test_upload_image_from_bytes(self):
        """Test uploading image from bytes."""
        # Mock client
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30
        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "test-thread-123",
            "elements": [{"type": "TextElement", "content": "JPEG image detected."}],
        }

        upload_client = UploadClient(mock_client)

        # JPEG magic bytes
        jpeg_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF"

        with patch("httpx.Client") as mock_httpx:
            # Mock streaming response
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines.return_value = [
                '{"type": "TextElement", "content": "JPEG image"}'
            ]

            mock_stream_client = Mock()
            mock_stream_client.stream.return_value.__enter__.return_value = (
                mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock()
            mock_stream_client.__enter__.return_value = mock_stream_client
            mock_stream_client.__exit__ = Mock()

            mock_httpx.return_value = mock_stream_client

            response = upload_client.upload_image("Describe this image", jpeg_bytes)

            assert isinstance(response, Response)
            assert response.thread_id == "test-thread-123"

    def test_upload_image_pil_support(self):
        """Test uploading PIL Image object."""
        # Mock client
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30
        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "test-thread-123",
            "elements": [{"type": "TextElement", "content": "PIL image processed."}],
        }

        upload_client = UploadClient(mock_client)

        # Mock PIL Image
        with patch("louieai._upload.Image", create=True) as mock_pil:
            mock_image = Mock()
            mock_image.format = "PNG"
            mock_image.save = Mock()
            mock_pil.Image = type(mock_image)

            with patch("httpx.Client") as mock_httpx:
                # Mock streaming response
                mock_response = Mock()
                mock_response.raise_for_status = Mock()
                mock_response.iter_lines.return_value = [
                    '{"type": "TextElement", "content": "PIL image"}'
                ]

                mock_stream_context = Mock()
                mock_stream_context.__enter__.return_value = mock_response
                mock_stream_context.__exit__ = Mock()

                mock_stream_client = Mock()
                mock_stream_client.stream.return_value = mock_stream_context
                mock_stream_client.__enter__.return_value = mock_stream_client
                mock_stream_client.__exit__ = Mock()

                mock_httpx.return_value = mock_stream_client

                response = upload_client.upload_image("Analyze this", mock_image)

                assert isinstance(response, Response)
                assert response.thread_id == "test-thread-123"

    def test_image_format_detection(self):
        """Test image format detection from bytes."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Test PNG
        png_bytes = b"\x89PNG\r\n\x1a\n"
        data, filename, content_type = upload_client._serialize_image(png_bytes)
        assert filename == "image.png"
        assert content_type == "image/png"

        # Test JPEG
        jpeg_bytes = b"\xff\xd8\xff\xe0"
        data, filename, content_type = upload_client._serialize_image(jpeg_bytes)
        assert filename == "image.jpg"
        assert content_type == "image/jpeg"

        # Test GIF
        gif_bytes = b"GIF89a"
        data, filename, content_type = upload_client._serialize_image(gif_bytes)
        assert filename == "image.gif"
        assert content_type == "image/gif"

    def test_upload_image_error_handling(self):
        """Test error handling for invalid image inputs."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Test invalid type
        with pytest.raises(TypeError, match="Unsupported image type"):
            upload_client._serialize_image(123)

        # Test non-existent file
        with pytest.raises(FileNotFoundError):
            upload_client._serialize_image("nonexistent.png")


class TestBinaryUpload:
    """Test binary file upload functionality."""

    def test_upload_binary_pdf(self):
        """Test uploading PDF file."""
        # Mock client
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30
        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "test-thread-123",
            "elements": [
                {"type": "TextElement", "content": "PDF document summarized."}
            ],
        }

        upload_client = UploadClient(mock_client)

        # Mock file operations
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", mock_open_binary(b"%PDF-1.4\n")),
            patch("mimetypes.guess_type", return_value=("application/pdf", None)),
            patch("httpx.Client") as mock_httpx,
        ):
            # Mock streaming response
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines.return_value = [
                '{"type": "TextElement", "content": "PDF processed"}'
            ]

            mock_stream_client = Mock()
            mock_stream_client.stream.return_value.__enter__.return_value = (
                mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock()
            mock_stream_client.__enter__.return_value = mock_stream_client
            mock_stream_client.__exit__ = Mock()

            mock_httpx.return_value = mock_stream_client

            response = upload_client.upload_binary("Summarize this PDF", "test.pdf")

            assert isinstance(response, Response)
            assert response.thread_id == "test-thread-123"

    def test_upload_binary_excel(self):
        """Test uploading Excel file from bytes."""
        # Mock client
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30
        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "test-thread-123",
            "elements": [{"type": "TextElement", "content": "Excel data extracted."}],
        }

        upload_client = UploadClient(mock_client)

        # Excel magic bytes (ZIP format with xl/ content)
        excel_bytes = b"PK\x03\x04" + b"\x00" * 100 + b"xl/workbook.xml"

        with patch("httpx.Client") as mock_httpx:
            # Mock streaming response
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines.return_value = [
                '{"type": "TextElement", "content": "Excel processed"}'
            ]

            mock_stream_client = Mock()
            mock_stream_client.stream.return_value.__enter__.return_value = (
                mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock()
            mock_stream_client.__enter__.return_value = mock_stream_client
            mock_stream_client.__exit__ = Mock()

            mock_httpx.return_value = mock_stream_client

            response = upload_client.upload_binary(
                "Extract data from spreadsheet", excel_bytes, filename="data.xlsx"
            )

            assert isinstance(response, Response)
            assert response.thread_id == "test-thread-123"

    def test_binary_format_detection(self):
        """Test binary file format detection."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Test PDF
        pdf_bytes = b"%PDF-1.4\nSome PDF content"
        data, filename, content_type = upload_client._serialize_binary(
            pdf_bytes, "test.pdf"
        )
        assert filename == "test.pdf"
        assert content_type == "application/pdf"

        # Test Excel (ZIP with xl/ content)
        excel_bytes = b"PK\x03\x04" + b"\x00" * 100 + b"xl/workbook.xml" + b"\x00" * 800
        data, filename, content_type = upload_client._serialize_binary(excel_bytes)
        assert filename == "spreadsheet.xlsx"
        assert (
            content_type
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Test Word document
        word_bytes = b"PK\x03\x04" + b"\x00" * 100 + b"word/document.xml"
        data, filename, content_type = upload_client._serialize_binary(word_bytes)
        assert filename == "document.docx"
        assert (
            content_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        # Test JSON
        json_bytes = b'{"key": "value"}'
        data, filename, content_type = upload_client._serialize_binary(json_bytes)
        assert filename == "data.json"
        assert content_type == "application/json"

    def test_upload_binary_file_like_object(self):
        """Test uploading from file-like object."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Create BytesIO object
        file_content = b"%PDF-1.4\nPDF content here"
        file_obj = io.BytesIO(file_content)
        file_obj.name = "report.pdf"

        data, filename, content_type = upload_client._serialize_binary(file_obj)

        assert data == file_content
        assert filename == "report.pdf"
        assert content_type == "application/pdf"
        # Check that file pointer was reset
        assert file_obj.tell() == 0

    def test_upload_binary_error_handling(self):
        """Test error handling for invalid binary inputs."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Test invalid type
        with pytest.raises(TypeError, match="Unsupported file type"):
            upload_client._serialize_binary(123)

        # Test non-existent file
        with pytest.raises(FileNotFoundError):
            upload_client._serialize_binary("nonexistent.pdf")


class TestLouieClientIntegration:
    """Test integration with LouieClient."""

    def test_client_upload_image_method(self):
        """Test LouieClient.upload_image method."""
        mock_client = LouieClient(server_url="https://test.louie.ai")
        mock_client._get_headers = Mock(return_value={"Authorization": "Bearer token"})

        with patch("louieai._upload.UploadClient") as mock_upload_class:
            mock_upload_instance = Mock()
            mock_upload_instance.upload_image.return_value = Response("test-thread", [])
            mock_upload_class.return_value = mock_upload_instance

            response = mock_client.upload_image("Analyze", "test.jpg")

            mock_upload_class.assert_called_once_with(mock_client)
            mock_upload_instance.upload_image.assert_called_once_with(
                prompt="Analyze",
                image="test.jpg",
                thread_id="",
                agent="UploadPassthroughAgent",
                traces=False,
                share_mode="Private",
                name=None,
            )
            assert isinstance(response, Response)

    def test_client_upload_binary_method(self):
        """Test LouieClient.upload_binary method."""
        mock_client = LouieClient(server_url="https://test.louie.ai")
        mock_client._get_headers = Mock(return_value={"Authorization": "Bearer token"})

        with patch("louieai._upload.UploadClient") as mock_upload_class:
            mock_upload_instance = Mock()
            mock_upload_instance.upload_binary.return_value = Response(
                "test-thread", []
            )
            mock_upload_class.return_value = mock_upload_instance

            response = mock_client.upload_binary("Summarize", "test.pdf")

            mock_upload_class.assert_called_once_with(mock_client)
            mock_upload_instance.upload_binary.assert_called_once_with(
                prompt="Summarize",
                file="test.pdf",
                thread_id="",
                agent="UploadPassthroughAgent",
                traces=False,
                share_mode="Private",
                name=None,
                filename=None,
            )
            assert isinstance(response, Response)


def mock_open_binary(content):
    """Create mock for binary file reading."""

    def mock_open_func(*args, **kwargs):
        mock_file = Mock()
        if "rb" in args[1]:
            mock_file.read.return_value = content
        else:
            mock_file.read.return_value = content.decode()
        return mock_file

    return mock_open_func
