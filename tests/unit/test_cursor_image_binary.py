"""Tests for Cursor image and binary file integration."""

import io
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from louieai._client import Response
from louieai.notebook.cursor import Cursor


class TestCursorImageHandling:
    """Test Cursor handling of image inputs."""

    def test_cursor_image_detection(self):
        """Test image input detection methods."""
        mock_client = Mock()
        cursor = Cursor(client=mock_client)

        # Test file path detection
        assert cursor._is_image_input("photo.jpg")
        assert cursor._is_image_input("chart.PNG")
        assert not cursor._is_image_input("document.pdf")

        # Test bytes detection
        png_bytes = b"\x89PNG\r\n\x1a\n"
        jpeg_bytes = b"\xff\xd8\xff\xe0"
        pdf_bytes = b"%PDF-1.4\n"

        assert cursor._is_image_input(png_bytes)
        assert cursor._is_image_input(jpeg_bytes)
        assert not cursor._is_image_input(pdf_bytes)

        # Test PIL Image detection (skip since PIL is optional and complex to mock)
        # PIL.Image detection is tested implicitly in integration tests

        # Test None and invalid types
        assert not cursor._is_image_input(None)
        assert not cursor._is_image_input(123)

    def test_cursor_binary_file_detection(self):
        """Test binary file input detection methods."""
        mock_client = Mock()
        cursor = Cursor(client=mock_client)

        # Test file path detection
        assert cursor._is_binary_file_input("document.pdf")
        assert cursor._is_binary_file_input("spreadsheet.xlsx")
        assert not cursor._is_binary_file_input("photo.jpg")

        # Test bytes detection
        pdf_bytes = b"%PDF-1.4\n"
        excel_bytes = b"PK\x03\x04"
        json_bytes = b'{"key": "value"}'
        png_bytes = b"\x89PNG\r\n\x1a\n"

        assert cursor._is_binary_file_input(pdf_bytes)
        assert cursor._is_binary_file_input(excel_bytes)
        assert cursor._is_binary_file_input(json_bytes)
        assert not cursor._is_binary_file_input(png_bytes)

        # Test None and invalid types
        assert not cursor._is_binary_file_input(None)
        assert not cursor._is_binary_file_input(123)

    def test_cursor_call_image_first_arg_no_prompt(self):
        """Test lui(image) pattern."""
        mock_client = Mock()
        mock_response = Response(
            "test-thread",
            [{"type": "TextElement", "content": "This image shows a sunset"}],
        )
        mock_client.upload_image.return_value = mock_response

        cursor = Cursor(client=mock_client)

        with (
            patch.object(cursor, "_is_image_input", return_value=True),
            patch.object(cursor, "_is_binary_file_input", return_value=False),
            patch.object(cursor, "_in_jupyter", return_value=False),
        ):
            result = cursor("photo.jpg")

            # Should return cursor itself
            assert result is cursor

            # Should call upload_image with default prompt
            mock_client.upload_image.assert_called_once()
            call_args = mock_client.upload_image.call_args
            assert call_args[1]["prompt"] == "Analyze this image"
            assert call_args[1]["image"] == "photo.jpg"

    def test_cursor_call_image_with_prompt(self):
        """Test lui("prompt", image) pattern."""
        mock_client = Mock()
        mock_response = Response(
            "test-thread",
            [{"type": "TextElement", "content": "The chart shows sales data"}],
        )
        mock_client.upload_image.return_value = mock_response

        cursor = Cursor(client=mock_client)

        with (
            patch.object(cursor, "_is_image_input") as mock_is_image,
            patch.object(cursor, "_is_binary_file_input", return_value=False),
            patch.object(cursor, "_in_jupyter", return_value=False),
        ):
            # Second argument is image
            mock_is_image.side_effect = lambda x: x == "chart.png"

            result = cursor("Explain this chart", "chart.png")

            assert result is cursor
            mock_client.upload_image.assert_called_once()
            call_args = mock_client.upload_image.call_args
            assert call_args[1]["prompt"] == "Explain this chart"
            assert call_args[1]["image"] == "chart.png"

    def test_cursor_call_image_first_with_prompt(self):
        """Test lui(image, "prompt") pattern."""
        mock_client = Mock()
        mock_response = Response(
            "test-thread",
            [{"type": "TextElement", "content": "Detected objects in image"}],
        )
        mock_client.upload_image.return_value = mock_response

        cursor = Cursor(client=mock_client)

        with (
            patch.object(cursor, "_is_image_input") as mock_is_image,
            patch.object(cursor, "_is_binary_file_input", return_value=False),
            patch.object(cursor, "_in_jupyter", return_value=False),
        ):
            # First argument is image
            mock_is_image.side_effect = lambda x: x == "photo.jpg"

            result = cursor("photo.jpg", "What objects are in this image?")

            assert result is cursor
            mock_client.upload_image.assert_called_once()
            call_args = mock_client.upload_image.call_args
            assert call_args[1]["prompt"] == "What objects are in this image?"
            assert call_args[1]["image"] == "photo.jpg"


