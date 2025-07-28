"""Integration tests with real Louie instance.

These tests require credentials to be set in environment variables.
They will be skipped if credentials are not available.
"""

import pytest

from louieai import LouieClient

from ..utils import load_test_credentials


class TestRealLouieIntegration:
    """Integration tests that connect to a real Louie instance."""

    @pytest.fixture
    def client(self):
        """Create a Louie client with test credentials."""
        creds = load_test_credentials()
        if not creds:
            pytest.skip("Test credentials not available")

        # Initialize graphistry connection
        import graphistry

        graphistry.register(
            api=creds["api_version"],
            server=creds["server"],
            username=creds["username"],
            password=creds["password"],
        )

        # Create Louie client
        # Use louie-dev.grph.xyz as mentioned in credentials
        return LouieClient(server_url="https://louie-dev.grph.xyz")

    def test_basic_query(self, client):
        """Test a simple query to verify connection."""
        # Test with new thread-based API
        client.create_thread(name="Integration Test")
        response = client.add_cell("", "Return the text 'Hello from Louie!'")

        # Check response
        assert response is not None
        assert hasattr(response, "type")
        assert hasattr(response, "thread_id")
        print(f"Response type: {response.type}")
        print(f"Thread ID: {response.thread_id}")
        if hasattr(response, "text") and response.text:
            print(f"Text: {response.text[:100]}")
        # Verify we got a valid thread ID
        assert response.thread_id.startswith("D_")

    def test_data_query(self, client):
        """Test a data query if test database is available."""
        # Create thread with initial data generation
        thread = client.create_thread(
            name="Data Query Test",
            initial_prompt="Create a sample DataFrame with 5 rows of test data",
        )

        # Thread should have an ID now
        assert thread.id
        assert thread.id.startswith("D_")

        # Check if we can query the data
        response = client.add_cell(thread.id, "How many rows are in the data?")

        # Should get a response about the data
        assert response is not None
        assert hasattr(response, "type")

    def test_multi_step_workflow(self, client):
        """Test a multi-step workflow."""
        # Create thread with initial data
        thread = client.create_thread(
            name="Workflow Test",
            initial_prompt=(
                "Generate a sample dataset with 10 rows "
                "including columns: id, value, category"
            ),
        )

        # Verify thread was created
        assert thread.id

        # Step 2: Analyze the data in same thread
        response2 = client.add_cell(thread.id, "Summarize the data you just created")

        # Verify we got response and it's in same thread
        assert response2 is not None
        assert response2.thread_id == thread.id

    def test_error_handling(self, client):
        """Test error handling with invalid query."""
        # Try to query non-existent data
        response = client.add_cell(
            "",  # New thread
            "Query a non_existent_database.non_existent_table",
        )

        # Check response (errors typically come as TextElement)
        assert response is not None
        assert hasattr(response, "type")
        # In actual API, errors often come as helpful text responses
        if response.type == "TextElement":
            assert hasattr(response, "text")
            print(f"Error response: {response.text[:200]}")
