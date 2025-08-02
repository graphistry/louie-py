#!/usr/bin/env python3
"""Debug streaming behavior in Louie client."""

import json
import time
from unittest.mock import Mock, patch
import httpx
import os

# Set up test credentials
os.environ['GRAPHISTRY_USERNAME'] = 'leotest2'
os.environ['GRAPHISTRY_PASSWORD'] = 'accountaccount'
os.environ['GRAPHISTRY_SERVER'] = 'graphistry-dev.grph.xyz'

from louieai import louie
from louieai._client import LouieClient


def test_streaming_behavior():
    """Test how streaming currently works."""
    
    # Create mock streaming lines that simulate a real response
    mock_lines = [
        '{"dthread_id": "D_test123"}',
        '{"payload": {"id": "B_001", "type": "TextElement", "text": "Starting analysis..."}}',
        '{"payload": {"id": "B_001", "type": "TextElement", "text": "Starting analysis...\\nProcessing data..."}}',
        '{"payload": {"id": "B_001", "type": "TextElement", "text": "Starting analysis...\\nProcessing data...\\nGenerating insights..."}}',
        '{"payload": {"id": "B_001", "type": "TextElement", "text": "Starting analysis...\\nProcessing data...\\nGenerating insights...\\nComplete!"}}',
        '{"payload": {"id": "B_002", "type": "DfElement", "df_id": "df_456", "metadata": {"shape": [5, 3]}}}'
    ]
    
    # Create a generator that yields lines with delays
    def slow_lines():
        for i, line in enumerate(mock_lines):
            print(f"\n[{i}] Streaming line: {line[:80]}...")
            yield line
            time.sleep(0.5)  # Simulate network delay
    
    # Mock the streaming response
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.iter_lines = slow_lines
    
    # Mock httpx client
    mock_stream_cm = Mock()
    mock_stream_cm.__enter__ = Mock(return_value=mock_response)
    mock_stream_cm.__exit__ = Mock(return_value=None)
    
    mock_httpx_instance = Mock()
    mock_httpx_instance.stream.return_value = mock_stream_cm
    
    # Create client
    client = LouieClient()
    
    print("Starting streaming test...")
    print("="*60)
    
    start_time = time.time()
    
    with patch('louieai._client.httpx.Client') as mock_httpx:
        mock_httpx.return_value.__enter__.return_value = mock_httpx_instance
        
        # Mock Arrow fetch to avoid network calls
        with patch.object(client, '_fetch_dataframe_arrow', return_value=None):
            print("\nCalling add_cell (this will collect all lines before returning)...")
            response = client.add_cell("", "Test streaming")
    
    elapsed = time.time() - start_time
    
    print(f"\nResponse received after {elapsed:.1f}s")
    print(f"Thread ID: {response.thread_id}")
    print(f"Elements: {len(response.elements)}")
    
    for i, elem in enumerate(response.elements):
        print(f"\nElement {i}:")
        print(f"  Type: {elem.get('type')}")
        if elem.get('type') == 'TextElement':
            print(f"  Text: {elem.get('text')}")


def test_direct_streaming():
    """Test direct streaming with httpx to show what's possible."""
    print("\n\nDirect streaming test (what we want to achieve):")
    print("="*60)
    
    # Simulate direct streaming
    mock_lines = [
        '{"dthread_id": "D_test123"}',
        '{"payload": {"id": "B_001", "type": "TextElement", "text": "Starting..."}}',
        '{"payload": {"id": "B_001", "type": "TextElement", "text": "Starting...\\nProcessing..."}}',
        '{"payload": {"id": "B_001", "type": "TextElement", "text": "Starting...\\nProcessing...\\nDone!"}}',
    ]
    
    print("\nStreaming with immediate display:")
    
    elements_by_id = {}
    thread_id = None
    
    for i, line in enumerate(mock_lines):
        time.sleep(0.5)  # Simulate network delay
        
        try:
            data = json.loads(line)
            
            # Handle thread ID
            if "dthread_id" in data:
                thread_id = data["dthread_id"]
                print(f"\n[Thread created: {thread_id}]")
            
            # Handle payload updates
            elif "payload" in data:
                elem = data["payload"]
                elem_id = elem.get("id")
                
                if elem_id:
                    # This is an update to existing element
                    old_elem = elements_by_id.get(elem_id, {})
                    elements_by_id[elem_id] = elem
                    
                    # Display update
                    if elem.get("type") == "TextElement":
                        old_text = old_elem.get("text", "")
                        new_text = elem.get("text", "")
                        
                        # Show only the new content
                        if new_text != old_text:
                            if old_text and new_text.startswith(old_text):
                                # Show only the appended part
                                appended = new_text[len(old_text):]
                                print(f"{appended}", end="", flush=True)
                            else:
                                # Full replacement
                                print(f"\n{new_text}", end="", flush=True)
                    
                    elif elem.get("type") == "DfElement":
                        print(f"\n\n[DataFrame available: {elem.get('df_id')}]")
        
        except json.JSONDecodeError:
            pass
    
    print("\n\n[Streaming complete]")


if __name__ == "__main__":
    test_streaming_behavior()
    test_direct_streaming()