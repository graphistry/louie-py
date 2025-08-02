"""Test inline dataframe display in HTML output."""

import pandas as pd

from louieai._client import Response
from louieai.notebook.cursor import _render_response_html


def test_render_response_html_with_dataframe():
    """Test that _render_response_html displays dataframes inline."""
    # Create a test dataframe
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    
    # Create response with dataframe element
    response = Response(
        thread_id="test",
        elements=[
            {"type": "TextElement", "text": "Here is your data:"},
            {"type": "df", "id": "df_123", "table": df},
        ],
    )
    
    # Render HTML
    html = _render_response_html(response)
    
    # Verify dataframe HTML is included
    assert "<table" in html  # DataFrames render as HTML tables
    assert "<tr>" in html
    assert "<td>" in html
    # Check for actual data values
    assert "1" in html
    assert "2" in html
    assert "3" in html
    assert "4" in html
    assert "5" in html
    assert "6" in html


def test_render_response_html_without_table():
    """Test that dataframes without table data show placeholder."""
    # Create response with dataframe element but no table
    response = Response(
        thread_id="test",
        elements=[
            {"type": "df", "id": "df_123", "metadata": {"shape": [10, 5]}},
        ],
    )
    
    # Render HTML
    html = _render_response_html(response)
    
    # Should not have table HTML
    assert "<table" not in html
    # Should have text content
    assert "Here is your data:" not in html  # No text element


def test_render_mixed_content():
    """Test rendering with text and dataframe together."""
    df = pd.DataFrame({"x": [10, 20], "y": [30, 40]})
    
    response = Response(
        thread_id="test",
        elements=[
            {"type": "text", "value": "Analysis complete!"},
            {"type": "df", "id": "results", "table": df},
            {"type": "text", "value": "Total rows: 2"},
        ],
    )
    
    html = _render_response_html(response)
    
    # Check all content is present
    assert "Analysis complete!" in html
    assert "<table" in html
    assert "10" in html
    assert "20" in html
    assert "30" in html
    assert "40" in html
    assert "Total rows: 2" in html