class TestCursorBinaryHandling:
    """Test Cursor handling of binary file inputs."""

    def test_cursor_call_binary_first_arg_no_prompt(self):
        """Test lui(binary_file) pattern."""
        mock_client = Mock()
        mock_response = Response(
            "test-thread", [{"type": "TextElement", "content": "PDF document analyzed"}]
        )
        mock_client.upload_binary.return_value = mock_response

        cursor = Cursor(client=mock_client)

        with (
            patch.object(cursor, "_is_image_input", return_value=False),
            patch.object(cursor, "_is_binary_file_input", return_value=True),
            patch.object(cursor, "_in_jupyter", return_value=False),
        ):
            result = cursor("document.pdf")

            # Should return cursor itself
            assert result is cursor

            # Should call upload_binary with default prompt
            mock_client.upload_binary.assert_called_once()
            call_args = mock_client.upload_binary.call_args
            assert call_args[1]["prompt"] == "Analyze this file"
            assert call_args[1]["file"] == "document.pdf"

    def test_cursor_call_binary_with_prompt(self):
        """Test lui("prompt", binary_file) pattern."""
        mock_client = Mock()
        mock_response = Response(
            "test-thread", [{"type": "TextElement", "content": "Excel data summarized"}]
        )
        mock_client.upload_binary.return_value = mock_response

        cursor = Cursor(client=mock_client)

        with (
            patch.object(cursor, "_is_image_input", return_value=False),
            patch.object(cursor, "_is_binary_file_input") as mock_is_binary,
            patch.object(cursor, "_in_jupyter", return_value=False),
        ):
            # Second argument is binary file
            mock_is_binary.side_effect = lambda x: x == "data.xlsx"

            result = cursor("Extract key metrics", "data.xlsx")

            assert result is cursor
            mock_client.upload_binary.assert_called_once()
            call_args = mock_client.upload_binary.call_args
            assert call_args[1]["prompt"] == "Extract key metrics"
            assert call_args[1]["file"] == "data.xlsx"

    def test_cursor_call_binary_first_with_prompt(self):
        """Test lui(binary_file, "prompt") pattern."""
        mock_client = Mock()
        mock_response = Response(
            "test-thread", [{"type": "TextElement", "content": "Report summarized"}]
        )
        mock_client.upload_binary.return_value = mock_response

        cursor = Cursor(client=mock_client)

        with (
            patch.object(cursor, "_is_image_input", return_value=False),
            patch.object(cursor, "_is_binary_file_input") as mock_is_binary,
            patch.object(cursor, "_in_jupyter", return_value=False),
        ):
            # First argument is binary file
            mock_is_binary.side_effect = lambda x: x == "report.pdf"

            result = cursor("report.pdf", "Summarize the key findings")

            assert result is cursor
            mock_client.upload_binary.assert_called_once()
            call_args = mock_client.upload_binary.call_args
            assert call_args[1]["prompt"] == "Summarize the key findings"
            assert call_args[1]["file"] == "report.pdf"


