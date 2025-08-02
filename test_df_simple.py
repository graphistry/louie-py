#!/usr/bin/env python3
"""Simple test script for dataframe issue."""

import louieai
import graphistry

# Create graphistry client with direct credentials
g = graphistry.register(
    api=3,
    server='graphistry-dev.grph.xyz',
    personal_key_id='CU5V6VZJB7', 
    personal_key_secret='32RBP6PUCSUVAIYJ',
    org_name='databricks-pat-botsv3'
)

# Create louie client
lui = louieai.louie(g, server_url='https://louie-dev.grph.xyz', share_mode='Private')

# Make request
print("Making request...")
result = lui('get some data databricks aws-s3-accesslogs limit 10', traces=False)

# Check results
print(f"\nlui.df is None: {lui.df is None}")
print(f"Number of elements: {len(lui.elements)}")

# Show element types
print("\nElement types:")
for i, elem in enumerate(lui.elements):
    print(f"  {i}: type='{elem.get('type')}' keys={list(elem.keys())}")
    if elem.get('type') in ['df', 'DfElement']:
        print(f"     df_id={elem.get('df_id')} block_id={elem.get('block_id')} id={elem.get('id')}")

# Check if we have text elements
texts = [e for e in lui.elements if e.get('type') in ['text', 'TextElement']]
print(f"\nText elements: {len(texts)}")
if texts:
    for t in texts[:3]:  # Show first 3
        content = t.get('value') or t.get('text') or t.get('content')
        print(f"  '{content}'")

print("\nDone.")