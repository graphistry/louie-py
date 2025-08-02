#!/usr/bin/env python3
"""Integration test for dataframe fetching."""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import louieai
import graphistry

print("=== Dataframe Fetching Integration Test ===\n")

# Get credentials
server = os.getenv("GRAPHISTRY_SERVER", "graphistry-dev.grph.xyz")
username = os.getenv("GRAPHISTRY_USERNAME", "leotest2")
password = os.getenv("GRAPHISTRY_PASSWORD", "accountaccount")
louie_server = os.getenv("LOUIE_SERVER", "louie-dev.grph.xyz")

print(f"Using server: {server}")
print(f"Using username: {username}")
print(f"Louie server: {louie_server}\n")

# Create graphistry client
print("1. Creating graphistry client...")
g = graphistry.register(api=3, server=server, username=username, password=password)

# Create louie client
print("2. Creating louie client...")
lui = louieai.louie(g, server_url=f"https://{louie_server}")

print("3. Making request for data...")
lui("Create a simple dataframe with 5 rows containing id, name, and score columns")

print("\n4. Checking results...")
print(f"   lui.df is None: {lui.df is None}")
print(f"   Number of dataframes: {len(lui.dfs)}")

# Check the response structure
if hasattr(lui, "_history") and lui._history:
    last_response = lui._history[-1]
    print(f"\n5. Analyzing response elements...")
    print(f"   Total elements: {len(last_response.elements)}")

    for i, elem in enumerate(last_response.elements):
        elem_type = elem.get("type")
        print(f"\n   Element {i}: type={elem_type}")

        if elem_type == "DfElement":
            print(f"     Keys in element: {sorted(elem.keys())}")

            # Check various possible ID fields
            print(f"     df_id: {elem.get('df_id')}")
            print(f"     block_id: {elem.get('block_id')}")
            print(f"     id: {elem.get('id')}")

            # Check metadata
            if "metadata" in elem:
                print(f"     metadata: {elem['metadata']}")

            # Check if table was populated
            print(f"     'table' key present: {'table' in elem}")

            # Print full element for debugging
            elem_copy = elem.copy()
            if "table" in elem_copy:
                elem_copy["table"] = (
                    f"<DataFrame {elem_copy['table'].shape if hasattr(elem_copy['table'], 'shape') else 'unknown'}>"
                )
            print(f"     Full element: {json.dumps(elem_copy, indent=8)}")

print("\n6. Testing with explicit databricks data request...")
lui2 = louieai.louie(g, server_url=f"https://{louie_server}")
lui2("get some data from databricks client_demos.botsv3.aws-s3-accesslogs limit 10")

print(f"\n   lui2.df is None: {lui2.df is None}")
if lui2.df is not None:
    print(f"   DataFrame shape: {lui2.df.shape}")
    print(f"   DataFrame columns: {list(lui2.df.columns)}")
else:
    # Check response elements
    if hasattr(lui2, "_history") and lui2._history:
        last_response = lui2._history[-1]
        df_elements = [
            e for e in last_response.elements if e.get("type") == "DfElement"
        ]
        print(f"   Found {len(df_elements)} DfElement(s)")
        for df_elem in df_elements:
            print(f"   DfElement keys: {sorted(df_elem.keys())}")

print("\nTest complete.")
