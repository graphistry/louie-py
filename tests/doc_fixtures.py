"""Mock fixtures for documentation examples.

These fixtures are based on real API responses validated in Step 30.
"""

from unittest.mock import Mock

from louieai import Response, Thread


def create_mock_responses():
    """Create realistic mock responses for documentation testing."""

    # Text response with hello message
    hello_elements = [
        {
            "type": "TextElement",
            "id": "B_mock123",
            "text": "Hello from Louie!",
            "language": "Markdown",
        }
    ]
    hello_response = Response("D_mockThread123", hello_elements)

    # Text response with analysis
    analysis_elements = [
        {
            "type": "TextElement",
            "id": "B_mock456",
            "text": """Based on the analysis of sales trends:

1. **Q4 Performance**: Sales increased 15% year-over-year
2. **Top Products**: Electronics category dominated with 45% of revenue
3. **Growth Areas**: New markets in APAC showing 25% monthly growth

Key insights:
- Customer retention improved by 12%
- Average order value up $35
- Mobile purchases now represent 60% of total sales""",
            "language": "Markdown",
        }
    ]
    analysis_response = Response("D_mockThread456", analysis_elements)

    # DataFrame response
    df_elements = [
        {
            "type": "DfElement",
            "id": "B_df789",
            "metadata": {
                "shape": [100, 5],
                "columns": {
                    "customer_id": "int64",
                    "name": "string",
                    "signup_date": "datetime64[ns]",
                    "total_purchases": "float64",
                    "status": "string",
                },
                "summary": {"total_purchases": {"min": 0, "max": 5000, "mean": 250.5}},
            },
        }
    ]
    df_response = Response("D_mockThread789", df_elements)

    # Mock DataFrame
    import pandas as pd

    mock_df = pd.DataFrame(
        {
            "customer_id": range(5),
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "signup_date": pd.date_range("2024-01-01", periods=5),
            "total_purchases": [150.5, 320.0, 87.5, 450.25, 200.0],
            "status": ["active", "active", "pending", "active", "inactive"],
        }
    )

    # Multi-element response (text + dataframe)
    mixed_elements = [
        {
            "type": "TextElement",
            "id": "B_mixed_text",
            "text": "Here's your customer data analysis:",
            "language": "Markdown",
        },
        {
            "type": "DfElement",
            "id": "B_mixed_df",
            "metadata": {
                "shape": [5, 5],
                "columns": {
                    "customer_id": "int64",
                    "name": "string",
                    "signup_date": "datetime64[ns]",
                    "total_purchases": "float64",
                    "status": "string",
                },
            },
        },
    ]
    mixed_response = Response("D_mockMixed", mixed_elements)

    return {
        "hello": hello_response,
        "analysis": analysis_response,
        "dataframe": df_response,
        "mixed": mixed_response,
        "mock_df": mock_df,
    }


def create_mock_client():
    """Create a mock LouieClient for testing documentation examples."""
    from louieai._client import LouieClient

    # Mock the client
    mock_client = Mock(spec=LouieClient)

    # Create mock responses
    responses = create_mock_responses()

    # Mock thread creation
    def mock_create_thread(name=None, initial_prompt=None):
        thread = Thread(id="D_mockThread", name=name)
        if initial_prompt:
            # Return the thread - in real usage, initial response would be from add_cell
            return thread
        return thread

    mock_client.create_thread.side_effect = mock_create_thread

    # Mock add_cell method
    def mock_add_cell(thread_id, prompt):
        if "hello" in prompt.lower():
            return responses["hello"]
        elif "analysis" in prompt.lower() or "trends" in prompt.lower():
            return responses["analysis"]
        elif "data" in prompt.lower() or "dataframe" in prompt.lower():
            return responses["dataframe"]
        else:
            return responses["mixed"]

    mock_client.add_cell.side_effect = mock_add_cell

    # Mock list_threads
    mock_client.list_threads.return_value = [
        Thread(id="D_thread1", name="Analysis Session"),
        Thread(id="D_thread2", name="Data Exploration"),
    ]

    # Mock get_thread
    mock_client.get_thread.return_value = Thread(
        id="D_thread1", name="Analysis Session"
    )

    return mock_client
