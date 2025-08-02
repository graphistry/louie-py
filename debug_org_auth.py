#!/usr/bin/env python3
"""Debug script to test the exact user scenario with credentials."""

import logging
import sys

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# Import after logging is configured
import louieai
import graphistry

def main():
    """Test the exact user scenario."""
    print("=== Testing exact user scenario ===\n")
    
    print("1. Creating graphistry client with org_name...")
    g = graphistry.register(
        api=3,
        server='graphistry-dev.grph.xyz',
        personal_key_id='CU5V6VZJB7', 
        personal_key_secret='32RBP6PUCSUVAIYJ',
        org_name='databricks-pat-botsv3'
    )
    
    print("\n2. Checking graphistry client state...")
    # Check if org_name() method exists
    if hasattr(g, 'org_name') and callable(g.org_name):
        try:
            org_name_value = g.org_name()
            print(f"   g.org_name() = {org_name_value}")
        except Exception as e:
            print(f"   g.org_name() failed: {e}")
    
    # Check various attributes
    if hasattr(g, '_credentials'):
        print(f"   g._credentials exists: {type(g._credentials)}")
        if hasattr(g._credentials, 'get'):
            print(f"   g._credentials.get('org_name') = {g._credentials.get('org_name')}")
    
    if hasattr(g, '_auth_manager'):
        print(f"   g._auth_manager exists")
        if g._auth_manager and hasattr(g._auth_manager, '_credentials'):
            print(f"   g._auth_manager._credentials.get('org_name') = {g._auth_manager._credentials.get('org_name')}")
    
    print("\n3. Creating Louie client from graphistry client...")
    lui = louieai.louie(g, server_url='https://louie-dev.grph.xyz', share_mode='Private')
    
    print("\n4. Checking Louie client internals...")
    if hasattr(lui, '_client'):
        client = lui._client
        if hasattr(client, '_auth_manager'):
            auth_mgr = client._auth_manager
            if hasattr(auth_mgr, '_credentials'):
                creds = auth_mgr._credentials
                print(f"   org_name in Louie credentials: {creds.get('org_name')}")
    
    print("\n5. Making a test request...")
    try:
        response = lui("get some data databricks aws-s3-accesslogs", traces=True)
        print(f"\nSuccess! Thread ID: {response.thread_id}")
        print(f"URL: {lui.url}")
    except Exception as e:
        print(f"\nFailed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()