class TestCursorMixedInputs:
    """Test Cursor handling of mixed input scenarios."""

    def test_cursor_dataframe_still_works(self):
        """Test that DataFrame upload still works after image/binary support."""
        mock_client = Mock()
        mock_response = Response(
            "test-thread", [{"type": "TextElement", "content": "DataFrame analyzed"}]
        )
        mock_client.upload_dataframe.return_value = mock_response

        cursor = Cursor(client=mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with (
            patch.object(cursor, "_is_image_input", return_value=False),
            patch.object(cursor, "_is_binary_file_input", return_value=False),
            patch.object(cursor, "_in_jupyter", return_value=False),
        ):
            result = cursor("Analyze this data", df)

            assert result is cursor
            mock_client.upload_dataframe.assert_called_once()
            call_args = mock_client.upload_dataframe.call_args
            assert call_args[1]["prompt"] == "Analyze this data"
            assert call_args[1]["df"] is df

    def test_cursor_error_invalid_combinations(self):
        """Test error handling for invalid argument combinations."""
        mock_client = Mock()
        cursor = Cursor(client=mock_client)

        with (
            patch.object(cursor, "_is_image_input") as mock_is_image,
            patch.object(cursor, "_is_binary_file_input", return_value=False),
        ):
            # Image with non-string second argument
            mock_is_image.side_effect = lambda x: x == "photo.jpg"

            with pytest.raises(ValueError, match="When first argument is image"):
                cursor("photo.jpg", 123)

    def test_cursor_error_unsupported_types(self):
        """Test error handling for unsupported argument types."""
        mock_client = Mock()
        cursor = Cursor(client=mock_client)

        with (
            patch.object(cursor, "_is_image_input", return_value=False),
            patch.object(cursor, "_is_binary_file_input", return_value=False),
        ):
            # Invalid first argument type
            with pytest.raises(ValueError, match="Unsupported first argument type"):
                cursor(123)

            # Invalid second argument type
            with pytest.raises(ValueError, match="Unsupported second argument type"):
                cursor("prompt", 123)

    def test_cursor_agent_selection(self):
        """Test correct agent selection for different input types."""
        mock_client = Mock()
        mock_response = Response("test-thread", [])
        mock_client.upload_image.return_value = mock_response
        mock_client.upload_binary.return_value = mock_response
        mock_client.add_cell.return_value = mock_response

        cursor = Cursor(client=mock_client)

        with patch.object(cursor, "_in_jupyter", return_value=False):
            # Image upload should use UploadPassthroughAgent
            with (
                patch.object(cursor, "_is_image_input", return_value=True),
                patch.object(cursor, "_is_binary_file_input", return_value=False),
            ):
                cursor("photo.jpg")
                call_args = mock_client.upload_image.call_args
                assert call_args[1]["agent"] == "UploadPassthroughAgent"

            # Binary upload should use UploadPassthroughAgent
            with (
                patch.object(cursor, "_is_image_input", return_value=False),
                patch.object(cursor, "_is_binary_file_input", return_value=True),
            ):
                cursor("document.pdf")
                call_args = mock_client.upload_binary.call_args
                assert call_args[1]["agent"] == "UploadPassthroughAgent"

            # Text-only query should use LouieAgent
            with (
                patch.object(cursor, "_is_image_input", return_value=False),
                patch.object(cursor, "_is_binary_file_input", return_value=False),
            ):
                cursor("What is AI?")
                call_args = mock_client.add_cell.call_args
                assert call_args[1]["agent"] == "LouieAgent"


class TestCursorFilelikeObjects:
    """Test Cursor with file-like objects."""

    def test_cursor_with_bytesio_image(self):
        """Test Cursor with BytesIO image object."""
        mock_client = Mock()
        mock_response = Response(
            "test-thread", [{"type": "TextElement", "content": "Image processed"}]
        )
        mock_client.upload_image.return_value = mock_response

        cursor = Cursor(client=mock_client)

        # Create BytesIO with PNG data
        img_data = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"fake_png_data")
        img_data.name = "test.png"

        with (
            patch.object(cursor, "_is_image_input") as mock_is_image,
            patch.object(cursor, "_is_binary_file_input", return_value=False),
            patch.object(cursor, "_in_jupyter", return_value=False),
        ):
            # Only the img_data should be detected as image
            mock_is_image.side_effect = lambda x: x is img_data

            result = cursor("Analyze this image", img_data)

            assert result is cursor
            mock_client.upload_image.assert_called_once()
            call_args = mock_client.upload_image.call_args
            assert call_args[1]["image"] is img_data

    def test_cursor_with_bytesio_binary(self):
        """Test Cursor with BytesIO binary file object."""
        mock_client = Mock()
        mock_response = Response(
            "test-thread", [{"type": "TextElement", "content": "PDF processed"}]
        )
        mock_client.upload_binary.return_value = mock_response

        cursor = Cursor(client=mock_client)

        # Create BytesIO with PDF data
        pdf_data = io.BytesIO(b"%PDF-1.4\nfake_pdf_content")
        pdf_data.name = "document.pdf"

        with (
            patch.object(cursor, "_is_image_input", return_value=False),
            patch.object(cursor, "_is_binary_file_input") as mock_is_binary,
            patch.object(cursor, "_in_jupyter", return_value=False),
        ):
            # Only the pdf_data should be detected as binary file
            mock_is_binary.side_effect = lambda x: x is pdf_data

            result = cursor("Summarize this document", pdf_data)

            assert result is cursor
            mock_client.upload_binary.assert_called_once()
            call_args = mock_client.upload_binary.call_args
            assert call_args[1]["file"] is pdf_data
