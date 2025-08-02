#!/usr/bin/env python3
"""Debug script for notebook streaming and dataframe display issues."""

import sys
import time
import pandas as pd
from unittest.mock import Mock, patch

# Check if we're in a Jupyter environment
def check_jupyter():
    """Check if we're running in Jupyter."""
    print("=== Jupyter Environment Check ===")
    if 'IPython' in sys.modules:
        print("✓ IPython is imported")
        try:
            from IPython import get_ipython
            ipython = get_ipython()
            if ipython is not None:
                print(f"✓ IPython kernel: {type(ipython).__name__}")
                if hasattr(ipython, 'config'):
                    print(f"✓ IPython config available")
            else:
                print("✗ IPython kernel is None (not in notebook)")
        except Exception as e:
            print(f"✗ Error getting IPython: {e}")
    else:
        print("✗ IPython not in sys.modules")
    print()


def test_display_methods():
    """Test IPython display methods."""
    print("=== Display Method Tests ===")
    try:
        from IPython.display import display, HTML, Markdown
        print("✓ IPython.display imports successful")
        
        # Test HTML display
        try:
            display(HTML("<b>Test HTML</b>"))
            print("✓ HTML display works")
        except Exception as e:
            print(f"✗ HTML display error: {e}")
        
        # Test Markdown display
        try:
            display(Markdown("**Test Markdown**"))
            print("✓ Markdown display works")
        except Exception as e:
            print(f"✗ Markdown display error: {e}")
            
    except ImportError as e:
        print(f"✗ Cannot import IPython.display: {e}")
    print()


def test_cursor_display():
    """Test the cursor's display logic."""
    print("=== Cursor Display Test ===")
    
    # Import cursor and create mock response
    from louieai.notebook.cursor import Cursor, _render_response_html
    from louieai._client import Response
    
    # Create a mock response with text and dataframe
    mock_elements = [
        {"type": "TextElement", "id": "1", "text": "Here's your data analysis:"},
        {"type": "DfElement", "id": "2", "table": pd.DataFrame({
            "user": ["alice", "bob", "charlie"],
            "score": [95, 87, 92]
        })}
    ]
    
    mock_response = Response(thread_id="test_123", elements=mock_elements)
    
    # Test the render function
    print("Testing _render_response_html...")
    html_output = _render_response_html(mock_response)
    print(f"HTML output length: {len(html_output)} chars")
    print(f"Contains text: {'Here\\'s your data' in html_output}")
    print(f"Contains dataframe HTML: {'<table' in html_output}")
    print()
    
    # Test cursor display method
    print("Testing cursor._display method...")
    cursor = Cursor()
    
    # Mock the IPython display
    with patch('louieai.notebook.cursor.display') as mock_display:
        cursor._display(mock_response)
        if mock_display.called:
            print("✓ display() was called")
            print(f"  Called {mock_display.call_count} time(s)")
            if mock_display.call_args:
                args = mock_display.call_args[0]
                if args:
                    print(f"  First argument type: {type(args[0])}")
        else:
            print("✗ display() was NOT called")
    print()


def test_streaming_response():
    """Test streaming response handling."""
    print("=== Streaming Response Test ===")
    
    from louieai._client import LouieClient
    
    # Create a mock streaming response
    mock_lines = [
        '{"dthread_id": "D_test123"}',
        '{"payload": {"id": "B_001", "type": "TextElement", "text": "Starting analysis..."}}',
        '{"payload": {"id": "B_001", "type": "TextElement", "text": "Starting analysis...\\nProcessing data..."}}',
        '{"payload": {"id": "B_002", "type": "DfElement", "table": {"columns": ["a", "b"], "data": [[1, 2], [3, 4]]}}}'
    ]
    
    client = LouieClient()
    
    # Test parsing
    response_text = "\n".join(mock_lines)
    result = client._parse_jsonl_response(response_text)
    
    print(f"Thread ID: {result['dthread_id']}")
    print(f"Number of elements: {len(result['elements'])}")
    for i, elem in enumerate(result['elements']):
        print(f"  Element {i}: type={elem.get('type')}, id={elem.get('id')}")
    print()


def test_dataframe_access():
    """Test dataframe property access."""
    print("=== DataFrame Access Test ===")
    
    from louieai.notebook.cursor import Cursor, ResponseProxy
    from louieai._client import Response
    
    # Create response with dataframe
    df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    elements = [
        {"type": "TextElement", "text": "Here's your dataframe:"},
        {"type": "DfElement", "table": df}
    ]
    response = Response(thread_id="test", elements=elements)
    
    # Test ResponseProxy
    proxy = ResponseProxy(response)
    print(f"proxy.df type: {type(proxy.df)}")
    print(f"proxy.df is DataFrame: {isinstance(proxy.df, pd.DataFrame)}")
    print(f"proxy.dfs length: {len(proxy.dfs)}")
    print(f"proxy.text: '{proxy.text}'")
    print(f"proxy.texts: {proxy.texts}")
    
    # Test cursor with history
    cursor = Cursor()
    cursor._history.append(response)
    
    print(f"\ncursor.df type: {type(cursor.df)}")
    print(f"cursor.df is DataFrame: {isinstance(cursor.df, pd.DataFrame)}")
    if cursor.df is not None:
        print(f"cursor.df shape: {cursor.df.shape}")
        print(f"cursor.df columns: {list(cursor.df.columns)}")
    print()


def test_in_notebook_detection():
    """Test the _in_jupyter detection."""
    print("=== Notebook Detection Test ===")
    
    from louieai.notebook.cursor import Cursor
    
    cursor = Cursor()
    in_jupyter = cursor._in_jupyter()
    print(f"cursor._in_jupyter(): {in_jupyter}")
    print(f"'IPython' in sys.modules: {'IPython' in sys.modules}")
    
    # Test with mock
    with patch.object(sys, 'modules', {'IPython': Mock()}):
        cursor2 = Cursor()
        print(f"With mocked IPython: {cursor2._in_jupyter()}")
    print()


if __name__ == "__main__":
    print("LouieAI Notebook Debug Script")
    print("=" * 50)
    print()
    
    check_jupyter()
    test_display_methods()
    test_cursor_display()
    test_streaming_response()
    test_dataframe_access()
    test_in_notebook_detection()
    
    print("\nTo test in a real notebook:")
    print("1. Run this in a Jupyter notebook cell")
    print("2. Check if display outputs appear")
    print("3. Try a real query and check lui.df")