"""Integration tests for notebook API basic flow."""

import json
import os
from pathlib import Path

import pandas as pd
import pytest

from louieai.globals import lui

# Skip if no credentials provided
has_username = os.environ.get("GRAPHISTRY_USERNAME") is not None
has_password = os.environ.get("GRAPHISTRY_PASSWORD") is not None
pytestmark = pytest.mark.skipif(
    not (has_username and has_password),
    reason="Integration tests require GRAPHISTRY_USERNAME and GRAPHISTRY_PASSWORD",
)


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


class TestBasicFlow:
    """Test basic notebook workflow."""

    def test_simple_query(self, output_dir):
        """Test a simple text query."""
        # Make a basic query
        response = lui("What is 2 + 2?")

        # Save response for analysis
        with open(output_dir / "simple_query_response.json", "w") as f:
            json.dump(
                {
                    "thread_id": response.thread_id,
                    "text_elements": response.text_elements,
                    "dataframe_elements": response.dataframe_elements,
                    "graph_elements": getattr(response, "graph_elements", []),
                    "markdown_elements": getattr(response, "markdown_elements", []),
                    "all_attributes": dir(response),
                },
                f,
                indent=2,
                default=str,
            )

        # Basic assertions
        assert response is not None
        assert response.thread_id
        assert lui.text is not None

        # Session should be active
        repr_str = repr(lui)
        assert "Session: Active" in repr_str
        assert "History: 1 responses" in repr_str

    def test_dataframe_query(self, output_dir):
        """Test query that returns a dataframe."""
        # Query for data
        response = lui(
            "Create a sample dataframe with 5 rows of sales data "
            "including columns: product, quantity, price"
        )

        # Save response
        with open(output_dir / "dataframe_query_response.json", "w") as f:
            json.dump(
                {
                    "thread_id": response.thread_id,
                    "text_elements": response.text_elements,
                    "dataframe_elements": [
                        {
                            "type": elem.get("type"),
                            "has_table": "table" in elem,
                            "table_type": type(elem.get("table", None)).__name__,
                            "shape": (
                                elem.get("table").shape
                                if hasattr(elem.get("table", None), "shape")
                                else None
                            ),
                        }
                        for elem in response.dataframe_elements
                    ],
                    "element_keys": (
                        list(response.dataframe_elements[0].keys())
                        if response.dataframe_elements
                        else []
                    ),
                },
                f,
                indent=2,
                default=str,
            )

        # Check dataframe access
        df = lui.df
        if df is not None:
            assert isinstance(df, pd.DataFrame)
            df.to_csv(output_dir / "sample_dataframe.csv", index=False)
            print(f"DataFrame shape: {df.shape}")
            print(f"DataFrame columns: {list(df.columns)}")

    def test_traces_enabled(self, output_dir):
        """Test query with traces enabled."""
        # Enable traces
        lui.traces = True

        response = lui("Explain step by step how to calculate the area of a circle")

        # Save response with traces
        with open(output_dir / "traces_response.json", "w") as f:
            json.dump(
                {
                    "thread_id": response.thread_id,
                    "text_elements": response.text_elements,
                    "trace_elements": getattr(response, "trace_elements", []),
                    "reasoning_elements": getattr(response, "reasoning_elements", []),
                    "has_traces": (
                        hasattr(response, "trace_elements")
                        or hasattr(response, "reasoning_elements")
                    ),
                },
                f,
                indent=2,
                default=str,
            )

        # Traces should be enabled
        assert lui.traces is True

    def test_history_access(self, output_dir):
        """Test accessing previous responses."""
        # Make multiple queries
        lui("First query")
        lui("Second query")
        lui("Third query")

        # Access history
        assert lui[-1].text == lui.text  # Latest
        assert lui[-2].text is not None  # Second to last
        assert lui[-3].text is not None  # Third to last

        # Save history info
        with open(output_dir / "history_test.json", "w") as f:
            json.dump(
                {
                    "history_length": len(lui._cursor._history),
                    "latest_text": lui.text,
                    "previous_text": lui[-2].text,
                    "all_texts": [lui[i].text for i in range(-3, 0)],
                },
                f,
                indent=2,
                default=str,
            )

    def test_element_types_discovery(self, output_dir):
        """Discover what element types are available."""
        # Try different queries to discover element types
        queries = [
            "Show me a bar chart of monthly sales",
            "Create a markdown table with 3 columns",
            "Plot a simple line graph",
            "Show me some **bold** and *italic* markdown text",
            "Display an image or visualization",
        ]

        all_element_types = set()

        for i, query in enumerate(queries):
            try:
                response = lui(query)

                # Collect all attributes that look like elements
                element_attrs = [
                    attr
                    for attr in dir(response)
                    if attr.endswith("_elements") and not attr.startswith("_")
                ]

                all_element_types.update(element_attrs)

                # Save detailed info about this response
                with open(output_dir / f"element_discovery_{i}.json", "w") as f:
                    element_info = {}
                    for attr in element_attrs:
                        elements = getattr(response, attr, [])
                        if elements:
                            element_info[attr] = [
                                {
                                    "keys": (
                                        list(elem.keys())
                                        if isinstance(elem, dict)
                                        else None
                                    ),
                                    "type": (
                                        elem.get("type", None)
                                        if isinstance(elem, dict)
                                        else None
                                    ),
                                    "sample": str(elem)[:200],
                                }
                                for elem in elements[:2]  # Just first 2 samples
                            ]

                    json.dump(
                        {
                            "query": query,
                            "element_types_found": element_attrs,
                            "element_details": element_info,
                            "text_response": lui.text[:500] if lui.text else None,
                        },
                        f,
                        indent=2,
                        default=str,
                    )

            except Exception as e:
                print(f"Query failed: {query} - {e}")

        # Save summary
        with open(output_dir / "element_types_summary.json", "w") as f:
            json.dump(
                {
                    "all_element_types_discovered": list(all_element_types),
                    "notes": (
                        "These are all the *_elements attributes found "
                        "across different queries"
                    ),
                },
                f,
                indent=2,
            )

        print(f"Discovered element types: {all_element_types}")

    def test_error_handling(self):
        """Test error scenarios."""
        # Access data before any query
        assert lui.df is None
        assert lui.text is None
        assert lui.dfs == []

        # Out of bounds history
        assert lui[-10].df is None

        # After a query, should have data
        lui("Hello")
        assert lui.text is not None
