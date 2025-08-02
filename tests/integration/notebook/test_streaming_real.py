"""Real integration tests for streaming display functionality."""

import os
import sys
import time

import pytest

from louieai import louie

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils import load_test_credentials


@pytest.mark.integration
class TestStreamingRealIntegration:
    """Test streaming functionality with real API calls."""

    @pytest.fixture
    def lui(self):
        """Create louie interface with real credentials."""
        creds = load_test_credentials()
        if not creds:
            pytest.skip("Test credentials not available")

        import graphistry

        graphistry_client = graphistry.register(
            api=creds["api_version"],
            server=creds["server"],
            username=creds["username"],
            password=creds["password"],
        )

        # Create louie interface with real auth
        return louie(
            graphistry_client=graphistry_client, server_url="https://louie-dev.grph.xyz"
        )

    def test_streaming_provides_faster_first_response(self, lui):
        """Test that streaming shows content before the full response is ready."""
        # Note: This test requires being in a Jupyter environment to see streaming
        # In pytest, we can only verify the response arrives

        start_time = time.time()

        # Query that takes time to complete
        lui("Count from 1 to 10 slowly, explaining each number in detail.")

        total_time = time.time() - start_time

        # Verify we got a response
        assert lui.text is not None
        assert len(lui.text) > 100  # Should have detailed explanations

        print(f"\nResponse completed in {total_time:.1f}s")
        print(f"Response length: {len(lui.text)} chars")
        print(f"First 100 chars: {lui.text[:100]}...")

    def test_streaming_with_data_generation(self, lui):
        """Test streaming when generating dataframes."""
        start_time = time.time()

        # Query that generates data
        lui(
            "Create a sample dataset with 10 rows of sales data including "
            "date, product, quantity, and revenue."
        )

        total_time = time.time() - start_time

        # Check response
        assert lui.text is not None

        # May or may not have a dataframe depending on agent behavior
        if lui.df is not None:
            print(f"\nGot dataframe with shape: {lui.df.shape}")
            print(f"Columns: {list(lui.df.columns)}")
        else:
            print("\nNo dataframe returned (agent may have just described it)")

        print(f"Response time: {total_time:.1f}s")

    def test_multiple_queries_maintain_context(self, lui):
        """Test that streaming works across multiple queries in same thread."""
        # First query
        start1 = time.time()
        lui("Remember the number 42 as my favorite number.")
        time1 = time.time() - start1

        thread_id = lui.thread_id
        assert thread_id is not None

        # Second query - should remember context
        start2 = time.time()
        lui("What was my favorite number?")
        time2 = time.time() - start2

        # Should be same thread
        assert lui.thread_id == thread_id

        # Should remember the number
        assert "42" in lui.text

        print(f"\nFirst query: {time1:.1f}s")
        print(f"Second query: {time2:.1f}s")
        print(f"Thread maintained: {thread_id}")

    @pytest.mark.slow
    def test_long_streaming_response(self, lui):
        """Test streaming with a query that produces a long response."""
        start_time = time.time()

        # Query that produces lengthy output
        lui("""
        Write a detailed step-by-step guide for making chocolate chip cookies,
        including ingredient measurements, mixing instructions, baking tips,
        and troubleshooting common problems. Be very thorough.
        """)

        total_time = time.time() - start_time

        # Should have substantial response
        assert len(lui.text) > 500

        print(f"\nLong response completed in {total_time:.1f}s")
        print(f"Response length: {len(lui.text)} chars")

        # In a real Jupyter environment, this would have shown
        # progressive updates during these seconds
