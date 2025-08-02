"""
Test script to run in Jupyter notebook to debug display issues.

Run each cell separately to see the behavior:
"""

# Cell 1: Setup and authentication
import pandas as pd
import graphistry
import louieai
from IPython.display import display, HTML

print("Testing notebook display behavior...")

# Create a mock graphistry client for testing
class MockGraphistryClient:
    def api_token(self):
        return "test-token"
    def register(self, **kwargs):
        pass
    def refresh(self):
        pass

g = MockGraphistryClient()

# Cell 2: Test basic display
print("\n=== Test 1: Basic Display ===")
# Create a test cursor
lui = louieai.louie(g, server_url="https://test.louie.ai")

# Check if we're in Jupyter
print(f"In Jupyter: {lui._in_jupyter()}")
print(f"Display enabled: {lui._in_jupyter()}")

# Cell 3: Mock a response with text and dataframe
print("\n=== Test 2: Mock Response ===")
from louieai._client import Response
from unittest.mock import Mock, patch

# Create a fake response
fake_df = pd.DataFrame({
    'user_id': ['u1', 'u2', 'u3'],
    'score': [100, 85, 92],
    'status': ['active', 'active', 'pending']
})

fake_elements = [
    {"type": "TextElement", "id": "1", "text": "Here's your analysis:"},
    {"type": "TextElement", "id": "1", "text": "Here's your analysis:\nI found 3 users."},
    {"type": "DfElement", "id": "2", "table": fake_df}
]

fake_response = Response(thread_id="D_test123", elements=fake_elements)

# Cell 4: Test direct display
print("\n=== Test 3: Direct Display Test ===")
from louieai.notebook.cursor import _render_response_html

# Get the HTML that would be displayed
html_content = _render_response_html(fake_response)
print(f"Generated HTML length: {len(html_content)} chars")

# Try to display it
if html_content:
    display(HTML(html_content))
else:
    print("No HTML content generated!")

# Cell 5: Test cursor display method
print("\n=== Test 4: Cursor Display Method ===")

# Add to history and try to access
lui._history.append(fake_response)
lui._current_thread = "D_test123"

# Check data access
print(f"lui.text: {lui.text}")
print(f"lui.df type: {type(lui.df)}")
print(f"lui.df shape: {lui.df.shape if lui.df is not None else 'None'}")

# Test manual display
lui._display(fake_response)

# Cell 6: Test auto-display on query
print("\n=== Test 5: Mock Query with Auto-Display ===")

# Mock the add_cell method to return our fake response
with patch.object(lui._client, 'add_cell', return_value=fake_response):
    # This should auto-display if in Jupyter
    result = lui("test query")
    
print(f"Query returned: {type(result)}")
print(f"Auto-display should have triggered: {lui._in_jupyter()}")

# Cell 7: Check display parameters
print("\n=== Test 6: Display Parameters ===")

# Test with display disabled
with patch.object(lui._client, 'add_cell', return_value=fake_response):
    lui("test query", display=False)
    print("Query with display=False completed")

# Cell 8: Debug dataframe extraction
print("\n=== Test 7: DataFrame Extraction ===")

# Direct test of dataframe extraction
proxy = louieai.notebook.cursor.ResponseProxy(fake_response)
print(f"proxy.dfs: {proxy.dfs}")
print(f"proxy.df: {proxy.df}")
print(f"Number of dataframes: {len(proxy.dfs)}")

# Test from cursor
print(f"\nlui.dfs: {lui.dfs}")
print(f"lui.df: {lui.df}")

# Cell 9: Manual HTML display test
print("\n=== Test 8: Manual HTML Rendering ===")

# Create simple HTML to test display works
test_html = """
<div style="border: 1px solid #ccc; padding: 10px;">
    <h3>Test Display</h3>
    <p>If you see this styled box, HTML display is working!</p>
    <table border="1">
        <tr><th>Column 1</th><th>Column 2</th></tr>
        <tr><td>Data 1</td><td>Data 2</td></tr>
    </table>
</div>
"""
display(HTML(test_html))

# Cell 10: Summary
print("\n=== Summary ===")
print("Run this script in a Jupyter notebook to debug display issues.")
print("Check each test output to identify where the problem occurs.")
print("\nKey things to verify:")
print("1. Are you seeing the HTML displays?")
print("2. Is lui._in_jupyter() returning True?")
print("3. Can you access lui.df after queries?")
print("4. Do manual display() calls work?")