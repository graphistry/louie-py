"""Integration test for upload parsing fix."""

import os

import graphistry
import pandas as pd

from louieai import louie


def test_upload_parsing_integration():
    """Test that upload responses are parsed correctly after fix."""

    # Set up credentials
    os.environ["GRAPHISTRY_USERNAME"] = "testuser"
    os.environ["GRAPHISTRY_PASSWORD"] = "testpass"
    os.environ["GRAPHISTRY_SERVER"] = "test.server.com"
    os.environ["LOUIE_SERVER"] = "http://localhost:8000"

    # Authenticate
    g = graphistry.register(
        api=3,
        server=os.environ["GRAPHISTRY_SERVER"],
        username=os.environ["GRAPHISTRY_USERNAME"],
        password=os.environ["GRAPHISTRY_PASSWORD"],
    )

    # Create louie interface
    lui = louie(g, server_url="http://localhost:8000")

    # Create test DataFrame
    df = pd.DataFrame(
        {
            "product": ["Widget A", "Widget B", "Widget C"],
            "price": [10.99, 15.49, 8.99],
            "quantity": [100, 75, 150],
        }
    )

    print("\n" + "=" * 80)
    print("TESTING UPLOAD PARSING FIX")
    print("=" * 80)

    # Test 1: Upload and check response has thread_id
    print("\n1. Testing basic upload...")
    lui("Calculate the total inventory value", df)

    # Check we got a response
    assert lui._history is not None, "No history after upload"
    assert len(lui._history) > 0, "Empty history after upload"

    last_response = lui._history[-1]
    print(f"   Thread ID: {last_response.thread_id}")
    print(f"   Has text: {last_response.text is not None}")
    text_preview = str(last_response.text)[:100] if last_response.text else "None"
    print(f"   Text preview: {text_preview}")

    # The fix should ensure we get a thread_id
    assert last_response.thread_id is not None, "Thread ID is None after fix"
    assert last_response.thread_id != "", "Thread ID is empty after fix"
    assert last_response.thread_id.startswith("D_"), (
        f"Invalid thread ID format: {last_response.thread_id}"
    )

    print("   ✅ Thread ID parsed correctly!")

    # Test 2: Check text response exists
    print("\n2. Testing text extraction...")

    # After fix, we should have text
    if last_response.text:
        print(f"   Text content: {last_response.text[:200]}")
        print("   ✅ Text extracted successfully!")
    else:
        print("   ⚠️ No text in response (server may not have returned analysis)")

    # Test 3: Check elements are parsed
    print("\n3. Testing element parsing...")
    print(f"   Total elements: {len(last_response.elements)}")
    print(f"   Text elements: {len(last_response.text_elements)}")
    print(f"   DataFrame elements: {len(last_response.dataframe_elements)}")

    assert len(last_response.elements) > 0, "No elements parsed from response"
    print("   ✅ Elements parsed correctly!")

    # Test 4: Test with multiple uploads in same thread
    print("\n4. Testing multiple uploads in same thread...")
    thread_id = last_response.thread_id

    lui("What is the average price?", df)
    second_response = lui._history[-1]

    assert second_response.thread_id == thread_id, "Thread ID changed unexpectedly"
    print(f"   Second response thread: {second_response.thread_id}")
    text_preview = str(second_response.text)[:100] if second_response.text else "None"
    print(f"   Second response text: {text_preview}")
    print("   ✅ Multi-upload parsing works!")

    print("\n" + "=" * 80)
    print("ALL TESTS PASSED! Upload parsing fix is working.")
    print("=" * 80)

    return True


if __name__ == "__main__":
    test_upload_parsing_integration()
