"""Mock integration tests for notebook API to discover element types."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from louieai import Response
from louieai.globals import lui


@pytest.fixture(scope="module")
def output_dir():
    """Create output directory for test artifacts."""
    output_path = Path("/tmp/louie-notebook-tests")
    output_path.mkdir(exist_ok=True)
    return output_path


@pytest.fixture(autouse=True)
def reset_lui():
    """Reset lui singleton before each test."""
    import louieai.notebook

    louieai.notebook._global_cursor = None
    yield
    # Cleanup after test
    louieai.notebook._global_cursor = None


def create_mock_response(thread_id="test-123", **kwargs):
    """Create a mock response with various element types."""
    response = Mock(spec=Response)
    response.thread_id = thread_id

    # Default empty lists for all element types
    response.text_elements = kwargs.get("text_elements", [])
    response.dataframe_elements = kwargs.get("dataframe_elements", [])
    response.graph_elements = kwargs.get("graph_elements", [])
    response.markdown_elements = kwargs.get("markdown_elements", [])
    response.image_elements = kwargs.get("image_elements", [])
    response.chart_elements = kwargs.get("chart_elements", [])
    response.code_elements = kwargs.get("code_elements", [])
    response.error_elements = kwargs.get("error_elements", [])

    # Add any other element types passed in
    for key, value in kwargs.items():
        if key.endswith("_elements") and not hasattr(response, key):
            setattr(response, key, value)

    return response


class TestElementDiscovery:
    """Test discovery of different element types."""

    @patch("louieai.notebook.cursor.Cursor._in_jupyter", return_value=False)
    @patch("louieai.notebook.cursor.LouieClient")
    def test_text_elements(self, mock_client_class, mock_jupyter, output_dir):
        """Test handling of text elements."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock the _get_headers method to return a proper dict
        mock_client._get_headers.return_value = {"Authorization": "Bearer fake-token"}
        mock_client.server_url = "https://test.louie.ai"

        # Create response with text
        response = create_mock_response(
            text_elements=[
                {"type": "TextElement", "content": "Hello world"},
                {"type": "TextElement", "content": "Second text"},
            ]
        )
        mock_client.add_cell.return_value = response

        # Query
        lui("test")

        # Verify text access
        assert lui.text == "Second text"  # Now returns last text
        assert lui.texts == ["Hello world", "Second text"]

        # Save for analysis
        with open(output_dir / "text_elements.json", "w") as f:
            json.dump(
                {
                    "elements": response.text_elements,
                    "lui.text": lui.text,
                    "lui.texts": lui.texts,
                },
                f,
                indent=2,
            )

    @patch("louieai.notebook.cursor.Cursor._in_jupyter", return_value=False)
    @patch("louieai.notebook.cursor.LouieClient")
    def test_dataframe_elements(self, mock_client_class, mock_jupyter, output_dir):
        """Test handling of dataframe elements."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock the _get_headers method to return a proper dict
        mock_client._get_headers.return_value = {"Authorization": "Bearer fake-token"}
        mock_client.server_url = "https://test.louie.ai"

        # Create sample dataframes
        df1 = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        df2 = pd.DataFrame({"x": [7, 8], "y": [9, 10]})

        response = create_mock_response(
            dataframe_elements=[
                {"type": "DfElement", "table": df1, "description": "First table"},
                {"type": "DfElement", "table": df2, "description": "Second table"},
            ]
        )
        mock_client.add_cell.return_value = response

        # Query
        lui("test")

        # Verify dataframe access
        assert lui.df is not None
        pd.testing.assert_frame_equal(lui.df, df2)  # Now returns last dataframe
        assert len(lui.dfs) == 2

        # Save for analysis
        with open(output_dir / "dataframe_elements.json", "w") as f:
            json.dump(
                {
                    "element_structure": [
                        {
                            "type": elem.get("type"),
                            "keys": list(elem.keys()),
                            "has_table": "table" in elem,
                            "shape": elem["table"].shape if "table" in elem else None,
                        }
                        for elem in response.dataframe_elements
                    ],
                    "df_shapes": [df.shape for df in lui.dfs],
                },
                f,
                indent=2,
                default=str,
            )

    @patch("louieai.notebook.cursor.Cursor._in_jupyter", return_value=False)
    @patch("louieai.notebook.cursor.LouieClient")
    def test_graph_elements(self, mock_client_class, mock_jupyter, output_dir):
        """Test handling of graph elements."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock the _get_headers method to return a proper dict
        mock_client._get_headers.return_value = {"Authorization": "Bearer fake-token"}
        mock_client.server_url = "https://test.louie.ai"

        response = create_mock_response(
            graph_elements=[
                {
                    "type": "GraphElement",
                    "nodes": [{"id": 1}, {"id": 2}],
                    "edges": [{"source": 1, "target": 2}],
                    "style": {"node_color": "blue"},
                }
            ]
        )
        mock_client.add_cell.return_value = response

        # Query
        lui("test")

        # Check elements
        elements = lui.elements
        graph_elements = [e for e in elements if e["type"] == "graph"]
        assert len(graph_elements) == 1

        # Save for analysis
        with open(output_dir / "graph_elements.json", "w") as f:
            json.dump(
                {
                    "graph_elements": response.graph_elements,
                    "extracted_elements": graph_elements,
                },
                f,
                indent=2,
            )

    @patch("louieai.notebook.cursor.Cursor._in_jupyter", return_value=False)
    @patch("louieai.notebook.cursor.LouieClient")
    def test_markdown_elements(self, mock_client_class, mock_jupyter, output_dir):
        """Test handling of markdown elements."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock the _get_headers method to return a proper dict
        mock_client._get_headers.return_value = {"Authorization": "Bearer fake-token"}
        mock_client.server_url = "https://test.louie.ai"

        # Try markdown elements (may not exist yet)
        response = create_mock_response(
            markdown_elements=[
                {
                    "type": "MarkdownElement",
                    "content": "# Header\n\n**Bold** and *italic*",
                    "format": "markdown",
                }
            ]
        )
        mock_client.add_cell.return_value = response

        # Query
        lui("test")

        # Save what we found
        with open(output_dir / "markdown_elements.json", "w") as f:
            json.dump(
                {
                    "has_markdown_elements": hasattr(response, "markdown_elements"),
                    "markdown_elements": getattr(response, "markdown_elements", []),
                    "all_attributes": [
                        attr for attr in dir(response) if attr.endswith("_elements")
                    ],
                },
                f,
                indent=2,
            )

    @patch("louieai.notebook.cursor.Cursor._in_jupyter", return_value=False)
    @patch("louieai.notebook.cursor.LouieClient")
    def test_all_element_types(self, mock_client_class, mock_jupyter, output_dir):
        """Discover all element types supported by Response."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock the _get_headers method to return a proper dict
        mock_client._get_headers.return_value = {"Authorization": "Bearer fake-token"}
        mock_client.server_url = "https://test.louie.ai"

        # Create a real Response object to inspect
        from louieai import Response

        # Get all potential element attributes
        element_attrs = [
            attr
            for attr in dir(Response)
            if attr.endswith("_elements") and not attr.startswith("_")
        ]

        # Create response with various elements
        response = create_mock_response(
            text_elements=[{"type": "TextElement", "content": "text"}],
            dataframe_elements=[
                {"type": "DfElement", "table": pd.DataFrame({"a": [1]})}
            ],
            graph_elements=[{"type": "GraphElement", "data": {}}],
            code_elements=[
                {"type": "CodeElement", "code": "print('hello')", "language": "python"}
            ],
            image_elements=[
                {"type": "ImageElement", "url": "http://example.com/img.png"}
            ],
            chart_elements=[{"type": "ChartElement", "spec": {"type": "bar"}}],
        )
        mock_client.add_cell.return_value = response

        # Query
        lui("test")

        # Collect all elements
        all_elements = lui.elements

        # Save comprehensive analysis
        with open(output_dir / "all_element_types.json", "w") as f:
            json.dump(
                {
                    "response_element_attributes": element_attrs,
                    "mock_response_attributes": [
                        attr
                        for attr in dir(response)
                        if attr.endswith("_elements") and not attr.startswith("_")
                    ],
                    "elements_found_in_lui": {
                        "count": len(all_elements),
                        "types": list({e["type"] for e in all_elements}),
                        "sample": all_elements[:3] if all_elements else [],
                    },
                    "current_implementation_supports": [
                        "text_elements",
                        "dataframe_elements",
                        "graph_elements",
                    ],
                    "potentially_missing": [
                        "markdown_elements",
                        "code_elements",
                        "image_elements",
                        "chart_elements",
                        "error_elements",
                    ],
                },
                f,
                indent=2,
                default=str,
            )

        print(f"\nElement types on Response class: {element_attrs}")
        print(f"Elements extracted by lui: {len(all_elements)}")
        element_types = {e["type"] for e in all_elements}
        print(f"Element types found: {element_types}")
