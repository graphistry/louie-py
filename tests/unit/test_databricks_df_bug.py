"""Test for Databricks DataFrame None bug fix."""

import logging
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from louieai._client import LouieClient

# Set up logger for the test
logger = logging.getLogger(__name__)


class TestDatabricksDataFrameBug:
    """Test that Databricks DfElements properly fetch DataFrames."""

    @pytest.fixture
    def mock_graphistry_client(self):
        """Mock GraphistryClient instance."""
        mock = Mock()
        mock.api_token = Mock(return_value="fake-token-123")
        mock.register = Mock()
        mock.refresh = Mock()
        return mock

    @pytest.fixture
    def client(self, mock_graphistry_client):
        """Create test client."""
        return LouieClient(
            server_url="http://test.louie.ai", graphistry_client=mock_graphistry_client
        )

    def _mock_streaming_response(self, response_lines):
        """Helper to create a mock streaming response context."""
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

    def test_databricks_df_element_standard_format(self, client):
        """Test DfElement with standard df_id field."""
        # Mock the streaming response
        response_lines = [
            '{"dthread_id": "D_databricks_123"}',
            '{"payload": {"id": "B_001", "type": "DfElement", '
            '"df_id": "databricks_result_456"}}',
            '{"payload": {"id": "B_002", "type": "TextElement", '
            '"text": "Query completed"}}',
        ]

        # Mock DataFrame that would be fetched
        expected_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

        # Patch httpx.Client at the module level where it's imported
        with patch("louieai._client.httpx.Client") as mock_httpx_client:
            mock_httpx_client.return_value = self._mock_streaming_response(
                response_lines
            )

            with patch.object(client, "_fetch_dataframe_arrow") as mock_fetch:
                # Mock successful DataFrame fetch
                mock_fetch.return_value = expected_df

                # Make the query
                response = client.add_cell(
                    thread_id="",
                    prompt="SELECT * FROM table",
                    agent="DatabricksPassthroughAgent",
                )

                # Verify fetch was called with correct params
                mock_fetch.assert_called_once_with(
                    "D_databricks_123", "databricks_result_456"
                )

                # Check response has DataFrame
                assert len(response.dataframe_elements) == 1
                df_elem = response.dataframe_elements[0]
                assert "table" in df_elem
                pd.testing.assert_frame_equal(df_elem["table"], expected_df)

    def test_databricks_df_element_nested_data(self, client):
        """Test DfElement with df_id nested in data field."""
        # Mock response with nested data structure
        response_lines = [
            '{"dthread_id": "D_databricks_123"}',
            '{"payload": {"id": "B_001", "type": "DfElement", '
            '"data": {"df_id": "nested_df_456"}}}',
        ]

        expected_df = pd.DataFrame({"value": [10, 20, 30]})

        with patch("louieai._client.httpx.Client") as mock_httpx_client:
            mock_httpx_client.return_value = self._mock_streaming_response(
                response_lines
            )

            with patch.object(client, "_fetch_dataframe_arrow") as mock_fetch:
                mock_fetch.return_value = expected_df

                response = client.add_cell(
                    thread_id="",
                    prompt="SELECT * FROM table",
                    agent="DatabricksPassthroughAgent",
                )

                # Should extract df_id from nested data
                mock_fetch.assert_called_once_with("D_databricks_123", "nested_df_456")

                # Check DataFrame was attached
                df_elem = response.dataframe_elements[0]
                assert "table" in df_elem

    def test_databricks_df_element_fallback_to_id(self, client):
        """Test DfElement that only has element ID."""
        response_lines = [
            '{"dthread_id": "D_databricks_123"}',
            '{"payload": {"id": "B_001", "type": "DfElement"}}',
        ]

        expected_df = pd.DataFrame({"result": ["data"]})

        with patch("louieai._client.httpx.Client") as mock_httpx_client:
            mock_httpx_client.return_value = self._mock_streaming_response(
                response_lines
            )

            with patch.object(client, "_fetch_dataframe_arrow") as mock_fetch:
                mock_fetch.return_value = expected_df

                client.add_cell(
                    thread_id="",
                    prompt="SELECT * FROM table",
                    agent="DatabricksPassthroughAgent",
                )

                # Should fall back to element ID
                mock_fetch.assert_called_once_with("D_databricks_123", "B_001")

    def test_databricks_df_fetch_failure_warning(self, client):
        """Test warning when DataFrame fetch fails."""
        response_lines = [
            '{"dthread_id": "D_databricks_123"}',
            '{"payload": {"id": "B_001", "type": "DfElement", "df_id": "fail_456"}}',
        ]

        with patch("louieai._client.httpx.Client") as mock_httpx_client:
            mock_httpx_client.return_value = self._mock_streaming_response(
                response_lines
            )

            with patch.object(client, "_fetch_dataframe_arrow") as mock_fetch:
                # Mock fetch failure
                mock_fetch.return_value = None

                # Use mock logger to capture warnings
                with patch("louieai._client.logger") as mock_logger:
                    response = client.add_cell(
                        thread_id="",
                        prompt="SELECT * FROM table",
                        agent="DatabricksPassthroughAgent",
                    )

                    # Check logger.warning was called
                    mock_logger.warning.assert_called_once()
                    warning_msg = mock_logger.warning.call_args[0][0]
                    assert "Failed to fetch dataframe fail_456" in warning_msg

                # DataFrame element should exist but no table
                assert len(response.dataframe_elements) == 1
                df_elem = response.dataframe_elements[0]
                assert "table" not in df_elem
