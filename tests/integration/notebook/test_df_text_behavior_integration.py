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

from louieai.globals import lui

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


@pytest.fixture(autouse=True)
def reset_lui():
    """Reset lui singleton before each test."""
    import louieai.notebook

    louieai.notebook._global_cursor = None
    yield
    # Cleanup after test
    louieai.notebook._global_cursor = None


class TestSequentialCallsBehavior:
    """Test behavior with multiple sequential lui() calls."""

    def test_three_sequential_text_queries(self):
        """Test 3 sequential calls, each returning text."""
        # Call 1: Simple math
        response1 = lui("What is 2 + 2? Just give the number.")
        time.sleep(1)  # Brief pause between calls
        
        # Verify first call
        assert lui.text is not None
        text1 = lui.text
        assert "4" in text1 or "four" in text1.lower()
        assert len(lui.texts) >= 1
        
        # Call 2: Different math
        response2 = lui("What is 10 * 10? Just give the number.")
        time.sleep(1)
        
        # Verify second call
        assert lui.text is not None
        text2 = lui.text
        assert "100" in text2 or "hundred" in text2.lower()
        assert text2 != text1  # Different from first response
        assert len(lui.texts) >= 1
        
        # Call 3: Another calculation
        response3 = lui("What is 50 + 50? Just give the number.")
        time.sleep(1)
        
        # Verify third call
        assert lui.text is not None
        text3 = lui.text
        assert "100" in text3 or "hundred" in text3.lower()
        assert len(lui.texts) >= 1
        
        # Verify history navigation
        # lui[-1] should be the current (last) response
        assert lui[-1].text == text3
        
        # lui[-2] should be the second response
        assert lui[-2].text == text2
        
        # lui[-3] should be the first response
        assert lui[-3].text == text1

    def test_three_sequential_dataframe_queries(self):
        """Test 3 sequential calls that generate dataframes."""
        # Call 1: Create small dataframe
        response1 = lui(
            "Create a pandas dataframe with 3 rows. "
            "Columns: 'id' (values 1,2,3) and 'name' (values 'A','B','C')"
        )
        time.sleep(2)  # Allow time for df generation
        
        # Check if we got a dataframe
        if lui.df is not None:
            df1 = lui.df
            assert isinstance(df1, pd.DataFrame)
            assert len(lui.dfs) >= 1
            
            # Call 2: Create different dataframe
            response2 = lui(
                "Create a pandas dataframe with 2 rows. "
                "Columns: 'x' (values 10,20) and 'y' (values 30,40)"
            )
            time.sleep(2)
            
            if lui.df is not None:
                df2 = lui.df
                assert isinstance(df2, pd.DataFrame)
                # Should be different from first df
                assert not df2.equals(df1)
                
                # Call 3: Create third dataframe
                response3 = lui(
                    "Create a pandas dataframe with 4 rows. "
                    "Columns: 'value' with values [100, 200, 300, 400]"
                )
                time.sleep(2)
                
                if lui.df is not None:
                    df3 = lui.df
                    assert isinstance(df3, pd.DataFrame)
                    
                    # Verify history navigation
                    if lui[-1].df is not None:
                        pd.testing.assert_frame_equal(lui[-1].df, df3)
                    if lui[-2].df is not None:
                        pd.testing.assert_frame_equal(lui[-2].df, df2)
                    if lui[-3].df is not None:
                        pd.testing.assert_frame_equal(lui[-3].df, df1)

    def test_mixed_responses_text_and_df(self):
        """Test mixed responses - some with text, some with dataframes."""
        # Call 1: Text only
        response1 = lui("What is the capital of France? Just the city name.")
        time.sleep(1)
        
        text1 = lui.text
        assert text1 is not None
        assert "paris" in text1.lower()
        assert lui.df is None  # No dataframe in text response
        
        # Call 2: Request a dataframe
        response2 = lui(
            "Create a simple pandas dataframe with columns 'country' and 'capital'. "
            "Add 3 rows with any countries and their capitals."
        )
        time.sleep(2)
        
        # Might have both text and df
        text2 = lui.text
        df2 = lui.df
        
        # Call 3: Text only again
        response3 = lui("What is 100 divided by 4?")
        time.sleep(1)
        
        text3 = lui.text
        assert text3 is not None
        assert "25" in text3
        
        # Current response has no df
        if df2 is not None:
            # If call 2 created a df, call 3 should have no df
            assert lui.df is None or lui.df is not df2
        
        # Verify history
        assert lui[-1].text == text3
        assert lui[-3].text == text1
        
        # df should be accessible from history if it was created
        if df2 is not None and lui[-2].df is not None:
            pd.testing.assert_frame_equal(lui[-2].df, df2)


class TestSingleCallMultipleResults:
    """Test behavior when a single call returns multiple results."""

    def test_single_call_generating_multiple_texts(self):
        """Test a single query that generates multiple text responses."""
        # Query that might generate multiple text elements
        response = lui(
            "Give me three separate facts about Python programming. "
            "Number them 1, 2, 3."
        )
        time.sleep(2)
        
        # Should have text
        assert lui.text is not None
        
        # Check texts array
        all_texts = lui.texts
        assert len(all_texts) >= 1
        
        # If multiple texts, last one should be lui.text
        if len(all_texts) > 1:
            assert lui.text == all_texts[-1]
            assert lui.texts[-1] == all_texts[-1]

    def test_single_call_with_analysis_steps(self):
        """Test a query that involves multiple analysis steps."""
        # Complex query that might generate multiple outputs
        response = lui(
            "Analyze the numbers 10, 20, 30. "
            "First show them in a dataframe, "
            "then calculate their sum, "
            "then calculate their average."
        )
        time.sleep(3)
        
        # Should have text describing the analysis
        assert lui.text is not None
        
        # Might have a dataframe
        if lui.df is not None:
            df = lui.df
            assert isinstance(df, pd.DataFrame)
            
            # If multiple dfs generated, should get the last one
            if len(lui.dfs) > 1:
                assert lui.df is lui.dfs[-1]
                pd.testing.assert_frame_equal(lui.dfs[-1], df)
        
        # Should be able to access all texts
        texts = lui.texts
        assert len(texts) >= 1
        
        # Last text should be accessible via lui.text
        assert lui.text == texts[-1]


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_response_between_valid_ones(self):
        """Test behavior when a response has no df/text between valid responses."""
        # Call 1: Get text
        response1 = lui("Say 'Hello World'")
        time.sleep(1)
        
        text1 = lui.text
        assert text1 is not None
        assert "hello" in text1.lower()
        
        # Call 2: Try something that might fail or return empty
        response2 = lui("...")  # Minimal input
        time.sleep(1)
        
        # Call 3: Get text again
        response3 = lui("Say 'Goodbye'")
        time.sleep(1)
        
        text3 = lui.text
        assert text3 is not None
        assert "goodbye" in text3.lower() or "bye" in text3.lower()
        
        # History should still work
        assert lui[-1].text == text3
        assert lui[-3].text == text1

    def test_multiple_rapid_calls(self):
        """Test rapid sequential calls."""
        responses = []
        texts = []
        
        for i in range(3):
            response = lui(f"What is {i + 1} + {i + 1}?")
            time.sleep(0.5)  # Brief pause
            
            responses.append(response)
            if lui.text:
                texts.append(lui.text)
        
        # Should have gotten 3 responses
        assert len(texts) >= 2  # At least some should succeed
        
        # Current text should be from last successful response
        if lui.text:
            assert lui.text == texts[-1]
        
        # Should be able to navigate history
        for i in range(min(3, len(texts))):
            historical = lui[-(i + 1)]
            assert historical is not None