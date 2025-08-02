#!/usr/bin/env python3
"""Debug dataframe fetching issue."""

import logging
import json

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG, format="%(name)s - %(levelname)s - %(message)s"
)

import louieai
import graphistry

print("louieai", louieai.__version__)
print("graphistry", graphistry.__version__)

# Create graphistry client
g = graphistry.register(
    api=3,
    server="graphistry-dev.grph.xyz",
    personal_key_id="CU5V6VZJB7",
    personal_key_secret="32RBP6PUCSUVAIYJ",
    org_name="databricks-pat-botsv3",
)

# Create louie client
lui = louieai.louie(g, server_url="https://louie-dev.grph.xyz", share_mode="Private")

# Make request
print("\n=== Making request ===")
lui("get some data databricks aws-s3-accesslogs", traces=False)

# Check results
print("\n=== Results ===")
print(f"lui.df is None: {lui.df is None}")
print(f"lui.dfs: {lui.dfs}")

# Check the raw response elements
if hasattr(lui, "_history") and lui._history:
    last_response = lui._history[-1]
    print(f"\n=== Last response elements ===")
    for i, elem in enumerate(last_response.elements):
        print(f"Element {i}: type={elem.get('type')}")
        if elem.get("type") == "DfElement":
            print(f"  Full element: {json.dumps(elem, indent=2)}")
            print(f"  df_id: {elem.get('df_id')}")
            print(f"  block_id: {elem.get('block_id')}")
            print(f"  Keys: {list(elem.keys())}")
