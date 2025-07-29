"""Comprehensive mock response library for unit testing.

This module provides realistic mock responses for all Louie API response types.
"""

import json
from datetime import datetime, timezone
from typing import Any


class MockResponseLibrary:
    """Library of realistic mock responses for different query types."""

    @staticmethod
    def text_response(
        text: str,
        thread_id: str = "D_test001",
        element_id: str = "B_text_001",
        language: str = "Markdown",
    ) -> dict[str, Any]:
        """Create a mock TextElement response."""
        return {
            "id": element_id,
            "type": "TextElement",
            "text": text,
            "language": language,
            "thread_id": thread_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
        }

    @staticmethod
    def dataframe_response(
        thread_id: str = "D_test001",
        element_id: str = "B_df_001",
        shape: tuple = (10, 5),
        columns: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a mock DfElement response."""
        if columns is None:
            columns = ["id", "name", "value", "created_at", "status"]

        return {
            "id": element_id,
            "type": "DfElement",
            "df_id": f"df_{element_id}",
            "thread_id": thread_id,
            "metadata": {
                "shape": list(shape),
                "columns": columns,
                "dtypes": dict.fromkeys(columns, "object"),
                "memory_usage": shape[0] * shape[1] * 8,
                "description": f"DataFrame with {shape[0]} rows and {shape[1]} columns",
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
        }

    @staticmethod
    def graph_response(
        thread_id: str = "D_test001",
        element_id: str = "B_graph_001",
        dataset_id: str = "abc123def456",
        num_nodes: int = 100,
        num_edges: int = 200,
    ) -> dict[str, Any]:
        """Create a mock GraphElement response."""
        return {
            "id": element_id,
            "type": "GraphElement",
            "dataset_id": dataset_id,
            "thread_id": thread_id,
            "metadata": {
                "num_nodes": num_nodes,
                "num_edges": num_edges,
                "node_encodings": {
                    "color": {"attribute": "risk_score", "type": "continuous"},
                    "size": {"attribute": "transaction_volume", "type": "continuous"},
                },
                "edge_encodings": {
                    "color": {"attribute": "relationship_type", "type": "categorical"}
                },
            },
            "url": f"https://hub.graphistry.com/graph/graph.html?dataset={dataset_id}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
        }

    @staticmethod
    def exception_response(
        error_type: str = "ValidationError",
        message: str = "Invalid query parameters",
        thread_id: str = "D_test001",
        element_id: str = "B_exc_001",
    ) -> dict[str, Any]:
        """Create a mock ExceptionElement response."""
        return {
            "id": element_id,
            "type": "ExceptionElement",
            "error_type": error_type,
            "message": message,
            "thread_id": thread_id,
            "traceback": (
                f"Traceback (most recent call last):\n"
                f"  File '<stdin>', line 1\n"
                f"{error_type}: {message}"
            ),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
        }

    @staticmethod
    def image_response(
        thread_id: str = "D_test001",
        element_id: str = "B_img_001",
        alt_text: str = "Generated chart",
        chart_type: str = "line",
    ) -> dict[str, Any]:
        """Create a mock Base64ImageElement response."""
        # Mock base64 image data (1x1 transparent PNG)
        base64_data = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
            "YPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        )

        return {
            "id": element_id,
            "type": "Base64ImageElement",
            "src": f"data:image/png;base64,{base64_data}",
            "alt": alt_text,
            "thread_id": thread_id,
            "metadata": {
                "chart_type": chart_type,
                "width": 800,
                "height": 600,
                "format": "png",
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
        }

    @staticmethod
    def kepler_response(
        thread_id: str = "D_test001",
        element_id: str = "B_kepler_001",
        map_id: str = "map_123",
    ) -> dict[str, Any]:
        """Create a mock KeplerElement response."""
        return {
            "id": element_id,
            "type": "KeplerElement",
            "map_id": map_id,
            "thread_id": thread_id,
            "config": {
                "version": "v1",
                "config": {
                    "visState": {
                        "filters": [],
                        "layers": [
                            {
                                "type": "point",
                                "config": {
                                    "dataId": "locations",
                                    "columns": {"lat": "latitude", "lng": "longitude"},
                                },
                            }
                        ],
                    }
                },
            },
            "url": f"https://kepler.gl/demo?mapId={map_id}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
        }

    @staticmethod
    def call_response(
        function_name: str = "query_database",
        args: dict[str, Any] | None = None,
        result: Any | None = None,
        thread_id: str = "D_test001",
        element_id: str = "B_call_001",
    ) -> dict[str, Any]:
        """Create a mock CallElement response."""
        if args is None:
            args = {"database": "postgresql", "query": "SELECT * FROM users LIMIT 10"}
        if result is None:
            result = {"rows_returned": 10, "execution_time": 0.05}

        return {
            "id": element_id,
            "type": "CallElement",
            "function": function_name,
            "args": args,
            "result": result,
            "thread_id": thread_id,
            "metadata": {"agent": "DataAgent", "duration_ms": 50},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
        }


class MockStreamingResponse:
    """Simulate streaming JSONL responses."""

    def __init__(self, elements: list[dict[str, Any]], thread_id: str = "D_test001"):
        self.elements = elements
        self.thread_id = thread_id
        self._current_index = 0

    def iter_lines(self):
        """Iterate over response lines, simulating streaming."""
        for element in self.elements:
            # Add thread_id if not present
            if "thread_id" not in element:
                element["thread_id"] = self.thread_id

            # Simulate progressive updates for text elements
            if element.get("type") == "TextElement" and element.get("text"):
                text = element["text"]
                # Stream text in chunks
                words = text.split()
                partial_text = ""
                for i, word in enumerate(words):
                    partial_text += word + " "
                    partial_element = element.copy()
                    partial_element["text"] = partial_text.strip()
                    partial_element["status"] = (
                        "streaming" if i < len(words) - 1 else "completed"
                    )
                    yield json.dumps(partial_element).encode("utf-8")
            else:
                # Non-text elements are sent complete
                yield json.dumps(element).encode("utf-8")


class ResponseScenarios:
    """Pre-built response scenarios for common test cases."""

    @staticmethod
    def simple_question() -> list[dict[str, Any]]:
        """Response for a simple question."""
        return [
            MockResponseLibrary.text_response(
                "The capital of France is Paris. It's known for the Eiffel Tower, "
                "Louvre Museum, and its rich cultural heritage."
            )
        ]

    @staticmethod
    def data_query() -> list[dict[str, Any]]:
        """Response for a data query."""
        return [
            MockResponseLibrary.text_response("Querying customer database..."),
            MockResponseLibrary.call_response(
                function_name="query_postgresql",
                args={
                    "query": (
                        "SELECT * FROM customers WHERE created_at > '2024-01-01' "
                        "LIMIT 100"
                    )
                },
            ),
            MockResponseLibrary.dataframe_response(
                shape=(100, 5),
                columns=["customer_id", "name", "email", "created_at", "status"],
            ),
            MockResponseLibrary.text_response(
                "Found 100 customers who joined after January 1, 2024. "
                "The data shows a mix of active and pending customers."
            ),
        ]

    @staticmethod
    def visualization_request() -> list[dict[str, Any]]:
        """Response for a visualization request."""
        return [
            MockResponseLibrary.text_response("Creating network visualization..."),
            MockResponseLibrary.call_response(
                function_name="build_graph",
                args={"nodes": 500, "edges": 1200, "layout": "force-directed"},
            ),
            MockResponseLibrary.graph_response(num_nodes=500, num_edges=1200),
            MockResponseLibrary.text_response(
                "Created network graph with 500 nodes and 1,200 edges. "
                "Nodes are colored by risk score and sized by transaction volume."
            ),
        ]

    @staticmethod
    def error_scenario() -> list[dict[str, Any]]:
        """Response with an error."""
        return [
            MockResponseLibrary.text_response("Processing your request..."),
            MockResponseLibrary.exception_response(
                error_type="DatabaseConnectionError",
                message="Failed to connect to database: Connection timeout",
            ),
            MockResponseLibrary.text_response(
                "I encountered an error connecting to the database. "
                "Please check your connection settings and try again."
            ),
        ]

    @staticmethod
    def multi_step_analysis() -> list[dict[str, Any]]:
        """Response for a complex multi-step analysis."""
        return [
            MockResponseLibrary.text_response("Starting comprehensive analysis..."),
            MockResponseLibrary.call_response(
                function_name="query_database",
                args={
                    "database": "clickhouse",
                    "query": "SELECT * FROM events WHERE timestamp > now() - 7",
                },
            ),
            MockResponseLibrary.dataframe_response(shape=(10000, 8)),
            MockResponseLibrary.text_response(
                "Processing 10,000 events from the last 7 days..."
            ),
            MockResponseLibrary.call_response(
                function_name="detect_anomalies",
                args={"method": "isolation_forest", "contamination": 0.1},
            ),
            MockResponseLibrary.dataframe_response(
                shape=(1000, 9),
                columns=[
                    "event_id",
                    "timestamp",
                    "user_id",
                    "action",
                    "anomaly_score",
                    "is_anomaly",
                    "reason",
                    "severity",
                    "recommended_action",
                ],
            ),
            MockResponseLibrary.text_response(
                "Found 1,000 anomalous events. Creating visualization..."
            ),
            MockResponseLibrary.image_response(
                alt_text="Anomaly distribution over time", chart_type="scatter"
            ),
            MockResponseLibrary.text_response(
                """## Analysis Summary

Found 1,000 anomalous events (10% of total) with the following breakdown:
- High severity: 150 events
- Medium severity: 350 events
- Low severity: 500 events

### Key Findings:
1. Spike in anomalies on Tuesday between 2-4 PM
2. User accounts 'user_123' and 'user_456' show suspicious patterns
3. Most anomalies relate to unusual transaction amounts

### Recommendations:
- Investigate the Tuesday spike for potential system issues
- Review flagged user accounts for potential fraud
- Set up alerts for similar patterns in the future
"""
            ),
        ]


def create_mock_api_response(
    query: str, thread_id: str = "D_test001"
) -> MockStreamingResponse:
    """Create a mock API response based on the query content."""
    query_lower = query.lower()

    # Determine appropriate response scenario
    if any(
        word in query_lower
        for word in ["data", "query", "database", "sql", "customers", "users"]
    ):
        elements = ResponseScenarios.data_query()
    elif any(
        word in query_lower for word in ["graph", "network", "visualiz", "connections"]
    ):
        elements = ResponseScenarios.visualization_request()
    elif any(
        word in query_lower for word in ["analyze", "anomal", "pattern", "insight"]
    ):
        elements = ResponseScenarios.multi_step_analysis()
    elif any(word in query_lower for word in ["error", "fail", "problem"]):
        elements = ResponseScenarios.error_scenario()
    else:
        elements = ResponseScenarios.simple_question()

    return MockStreamingResponse(elements, thread_id)
