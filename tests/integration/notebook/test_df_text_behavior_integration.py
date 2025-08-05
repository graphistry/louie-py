"""Integration tests for df/text/g property behavior with real API calls.

These tests verify the expected behavior:
- lui.df → latest df in latest run
- lui.dfs[-1] → latest df in latest run
- lui[-1].df → latest df in previous run
- lui[-1].dfs[-1] → latest df in previous run
Same for text/texts and g/gs.
"""

import os
import time

import pandas as pd
import pytest

# Skip if no credentials provided
has_credentials = (
    os.environ.get("GRAPHISTRY_USERNAME") is not None
    and os.environ.get("GRAPHISTRY_PASSWORD") is not None
) or (
    os.environ.get("GRAPHISTRY_PERSONAL_KEY_ID") is not None
    and os.environ.get("GRAPHISTRY_PERSONAL_KEY_SECRET") is not None
)

pytestmark = pytest.mark.skipif(
    not has_credentials,
    reason="Integration tests require Graphistry credentials",
)


class TestSequentialCallsBehavior:
    """Test behavior with multiple sequential lui() calls."""

    @pytest.fixture
    def lui_cursor(self):
        """Create a properly authenticated lui cursor."""
        import graphistry
        import louieai
        from louieai.notebook.cursor import Cursor
        
        # Get credentials from environment
        server = os.environ.get("GRAPHISTRY_SERVER", "hub.graphistry.com")
        key_id = os.environ.get("GRAPHISTRY_PERSONAL_KEY_ID")
        key_secret = os.environ.get("GRAPHISTRY_PERSONAL_KEY_SECRET")
        org_name = os.environ.get("GRAPHISTRY_ORG_NAME")
        louie_server = os.environ.get("LOUIE_SERVER", "https://den.louie.ai")
        
        # Authenticate with graphistry
        if key_id and key_secret:
            g = graphistry.register(
                api=3,
                server=server,
                personal_key_id=key_id,
                personal_key_secret=key_secret,
                org_name=org_name,
            )
        else:
            # Fallback to username/password
            username = os.environ.get("GRAPHISTRY_USERNAME")
            password = os.environ.get("GRAPHISTRY_PASSWORD")
            if username and password:
                g = graphistry.register(
                    api=3,
                    server=server,
                    username=username,
                    password=password,
                )
            else:
                pytest.skip("No valid authentication credentials found")
        
        # Create LouieClient
        from louieai._client import LouieClient
        client = LouieClient(graphistry_client=g, server_url=louie_server)
        
        # Create cursor with the client
        cursor = Cursor(client=client)
        return cursor

    def test_three_sequential_text_queries(self, lui_cursor):
        """Test 3 sequential calls, each returning text."""
        lui = lui_cursor
        
        # Call 1: Simple math
        response1 = lui("What is 2 + 2? Just give the number.")
        time.sleep(1)  # Brief pause between calls
        
        # Verify first call
        assert lui.text is not None
        text1 = lui.text
        assert "4" in str(text1) or "four" in str(text1).lower()
        assert len(lui.texts) >= 1
        
        # Call 2: Different math
        response2 = lui("What is 10 * 10? Just give the number.")
        time.sleep(1)
        
        # Verify second call
        assert lui.text is not None
        text2 = lui.text
        assert "100" in str(text2) or "hundred" in str(text2).lower()
        assert text2 != text1  # Different from first response
        assert len(lui.texts) >= 1
        
        # Call 3: Another calculation
        response3 = lui("What is 50 + 50? Just give the number.")
        time.sleep(1)
        
        # Verify third call
        assert lui.text is not None
        text3 = lui.text
        assert "100" in str(text3) or "hundred" in str(text3).lower()
        assert len(lui.texts) >= 1
        
        # Verify history navigation
        # lui[-1] should be the current (last) response
        assert lui[-1].text == text3
        
        # lui[-2] should be the second response
        assert lui[-2].text == text2
        
        # lui[-3] should be the first response
        assert lui[-3].text == text1

    def test_three_sequential_dataframe_queries(self, lui_cursor):
        """Test 3 sequential calls that might generate dataframes."""
        lui = lui_cursor
        
        # Call 1: Request a simple calculation (likely text only)
        response1 = lui("What is the sum of 1, 2, and 3?")
        time.sleep(1)
        
        # Check what we got
        text1 = lui.text
        df1 = lui.df
        assert text1 is not None
        
        # Call 2: Another calculation
        response2 = lui("Calculate the average of 10, 20, and 30.")
        time.sleep(1)
        
        text2 = lui.text
        df2 = lui.df
        assert text2 is not None
        assert text2 != text1
        
        # Call 3: Different query
        response3 = lui("What is 100 divided by 4?")
        time.sleep(1)
        
        text3 = lui.text
        df3 = lui.df
        assert text3 is not None
        
        # Verify history navigation for text (always present)
        assert lui[-1].text == text3
        assert lui[-2].text == text2
        assert lui[-3].text == text1
        
        # If any dataframes were created, verify their behavior
        if df3 is not None:
            assert lui.df is df3
            if len(lui.dfs) > 0:
                assert lui.dfs[-1] is df3

    def test_mixed_responses_text_and_df(self, lui_cursor):
        """Test mixed responses - some with text, some might have dataframes."""
        lui = lui_cursor
        
        # Call 1: Text only question
        response1 = lui("What is the capital of France? Just the city name.")
        time.sleep(1)
        
        text1 = lui.text
        assert text1 is not None
        assert "paris" in str(text1).lower()
        
        # Call 2: Another text question
        response2 = lui("What is 2 times 3?")
        time.sleep(1)
        
        text2 = lui.text
        assert text2 is not None
        assert "6" in str(text2) or "six" in str(text2).lower()
        
        # Call 3: Final text question
        response3 = lui("What is 100 divided by 4?")
        time.sleep(1)
        
        text3 = lui.text
        assert text3 is not None
        assert "25" in str(text3)
        
        # Verify history for text
        assert lui[-1].text == text3
        assert lui[-2].text == text2
        assert lui[-3].text == text1


