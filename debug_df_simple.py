#!/usr/bin/env python3
"""Simple debug for dataframe fetching."""

import louieai

# Override _format_element temporarily to debug
original_format = louieai.notebook.streaming.StreamingDisplay._format_element


def debug_format_element(self, elem):
    elem_type = elem.get("type", "")
    if elem_type == "DfElement":
        print(f"\n[DEBUG] DfElement received:")
        print(f"  Keys: {list(elem.keys())}")
        print(f"  Full element: {elem}")
        if "metadata" in elem:
            print(f"  Metadata: {elem['metadata']}")
    return original_format(self, elem)


louieai.notebook.streaming.StreamingDisplay._format_element = debug_format_element

# Now run the test
import graphistry

g = graphistry.register(
    api=3,
    server="graphistry-dev.grph.xyz",
    personal_key_id="CU5V6VZJB7",
    personal_key_secret="32RBP6PUCSUVAIYJ",
    org_name="databricks-pat-botsv3",
)

lui = louieai.louie(g, server_url="https://louie-dev.grph.xyz", share_mode="Private")

print("Making request...")
lui("get some data databricks aws-s3-accesslogs", traces=False)

print(f"\nlui.df is None: {lui.df is None}")
print(f"Number of dataframes: {len(lui.dfs)}")

# Restore original
louieai.notebook.streaming.StreamingDisplay._format_element = original_format
