"""Integration tests with real Louie instance.

These tests require credentials to be set in environment variables.
They will be skipped if credentials are not available.
"""

import pytest

from louieai._client import LouieClient

from ..utils import load_test_credentials


class TestRealLouieIntegration:
    """Integration tests that connect to a real Louie instance."""

    @pytest.fixture
    def client(self):
        """Create a Louie client with test credentials."""
        creds = load_test_credentials()
        if not creds:
            pytest.skip("Test credentials not available")

        # Create GraphistryClient and register credentials
        import graphistry

        graphistry_client = graphistry.register(
            api=creds["api_version"],
            server=creds["server"],
            username=creds["username"],
            password=creds["password"],
        )

        # Create Louie client with graphistry client
        # Use louie-dev.grph.xyz as mentioned in credentials
        return LouieClient(
            server_url="https://louie-dev.grph.xyz", graphistry_client=graphistry_client
        )

    def test_basic_query(self, client):
        """Test a simple query to verify connection."""
        # Test with new thread-based API
        import time

        print("\n=== Starting basic query test ===")
        print(f"Server URL: {client.server_url}")
        print(f"Auth token available: {bool(client._auth_manager.get_token())}")
        print(f"Token preview: {client._auth_manager.get_token()[:30]}...")

        # Create thread first
        print("\nCreating thread...")
        start_time = time.time()
        try:
            thread = client.create_thread(name="Integration Test")
            print(f"Thread created in {time.time() - start_time:.2f}s")
            print(f"Thread ID: {thread.id if hasattr(thread, 'id') else 'No ID'}")
        except Exception as e:
            print(f"Failed to create thread: {e}")
            raise

        # Now add a cell with a simple query
        print("\nSending query...")
        start_time = time.time()
        try:
            response = client.add_cell("", "Return the text 'Hello from Louie!'")
            print(f"Query completed in {time.time() - start_time:.2f}s")
        except Exception as e:
            print(f"Query failed after {time.time() - start_time:.2f}s")
            print(f"Error type: {type(e).__name__}")
            print(f"Error: {e}")
            raise

        # Check response
        assert response is not None
        assert hasattr(response, "thread_id")
        assert hasattr(response, "elements")
        print(f"\nResponse Thread ID: {response.thread_id}")
        print(f"Elements: {len(response.elements)}")
        if response.text_elements:
            print(f"Text elements: {len(response.text_elements)}")
            for i, elem in enumerate(response.text_elements[:2]):
                text = elem.get("content", elem.get("text", ""))[:100]
                print(f"  Text {i}: {text}...")
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
        assert hasattr(response, "thread_id")
        assert hasattr(response, "elements")

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
        assert hasattr(response, "thread_id")
        assert hasattr(response, "elements")
        # In actual API, errors often come as helpful text responses
        if response.text_elements:
            text_elem = response.text_elements[0]
            assert "text" in text_elem
            print(f"Error response: {text_elem['text'][:200]}")