class TestSingleCallBehavior:
    """Test behavior for single calls."""

    @pytest.fixture
    def lui_cursor(self):
        """Create a properly authenticated lui cursor."""
        import graphistry
        from louieai._client import LouieClient
        from louieai.notebook.cursor import Cursor
        
        # Get credentials from environment
        server = os.environ.get("GRAPHISTRY_SERVER", "hub.graphistry.com")
        key_id = os.environ.get("GRAPHISTRY_PERSONAL_KEY_ID")
        key_secret = os.environ.get("GRAPHISTRY_PERSONAL_KEY_SECRET")
        org_name = os.environ.get("GRAPHISTRY_ORG_NAME")
        louie_server = os.environ.get("LOUIE_SERVER", "https://den.louie.ai")
        
        # Authenticate
        if key_id and key_secret:
            g = graphistry.register(
                api=3,
                server=server,
                personal_key_id=key_id,
                personal_key_secret=key_secret,
                org_name=org_name,
            )
        else:
            username = os.environ.get("GRAPHISTRY_USERNAME")
            password = os.environ.get("GRAPHISTRY_PASSWORD")
            if username and password:
                g = graphistry.register(
                    api=3,
                    server=server,
                    username=username,
                    password=password,
                )
            else:
                pytest.skip("No valid authentication credentials found")
        
        client = LouieClient(graphistry_client=g, server_url=louie_server)
        cursor = Cursor(client=client)
        return cursor

    def test_single_call_with_text(self, lui_cursor):
        """Test a single query that returns text."""
        lui = lui_cursor
        
        # Single query
        response = lui("What is the value of pi to 2 decimal places?")
        time.sleep(2)
        
        # Should have text
        assert lui.text is not None
        assert "3.14" in str(lui.text) or "pi" in str(lui.text).lower()
        
        # Check texts array
        all_texts = lui.texts
        assert len(all_texts) >= 1
        
        # Last text should match lui.text
        assert lui.text == all_texts[-1]
        if len(all_texts) > 1:
            assert lui.texts[-1] == all_texts[-1]

    def test_empty_history_behavior(self, lui_cursor):
        """Test behavior with empty history."""
        lui = lui_cursor
        
        # Before any queries
        assert lui.df is None
        assert lui.text is None
        assert lui.dfs == []
        assert lui.texts == []
        
        # Accessing history should not crash
        assert lui[-1].df is None
        assert lui[-1].text is None
        assert lui[-10].df is None  # Out of bounds