#!/usr/bin/env python3
"""Test notebook streaming functionality."""

import os
import time

# Set up test credentials
os.environ['GRAPHISTRY_USERNAME'] = 'leotest2'
os.environ['GRAPHISTRY_PASSWORD'] = 'accountaccount'
os.environ['GRAPHISTRY_SERVER'] = 'graphistry-dev.grph.xyz'
os.environ['LOUIE_URL'] = 'https://louie-dev.grph.xyz'

from louieai import louie


def test_notebook_streaming():
    """Test streaming in notebook API."""
    print("Testing notebook API with streaming...")
    print("="*60)
    
    # Create notebook interface
    lui = louie()
    
    # Simulate being in Jupyter
    import sys
    from unittest.mock import MagicMock
    
    # Mock IPython
    mock_ipython = MagicMock()
    mock_display = MagicMock()
    mock_html = MagicMock()
    mock_update = MagicMock()
    mock_clear = MagicMock()
    
    sys.modules['IPython'] = mock_ipython
    sys.modules['IPython.display'] = MagicMock(
        display=mock_display,
        HTML=mock_html,
        update_display=mock_update,
        clear_output=mock_clear
    )
    
    # Force reload to pick up mocked IPython
    import importlib
    import louieai.notebook.streaming
    importlib.reload(louieai.notebook.streaming)
    
    start_time = time.time()
    print("\nExecuting query with streaming display...")
    
    try:
        # This should now stream
        lui("Count from 1 to 3, explaining each number briefly.")
        
        elapsed = time.time() - start_time
        print(f"\nQuery completed in {elapsed:.1f}s")
        
        # Check display was called multiple times
        print(f"Display called: {mock_display.call_count} times")
        print(f"Clear output called: {mock_clear.call_count} times")
        print(f"HTML created: {mock_html.call_count} times")
        
        # Show result
        print(f"\nFinal text: {lui.text[:100]}...")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_notebook_streaming()