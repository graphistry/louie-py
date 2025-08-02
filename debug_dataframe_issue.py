#!/usr/bin/env python3
"""Debug script specifically for dataframe display issues."""

import json
import pandas as pd
from louieai._client import LouieClient, Response
from louieai.notebook.cursor import Cursor, ResponseProxy, _render_response_html

def test_df_element_parsing():
    """Test how DfElement is parsed from JSON."""
    print("=== Testing DfElement Parsing ===")
    
    # Simulate a JSONL response with a dataframe
    mock_df_data = {
        "columns": ["user_id", "score", "status"],
        "data": [
            ["u1", 100, "active"],
            ["u2", 85, "active"],
            ["u3", 92, "pending"]
        ]
    }
    
    # Create JSONL lines like the server would send
    lines = [
        '{"dthread_id": "D_test123"}',
        '{"payload": {"id": "B_001", "type": "TextElement", "text": "Here is your data:"}}',
        json.dumps({"payload": {"id": "B_002", "type": "DfElement", "table": mock_df_data}})
    ]
    
    # Parse the response
    client = LouieClient()
    response_text = "\n".join(lines)
    result = client._parse_jsonl_response(response_text)
    
    print(f"Thread ID: {result['dthread_id']}")
    print(f"Number of elements: {len(result['elements'])}")
    
    # Check what we got
    for i, elem in enumerate(result['elements']):
        print(f"\nElement {i}:")
        print(f"  Type: {elem.get('type')}")
        print(f"  ID: {elem.get('id')}")
        if elem.get('type') == 'DfElement':
            table = elem.get('table')
            print(f"  Table type: {type(table)}")
            print(f"  Table content: {table}")
            
            # Try to convert to DataFrame
            if isinstance(table, dict) and 'columns' in table and 'data' in table:
                try:
                    df = pd.DataFrame(table['data'], columns=table['columns'])
                    print(f"  Converted to DataFrame: {df.shape}")
                    print(df)
                except Exception as e:
                    print(f"  Failed to convert: {e}")
    
    # Create Response object
    response = Response(thread_id=result["dthread_id"], elements=result["elements"])
    print(f"\nResponse object created")
    print(f"response.dataframe_elements: {response.dataframe_elements}")
    
    return response


def test_response_properties():
    """Test Response properties for dataframes."""
    print("\n=== Testing Response Properties ===")
    
    # Create elements with proper DataFrame
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35]
    })
    
    elements = [
        {"type": "TextElement", "id": "1", "text": "User data:"},
        {"type": "DfElement", "id": "2", "table": df}
    ]
    
    response = Response(thread_id="test", elements=elements)
    
    print(f"response.text_elements: {len(response.text_elements)}")
    print(f"response.dataframe_elements: {len(response.dataframe_elements)}")
    
    for i, df_elem in enumerate(response.dataframe_elements):
        print(f"\nDataFrame element {i}:")
        print(f"  Type: {type(df_elem)}")
        print(f"  Keys: {df_elem.keys() if isinstance(df_elem, dict) else 'N/A'}")
        if isinstance(df_elem, dict) and 'table' in df_elem:
            table = df_elem['table']
            print(f"  Table type: {type(table)}")
            print(f"  Is DataFrame: {isinstance(table, pd.DataFrame)}")
            if isinstance(table, pd.DataFrame):
                print(f"  Shape: {table.shape}")
                print(f"  Columns: {list(table.columns)}")
    
    return response


def test_proxy_dataframe_access():
    """Test ResponseProxy dataframe access."""
    print("\n=== Testing ResponseProxy DataFrame Access ===")
    
    # Use response from previous test
    response = test_response_properties()
    proxy = ResponseProxy(response)
    
    print(f"\nResponseProxy properties:")
    print(f"proxy.df type: {type(proxy.df)}")
    print(f"proxy.dfs length: {len(proxy.dfs)}")
    
    if proxy.df is not None:
        print(f"proxy.df shape: {proxy.df.shape}")
        print(f"proxy.df columns: {list(proxy.df.columns)}")
        print(f"proxy.df head():")
        print(proxy.df.head())
    else:
        print("proxy.df is None!")
        
    # Debug the extraction method
    print("\nDebugging _extract_dataframes:")
    dfs = proxy._extract_dataframes(response)
    print(f"Extracted {len(dfs)} dataframes")
    
    return proxy


