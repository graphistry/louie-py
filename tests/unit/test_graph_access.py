"""Test graph element access in cursor API."""

from louieai._client import Response
from louieai.notebook.cursor import Cursor, ResponseProxy


class TestGraphAccess:
    """Test accessing graph elements from responses."""

    def test_response_proxy_graph_access(self):
        """Test accessing graphs through ResponseProxy."""
        # Create response with graph elements
        response = Response(
            thread_id="test",
            elements=[
                {"type": "TextElement", "text": "Here's a graph"},
                {
                    "type": "GraphElement",
                    "dataset_id": "graph_123",
                    "value": {"dataset_id": "graph_123"},
                },
                {"type": "graph", "dataset_id": "graph_456"},
            ],
        )

        proxy = ResponseProxy(response)

        # Test gs property
        graphs = proxy.gs
        assert len(graphs) == 2  # Both graph elements from elements list
        assert graphs[0]["dataset_id"] == "graph_123"
        assert graphs[1]["dataset_id"] == "graph_456"

        # Test g property
        graph = proxy.g
        assert graph is not None
        assert graph["dataset_id"] == "graph_456"  # Last graph

    def test_cursor_graph_access(self):
        """Test accessing graphs through Cursor lui[-1].g syntax."""
        cursor = Cursor()

        # Simulate adding responses to history
        response1 = Response(
            thread_id="test1",
            elements=[
                {"type": "graph", "dataset_id": "first_graph"},
            ],
        )

        response2 = Response(
            thread_id="test2",
            elements=[
                {"type": "GraphElement", "dataset_id": "second_graph"},
                {"type": "graph", "dataset_id": "third_graph"},
            ],
        )

        cursor._history.append(response1)
        cursor._history.append(response2)

        # Test current graphs (from latest response)
        assert len(cursor.gs) == 2
        assert cursor.g["dataset_id"] == "third_graph"  # Last graph

        # Test historical access
        assert len(cursor[-2].gs) == 1
        assert cursor[-2].g["dataset_id"] == "first_graph"

        assert len(cursor[-1].gs) == 2
        assert cursor[-1].g["dataset_id"] == "third_graph"  # Last graph

    def test_no_graphs(self):
        """Test behavior when no graphs are present."""
        response = Response(
            thread_id="test",
            elements=[
                {"type": "TextElement", "text": "No graphs here"},
            ],
        )

        proxy = ResponseProxy(response)
        assert proxy.gs == []
        assert proxy.g is None

        # Test with cursor
        cursor = Cursor()
        cursor._history.append(response)
        assert cursor.gs == []
        assert cursor.g is None

    def test_mixed_element_types(self):
        """Test graphs mixed with other element types."""
        response = Response(
            thread_id="test",
            elements=[
                {"type": "TextElement", "text": "Analysis"},
                {"type": "DfElement", "df_id": "df_123"},
                {"type": "graph", "dataset_id": "graph_1"},
                {"type": "TextElement", "text": "More text"},
                {"type": "GraphElement", "dataset_id": "graph_2"},
            ],
        )

        proxy = ResponseProxy(response)

        # Should only get graph elements
        graphs = proxy.gs
        assert len(graphs) == 2
        assert all("dataset_id" in g for g in graphs)
        assert [g["dataset_id"] for g in graphs] == ["graph_1", "graph_2"]

    def test_graph_elements_property(self):
        """Test that Response.graph_elements is computed correctly."""
        response = Response(
            thread_id="test",
            elements=[
                {"type": "TextElement", "text": "Text"},
                {"type": "graph", "dataset_id": "g1"},
                {"type": "GraphElement", "dataset_id": "g2", "extra": "data"},
                {"type": "df", "df_id": "d1"},
            ],
        )

        # graph_elements should filter to just graph types
        graph_elems = response.graph_elements
        assert len(graph_elems) == 2
        assert graph_elems[0]["dataset_id"] == "g1"
        assert graph_elems[1]["dataset_id"] == "g2"
        assert graph_elems[1]["extra"] == "data"
