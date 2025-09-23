"""Test image element support in louie-py."""

from unittest.mock import Mock


def test_base64_image_element_rendering():
    """Test rendering of Base64ImageElement."""
    from louieai.notebook.streaming import StreamingDisplay

    # Create a small test image (1x1 red pixel PNG)
    red_pixel_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAA"
        "DUlEQVR42mP8z8DwHwAFBQIAX8jx8gAAAABJRU5ErkJggg=="
    )

    display = StreamingDisplay()

    # Test Base64ImageElement
    element = {
        "type": "Base64ImageElement",
        "id": "img1",
        "src": f"data:image/png;base64,{red_pixel_base64}",
        "width": 100,
        "height": 100,
    }

    html = display._render_element(element)

    # Should render an img tag with the data URL
    assert "<img" in html
    assert f'src="data:image/png;base64,{red_pixel_base64}"' in html
    assert 'width="100"' in html or "width: 100px" in html
    assert 'height="100"' in html or "height: 100px" in html


def test_binary_element_with_url_rendering():
    """Test rendering of BinaryElement with URL."""
    from louieai.notebook.streaming import StreamingDisplay

    display = StreamingDisplay()

    # Test BinaryElement with URL (for images)
    element = {
        "type": "BinaryElement",
        "id": "bin1",
        "url": "/api/chat/thread123/binary/elem456",
        "content_type": "image/png",
        "filename": "chart.png",
        "size": 1024,
    }

    # Mock client with base URL
    mock_client = Mock()
    mock_client.base_url = "https://api.louie.ai"
    display.client = mock_client

    html = display._render_element(element)

    # Should render an img tag with the full URL
    assert "<img" in html
    assert 'src="https://api.louie.ai/api/chat/thread123/binary/elem456"' in html


def test_binary_element_non_image_rendering():
    """Test rendering of BinaryElement for non-image files."""
    from louieai.notebook.streaming import StreamingDisplay

    display = StreamingDisplay()

    # Test BinaryElement with URL (for non-image file)
    element = {
        "type": "BinaryElement",
        "id": "bin2",
        "url": "/api/chat/thread123/binary/elem789",
        "content_type": "application/pdf",
        "filename": "report.pdf",
        "size": 204800,
    }

    # Mock client with base URL
    mock_client = Mock()
    mock_client.base_url = "https://api.louie.ai"
    display.client = mock_client

    html = display._render_element(element)

    # Should render a download link
    assert "<a" in html
    assert 'href="https://api.louie.ai/api/chat/thread123/binary/elem789"' in html
    assert "download" in html
    assert "report.pdf" in html
