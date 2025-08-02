#!/usr/bin/env python3
"""Debug script to trace org_name flow through the Louie client chain."""

import logging
import sys

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# Import after logging is configured
import graphistry
import louieai

def main():
    """Test org_name propagation through the client chain."""
    print("=== Testing org_name propagation ===\n")
    
    # Create graphistry client
    print("1. Creating graphistry client...")
    g = graphistry.client()
    
    # Check if org_name() method exists
    if hasattr(g, 'org_name') and callable(g.org_name):
        try:
            org_name_value = g.org_name()
            print(f"   g.org_name() = {org_name_value}")
        except Exception as e:
            print(f"   g.org_name() failed: {e}")
    else:
        print("   g.org_name() method not found")
    
    # Check various attributes
    if hasattr(g, '_credentials'):
        print(f"   g._credentials = {g._credentials}")
    else:
        print("   g._credentials not found")
        
    if hasattr(g, '_auth_manager'):
        print(f"   g._auth_manager = {g._auth_manager}")
        if g._auth_manager and hasattr(g._auth_manager, '_credentials'):
            print(f"   g._auth_manager._credentials = {g._auth_manager._credentials}")
    else:
        print("   g._auth_manager not found")
        
    if hasattr(g, '_org_name'):
        print(f"   g._org_name = {g._org_name}")
    else:
        print("   g._org_name not found")
    
    print("\n2. Creating Louie client from graphistry client...")
    lui = louieai.louie(g)
    
    print("\n3. Checking Louie client internals...")
    if hasattr(lui, '_client'):
        client = lui._client
        print(f"   lui._client exists")
        
        if hasattr(client, '_auth_manager'):
            auth_mgr = client._auth_manager
            print(f"   lui._client._auth_manager exists")
            
            if hasattr(auth_mgr, '_credentials'):
                creds = auth_mgr._credentials
                print(f"   lui._client._auth_manager._credentials = {creds}")
                print(f"   org_name in credentials: {creds.get('org_name')}")
    
    print("\n4. Making a test request to see headers...")
    print("   (Check the logs above for header information)")
    
    # Make a simple test query
    try:
        response = lui("Hello, test")
        print(f"\n5. Test query successful! Thread ID: {response.thread_id}")
    except Exception as e:
        print(f"\n5. Test query failed: {e}")

if __name__ == "__main__":
    main()