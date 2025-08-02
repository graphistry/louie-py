#!/usr/bin/env python3
"""Test real streaming behavior with actual API."""

import os
import time
import json

# Set up test credentials
os.environ['GRAPHISTRY_USERNAME'] = 'leotest2'
os.environ['GRAPHISTRY_PASSWORD'] = 'accountaccount'
os.environ['GRAPHISTRY_SERVER'] = 'graphistry-dev.grph.xyz'
os.environ['LOUIE_URL'] = 'https://louie-dev.grph.xyz'

from louieai import louie


def test_notebook_streaming():
    """Test current notebook API streaming behavior."""
    print("Testing current notebook API (waits for complete response)...")
    print("="*60)
    
    # Create notebook interface
    lui = louie()
    
    start_time = time.time()
    print("Calling lui() - this will wait for complete response before displaying...")
    
    # This currently waits for the entire response
    lui("What is 2+2? Think step by step.")
    
    elapsed = time.time() - start_time
    print(f"\nResponse displayed after {elapsed:.1f}s")
    print(f"Text: {lui.text[:100]}...")


def test_direct_streaming():
    """Test what streaming could look like with direct API access."""
    print("\n\nDirect streaming test (showing desired behavior)...")
    print("="*60)
    
    import httpx
    import graphistry
    from louieai._client import LouieClient
    
    # Create graphistry client with auth
    g = graphistry.register(
        api=3,
        server='graphistry-dev.grph.xyz',
        username='leotest2',
        password='accountaccount'
    )
    
    # Create client
    client = LouieClient(server_url="https://louie-dev.grph.xyz", graphistry_client=g)
    
    # Get headers
    headers = client._get_headers()
    
    # Build request
    params = {
        "query": "Count from 1 to 5 slowly, explaining each number.",
        "agent": "LouieAgent",
        "ignore_traces": "true",
        "share_mode": "Private"
    }
    
    print("Starting streaming request...")
    start_time = time.time()
    
    thread_id = None
    elements_by_id = {}
    
    try:
        with httpx.Client(timeout=30.0) as http_client:
            with http_client.stream(
                "POST", 
                "https://louie-dev.grph.xyz/api/chat/", 
                headers=headers, 
                params=params
            ) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        
                        # Handle thread ID
                        if "dthread_id" in data:
                            thread_id = data["dthread_id"]
                            print(f"\n[Thread: {thread_id}]")
                        
                        # Handle payload updates
                        elif "payload" in data:
                            elem = data["payload"]
                            elem_id = elem.get("id")
                            elem_type = elem.get("type")
                            
                            if elem_id and elem_type == "TextElement":
                                old_text = elements_by_id.get(elem_id, {}).get("text", "")
                                new_text = elem.get("text", "")
                                
                                if new_text and new_text != old_text:
                                    # Show incremental update
                                    if old_text and new_text.startswith(old_text):
                                        # Just the new part
                                        delta = new_text[len(old_text):]
                                        print(delta, end="", flush=True)
                                    else:
                                        # Full replacement
                                        print(f"\n{new_text}", end="", flush=True)
                                
                                elements_by_id[elem_id] = elem
                            
                            elif elem_type == "DfElement":
                                print(f"\n\n[DataFrame: {elem.get('df_id') or elem.get('block_id')}]")
                                elements_by_id[elem_id] = elem
                    
                    except json.JSONDecodeError:
                        print(f"\n[Invalid JSON: {line[:50]}...]")
                    
                    # Show we're getting updates in real-time
                    current_time = time.time() - start_time
                    if int(current_time) != int(current_time - 0.1):  # Every second
                        print(f" [{current_time:.0f}s]", end="", flush=True)
    
    except Exception as e:
        print(f"\n\nError: {e}")
    
    total_time = time.time() - start_time
    print(f"\n\n[Streaming complete in {total_time:.1f}s]")


if __name__ == "__main__":
    # Test current behavior
    test_notebook_streaming()
    
    # Test desired streaming behavior
    test_direct_streaming()