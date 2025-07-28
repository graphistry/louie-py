#!/usr/bin/env python3
"""Export Louie.ai element types for documentation.

This script should be placed in graphistrygpt/scripts/export_element_types.py
and run to generate element_types.json for louie-py documentation.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

from graphistrygpt.models.elements import (
    Base64ImageElement,
    CallElement,
    DfElement,
    ElementUnion,
    ExceptionElement,
    GraphElement,
    InputGroupElement,
    KeplerElement,
    PerspectiveElement,
    TextElement,
)

# Version should be updated when element types change
EXPORT_VERSION = "1.0.0"


def get_git_sha() -> str:
    """Get current git SHA for versioning."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()[:8]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def get_element_examples() -> dict[str, list]:
    """Return example instances for each element type."""
    return {
        "TextElement": [
            {
                "name": "Natural language response",
                "value": TextElement(
                    text="Based on the analysis, sales increased 15% year-over-year",
                    language="Markdown",
                ).model_dump(),
            },
            {
                "name": "JSON response",
                "value": TextElement(
                    text='{"status": "success", "count": 42}',
                    language="JSON",
                ).model_dump(),
            },
            {
                "name": "SQL query",
                "value": TextElement(
                    text="SELECT user_id, COUNT(*) FROM events GROUP BY user_id",
                    language="SQL",
                ).model_dump(),
            },
        ],
        "DfElement": [
            {
                "name": "Query result",
                "description": "Example metadata structure",
                "value": {
                    "type": "DfElement",
                    "version": 0,
                    "metadata": {
                        "shape": [100, 5],
                        "columns": ["id", "name", "value", "created_at", "status"],
                        "dtypes": {
                            "id": "int64",
                            "name": "object",
                            "value": "float64",
                            "created_at": "datetime64[ns]",
                            "status": "object",
                        },
                    },
                },
            }
        ],
        "GraphElement": [
            {
                "name": "Network visualization",
                "value": {
                    "type": "GraphElement",
                    "dataset_id": "abc123def456",
                    "status": "completed",
                    "params": {
                        "node_color": "risk_score",
                        "edge_weight": "transaction_amount",
                        "layout": "forceatlas2",
                    },
                },
            }
        ],
        "ExceptionElement": [
            {
                "name": "Database error",
                "value": ExceptionElement(
                    text="Table 'users' not found",
                    traceback=(
                        'psycopg2.ProgrammingError: relation "users" does not exist\n'
                        "  at execute_query..."
                    ),
                ).model_dump(),
            },
            {
                "name": "Connection timeout",
                "value": ExceptionElement(
                    text="Connection to database timed out after 30 seconds",
                    traceback=None,
                ).model_dump(),
            },
        ],
        "KeplerElement": [
            {
                "name": "Geographic visualization",
                "value": {
                    "type": "KeplerElement",
                    "title": "Customer Locations Heatmap",
                    "config": {
                        "mapState": {"latitude": 37.7749, "longitude": -122.4194},
                        "layers": [
                            {"type": "heatmap", "config": {"colorRange": "viridis"}}
                        ],
                    },
                },
            }
        ],
        "PerspectiveElement": [
            {
                "name": "Sales heatmap",
                "value": {
                    "type": "PerspectiveElement",
                    "df_element_id": "df_123",
                    "config": {
                        "plugin": "d3_heatmap",
                        "columns": ["region", "product"],
                        "aggregates": {"revenue": "sum"},
                    },
                },
            }
        ],
        "Base64ImageElement": [
            {
                "name": "Generated chart",
                "value": {
                    "type": "Base64ImageElement",
                    "src": (
                        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR"
                        "42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                    ),
                    "width": 800,
                    "height": 600,
                    "props": {"format": "png", "dpi": 300},
                },
            }
        ],
        "CallElement": [
            {
                "name": "Agent execution record",
                "value": {
                    "type": "CallElement",
                    "agent": "sql",
                    "text": "SELECT * FROM users WHERE status = 'active'",
                    "language": "SQL",
                    "run_id": "run_abc123",
                },
            }
        ],
        "InputGroupElement": [
            {
                "name": "Interactive form",
                "value": {
                    "type": "InputGroupElement",
                    "items": [
                        {"type": "text", "label": "Enter username", "required": True}
                    ],
                },
            }
        ],
    }


def get_common_queries() -> dict[str, list]:
    """Return common queries that generate each element type."""
    return {
        "TextElement": [
            "Summarize the key findings from the analysis",
            "Explain the correlation between sales and marketing spend",
            "Generate an executive summary of the quarterly results",
            "What patterns do you see in the customer data?",
            "Create a SQL query to find high-value customers",
        ],
        "DfElement": [
            "Query PostgreSQL for customer demographics",
            "Get sales metrics from ClickHouse for the last quarter",
            "Search Splunk logs for error patterns in the last 24 hours",
            "Load and analyze the uploaded CSV file",
            "Find all users who haven't logged in for 30 days",
        ],
        "GraphElement": [
            "Visualize user connections in Graphistry",
            "Create a network graph of system dependencies",
            "Show fraud patterns as a graph visualization",
            "Map relationships between customers and products",
            "Generate a social network analysis of user interactions",
        ],
        "ExceptionElement": [
            "Query non_existent_table",
            "Connect to invalid database server",
            "Execute malformed SQL syntax",
            "Access data without proper permissions",
        ],
        "KeplerElement": [
            "Create a Kepler map of customer locations by revenue",
            "Show delivery routes with timing information",
            "Visualize regional sales data as a heatmap",
            "Map store locations with performance metrics",
            "Display geographic distribution of user activity",
        ],
        "PerspectiveElement": [
            "Create a heatmap of sales by region and product category",
            "Generate a pivot table of expenses by department and month",
            "Build an interactive chart of website traffic trends",
            "Show a treemap of revenue by business unit",
        ],
        "Base64ImageElement": [
            "Plot a line chart of monthly sales trends",
            "Create a bar chart comparing product performance",
            "Generate a scatter plot of price vs demand",
            "Make a histogram of customer age distribution",
        ],
        "CallElement": [
            # Note: CallElements are usually internal records, not user-facing
            "Internal: Record of SQL agent execution",
            "Internal: Python code execution trace",
        ],
        "InputGroupElement": [
            # Note: Usually for interactive forms, not common in API responses
            "Create an interactive form for data input",
            "Generate a survey form for user feedback",
        ],
    }


def export_types():
    """Export all element types to JSON Schema format."""
    # Get individual schemas
    element_types = {}

    # Get all element classes from the union
    element_classes = [
        TextElement,
        DfElement,
        GraphElement,
        ExceptionElement,
        KeplerElement,
        PerspectiveElement,
        Base64ImageElement,
        CallElement,
        InputGroupElement,
    ]

    examples = get_element_examples()
    queries = get_common_queries()

    for element_class in element_classes:
        name = element_class.__name__
        element_types[name] = {
            "schema": element_class.model_json_schema(),
            "description": (
                element_class.__doc__.strip()
                if element_class.__doc__
                else f"{name} element"
            ),
            "examples": examples.get(name, []),
            "common_queries": queries.get(name, []),
        }

    # Build export data
    export_data = {
        "version": EXPORT_VERSION,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source_version": get_git_sha(),
        "schema_version": "http://json-schema.org/draft-07/schema#",
        "metadata": {
            "description": "Louie.ai element types for API responses",
            "source_repo": "graphistrygpt",
            "export_script": "scripts/export_element_types.py",
            "total_types": len(element_types),
        },
        "element_union": ElementUnion.model_json_schema(),
        "element_types": element_types,
        "response_patterns": {
            "single_element": {
                "description": "Most queries return a single element",
                "example": {
                    "query": "Query PostgreSQL for user count",
                    "response_type": "DfElement",
                },
            },
            "multi_element": {
                "description": (
                    "Complex queries can return multiple elements in sequence"
                ),
                "example": {
                    "query": (
                        "Query sales data, create UMAP visualization, "
                        "and summarize insights"
                    ),
                    "response_types": ["DfElement", "GraphElement", "TextElement"],
                },
            },
            "error_handling": {
                "description": (
                    "Errors return ExceptionElement with detailed information"
                ),
                "example": {
                    "query": "Query invalid_table",
                    "response_type": "ExceptionElement",
                },
            },
            "streaming": {
                "description": "Long-running operations may return progress updates",
                "example": {
                    "query": "Process 10M records with ML analysis",
                    "response_types": ["TextElement (progress)", "DfElement (results)"],
                },
            },
        },
        "changelog": [
            {
                "version": "1.0.0",
                "date": "2025-07-27",
                "changes": [
                    "Initial export of all element types",
                    "Added examples and queries",
                ],
            }
        ],
    }

    # Create exports directory if it doesn't exist
    script_dir = Path(__file__).parent
    exports_dir = script_dir.parent / "exports"
    exports_dir.mkdir(exist_ok=True)

    # Write to file
    output_path = exports_dir / "element_types.json"
    with open(output_path, "w") as f:
        json.dump(export_data, f, indent=2, sort_keys=True)

    print(f"✅ Exported element types to {output_path}")
    print(f"   Version: {EXPORT_VERSION}")
    print(f"   Types: {len(element_types)}")
    print(f"   Source: {export_data['source_version']}")
    print("")
    print("Next steps:")
    print("1. Copy to louie-py: cp exports/element_types.json ../louie-py/data/")
    print(
        "2. Generate docs: "
        "cd ../louie-py && uv run python scripts/generate_type_docs.py"
    )
    print("3. Review generated documentation")

    return 0


if __name__ == "__main__":
    exit(export_types())