def test_cursor_dataframe_access():
    """Test Cursor dataframe access."""
    print("\n=== Testing Cursor DataFrame Access ===")
    
    # Create cursor with test response
    cursor = Cursor()
    
    # Add a test response to history
    df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    elements = [
        {"type": "TextElement", "text": "Data:"},
        {"type": "DfElement", "table": df}
    ]
    response = Response(thread_id="test", elements=elements)
    cursor._history.append(response)
    
    print(f"cursor.df type: {type(cursor.df)}")
    print(f"cursor.dfs length: {len(cursor.dfs)}")
    
    if cursor.df is not None:
        print(f"cursor.df shape: {cursor.df.shape}")
        print(cursor.df)
    else:
        print("cursor.df is None!")
        
    # Test extraction method
    print("\nTesting _extract_dataframes on cursor:")
    dfs = cursor._extract_dataframes(response)
    print(f"Extracted {len(dfs)} dataframes")
    for i, df in enumerate(dfs):
        print(f"  DataFrame {i}: shape={df.shape}")


def test_html_rendering():
    """Test HTML rendering of dataframes."""
    print("\n=== Testing HTML Rendering ===")
    
    # Create response with DataFrame
    df = pd.DataFrame({
        "product": ["A", "B", "C"],
        "sales": [100, 200, 150]
    })
    
    elements = [
        {"type": "TextElement", "text": "Sales data:"},
        {"type": "DfElement", "table": df}
    ]
    
    response = Response(thread_id="test", elements=elements)
    
    # Test rendering
    html = _render_response_html(response)
    print(f"Generated HTML length: {len(html)} chars")
    print(f"Contains table tag: {'<table' in html}")
    print(f"Contains Sales data text: {'Sales data' in html}")
    
    # Show first 500 chars of HTML
    print("\nFirst 500 chars of HTML:")
    print(html[:500])
    
    # Check if dataframe HTML is included
    df_html = df._repr_html_()
    print(f"\nDataFrame HTML length: {len(df_html)} chars")
    print(f"DataFrame HTML in response: {df_html[:100] in html}")


def test_real_server_response_format():
    """Show what a real server response might look like."""
    print("\n=== Real Server Response Format ===")
    
    # This is what the server might actually send
    server_response = {
        "type": "DfElement",
        "id": "df_123",
        "table": {
            "columns": ["timestamp", "event", "user"],
            "data": [
                ["2024-01-01 10:00", "login", "alice"],
                ["2024-01-01 10:15", "view_page", "alice"],
                ["2024-01-01 10:30", "logout", "alice"]
            ],
            "index": [0, 1, 2]
        }
    }
    
    print("Server sends table as dict:")
    print(json.dumps(server_response, indent=2))
    
    # The issue might be that the table needs to be converted
    table_data = server_response["table"]
    if isinstance(table_data, dict):
        df = pd.DataFrame(
            data=table_data["data"],
            columns=table_data["columns"],
            index=table_data.get("index")
        )
        print(f"\nConverted to DataFrame: {df.shape}")
        print(df)


if __name__ == "__main__":
    print("DataFrame Display Debug Script")
    print("=" * 50)
    
    # Run all tests
    test_df_element_parsing()
    test_proxy_dataframe_access()
    test_cursor_dataframe_access()
    test_html_rendering()
    test_real_server_response_format()
    
    print("\n" + "=" * 50)
    print("Key findings:")
    print("1. Check if server sends DataFrame as dict that needs conversion")
    print("2. Verify dataframe_elements property filters correctly")
    print("3. Ensure _extract_dataframes looks for the right structure")
    print("4. Confirm HTML rendering includes DataFrame._repr_html_()")