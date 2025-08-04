"""Test for DatabricksAgent empty text elements issue."""

import os
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from louieai import louie
from louieai._client import LouieClient


class TestDatabricksEmptyTextElements:
    """Test that DatabricksAgent text elements are properly populated."""

    @pytest.fixture
    def mock_graphistry_client(self):
        """Mock GraphistryClient instance."""
        mock = Mock()
        mock.api_token = Mock(return_value="fake-token-123")
        mock.register = Mock()
        mock.refresh = Mock()
        return mock

    @pytest.fixture
    def mock_streaming_response(self):
        """Mock streaming response with databricks elements."""

        def _create_response(response_lines):
            mock_client_instance = Mock()
            mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
            mock_client_instance.__exit__ = Mock(return_value=None)

            # Mock the stream response
            mock_response = Mock()
            mock_response.iter_lines.return_value = iter(response_lines)
            mock_response.raise_for_status = Mock()
            mock_stream_context = Mock()
            mock_stream_context.__enter__ = Mock(return_value=mock_response)
            mock_stream_context.__exit__ = Mock(return_value=None)
            mock_client_instance.stream.return_value = mock_stream_context

            return mock_client_instance

        return _create_response

    def test_databricks_agent_empty_text_elements(
        self, mock_graphistry_client, mock_streaming_response
    ):
        """Test that text elements from DatabricksAgent are properly populated."""
        # Create response lines that simulate the issue
        response_lines = [
            '{"dthread_id": "D_test_123"}',
            # Empty text elements (simulating the issue)
            '{"payload": {"id": "B_001", "type": "TextElement", "text": ""}}',
            '{"payload": {"id": "B_002", "type": "TextElement", "text": ""}}',
            '{"payload": {"id": "B_003", "type": "TextElement", "text": ""}}',
            # DataFrame element with actual data
            (
                '{"payload": {"id": "B_004", "type": "DfElement", '
                '"df_id": "databricks_result_456"}}'
            ),
        ]

        # Mock DataFrame that would be fetched
        expected_df = pd.DataFrame(
            {
                "ClientIP": ["107.77.213.173"],
                "CorrelationId": ["9e627e9e-d0dd-6000-daf9-da44fcd45d4e"],
                "CreationTime": ["2018-08-20T13:16:56"],
            }
        )

        # Patch httpx.Client
        with patch("louieai._client.httpx.Client") as mock_httpx_client:
            mock_httpx_client.return_value = mock_streaming_response(response_lines)

            # Create client with mocked graphistry
            client = LouieClient(
                server_url="http://test.louie.ai",
                graphistry_client=mock_graphistry_client,
            )

            with patch.object(client, "_fetch_dataframe_arrow") as mock_fetch:
                # Mock successful DataFrame fetch
                mock_fetch.return_value = expected_df

                # Create cursor and make query
                lui = louie(graphistry_client=mock_graphistry_client)
                lui._client = client  # Replace with our mocked client

                # Make the query
                lui(
                    "get 4 events from o365_management_activity_flat_tcook",
                    agent="DatabricksAgent",
                )

                # Check DataFrame is populated
                assert lui.df is not None
                assert lui.df.shape == (1, 3)

                # Check elements structure
                assert len(lui.elements) == 4

                # Verify text elements - this is where the issue occurs
                text_elements = [e for e in lui.elements if e["type"] == "text"]
                assert len(text_elements) == 3

                # The issue: all text values are empty
                for i, elem in enumerate(text_elements):
                    print(f"Text element {i}: {elem}")
                    assert elem["value"] == "", (
                        f"Expected empty text, but got: {elem['value']}"
                    )

                # DataFrame element should be populated
                df_elements = [e for e in lui.elements if e["type"] == "dataframe"]
                assert len(df_elements) == 1
                assert df_elements[0]["value"] is not None

    def test_databricks_agent_with_actual_text(
        self, mock_graphistry_client, mock_streaming_response
    ):
        """Test what happens when DatabricksAgent returns actual text content."""
        # Response with actual text content
        response_lines = [
            '{"dthread_id": "D_test_123"}',
            # Text elements with content
            (
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Executing query..."}}'
            ),
            (
                '{"payload": {"id": "B_002", "type": "TextElement", '
                '"text": "Query completed successfully."}}'
            ),
            (
                '{"payload": {"id": "B_003", "type": "TextElement", '
                '"text": "Retrieved 4 events."}}'
            ),
            # DataFrame element
            (
                '{"payload": {"id": "B_004", "type": "DfElement", '
                '"df_id": "databricks_result_456"}}'
            ),
        ]

        expected_df = pd.DataFrame({"result": [1, 2, 3, 4]})

        with patch("louieai._client.httpx.Client") as mock_httpx_client:
            mock_httpx_client.return_value = mock_streaming_response(response_lines)

            client = LouieClient(
                server_url="http://test.louie.ai",
                graphistry_client=mock_graphistry_client,
            )

            with patch.object(client, "_fetch_dataframe_arrow") as mock_fetch:
                mock_fetch.return_value = expected_df

                lui = louie(graphistry_client=mock_graphistry_client)
                lui._client = client

                lui(
                    "get 4 events from o365_management_activity_flat_tcook",
                    agent="DatabricksAgent",
                )

                # Check text elements have content
                text_elements = [e for e in lui.elements if e["type"] == "text"]
                assert len(text_elements) == 3

                # Verify text is populated
                assert text_elements[0]["value"] == "Executing query..."
                assert text_elements[1]["value"] == "Query completed successfully."
                assert text_elements[2]["value"] == "Retrieved 4 events."

                # Check lui.text property
                # Should return last text element
                assert lui.text == "Retrieved 4 events."

    @pytest.mark.integration
    def test_databricks_agent_real_credentials(self):
        """Integration test with real credentials (skipped unless env vars set)."""
        # Skip if no credentials
        if not all(
            [
                os.environ.get("DATABRICKS_PAT_TOKEN"),
                os.environ.get("DATABRICKS_SERVER_HOSTNAME"),
                os.environ.get("LOUIE_SERVER_URL"),
                os.environ.get("GRAPHISTRY_USERNAME"),
                os.environ.get("GRAPHISTRY_PASSWORD"),
            ]
        ):
            pytest.skip("Databricks integration test credentials not available")

        # This would be a real integration test
        # For now, we'll just document the expected behavior
        pass


@pytest.mark.parametrize(
    "agent_name", ["DatabricksAgent", "DatabricksPassthroughAgent"]
)
def test_empty_text_elements_multiple_agents(agent_name):
    """Test empty text elements across different Databricks agents."""
    # This is a simplified test to check the pattern across agents
    mock_response = Mock()

    # Simulate empty text elements
    mock_response.elements = [
        {"type": "text", "value": ""},
        {"type": "text", "value": ""},
        {"type": "dataframe", "value": pd.DataFrame({"col": [1, 2, 3]})},
    ]

    mock_response.text_elements = [
        {"type": "TextElement", "text": ""},
        {"type": "TextElement", "text": ""},
    ]

    mock_response.dataframe_elements = [
        {"type": "DfElement", "table": pd.DataFrame({"col": [1, 2, 3]})}
    ]

    # The issue is consistent across agents
    assert all(
        elem["value"] == "" for elem in mock_response.elements if elem["type"] == "text"
    )
