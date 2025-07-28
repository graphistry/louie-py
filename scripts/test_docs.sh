#!/usr/bin/env bash
# Test documentation examples

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "📚 Testing Documentation Examples"
echo "================================="

# Create a test script that properly sets up context
cat > tests/run_doc_tests.py << 'EOF'
#!/usr/bin/env python3
"""Run documentation tests with proper context."""

import re
import sys
from pathlib import Path
from unittest.mock import Mock, patch

def extract_code_blocks(filepath):
    """Extract Python code blocks from markdown."""
    content = Path(filepath).read_text()
    blocks = []
    
    # Find all ```python blocks
    pattern = r'```python\n(.*?)\n```'
    for match in re.finditer(pattern, content, re.DOTALL):
        code = match.group(1)
        line_num = content[:match.start()].count('\n') + 1
        blocks.append((code, line_num))
    
    return blocks

def create_mock_client():
    """Create a properly mocked LouieClient."""
    client = Mock()
    
    # Mock thread
    thread = Mock()
    thread.id = "D_test123"
    thread.name = "Test Thread"
    
    # Mock responses
    text_response = Mock()
    text_response.type = "TextElement"
    text_response.text = "Sample response text"
    text_response.thread_id = thread.id
    
    df_response = Mock()
    df_response.type = "DfElement"
    df_response.to_dataframe = Mock(return_value=Mock())
    df_response.thread_id = thread.id
    
    # Client methods
    client.create_thread = Mock(return_value=thread)
    client.add_cell = Mock(return_value=text_response)
    client.ask = Mock(return_value=text_response)
    client.list_threads = Mock(return_value=[thread])
    client.register = Mock(return_value=client)
    
    return client, thread, text_response

def test_code_block(code, context):
    """Test a single code block with proper context."""
    # Skip non-executable code
    if any(skip in code for skip in ['...', '$ ', 'pip install', 'uv pip']):
        return 'SKIP', 'Non-executable'
    
    # Replace placeholders
    code = code.replace('"your_user"', '"test_user"')
    code = code.replace('"your_pass"', '"test_pass"')
    
    # Create test context
    client, thread, response = create_mock_client()
    
    # Mock modules
    mock_graphistry = Mock()
    mock_graphistry.register = Mock()
    mock_graphistry.api_token = Mock(return_value="fake-token")
    mock_graphistry.nodes = Mock(return_value=mock_graphistry)
    mock_graphistry.edges = Mock(return_value=mock_graphistry)
    
    mock_louieai = Mock()
    mock_louieai.LouieClient = Mock(return_value=client)
    
    # Create namespace with common variables
    namespace = {
        '__builtins__': __builtins__,
        'print': lambda *args: None,  # Suppress prints
        'client': client,
        'thread': thread,
        'response': response,
        'df': Mock(),
        'df2': Mock(),
        'g': mock_graphistry,
        'threads': [thread],
        'response1': response,
        'response2': response,
    }
    
    try:
        # Patch imports
        with patch.dict('sys.modules', {
            'graphistry': mock_graphistry,
            'louieai': mock_louieai,
        }):
            # Handle imports in code
            if 'import' in code:
                exec(code, namespace)
            else:
                # For snippets, ensure imports are available
                namespace['graphistry'] = mock_graphistry
                namespace['LouieClient'] = Mock(return_value=client)
                namespace['louieai'] = mock_louieai
                exec(code, namespace)
        
        return 'PASS', None
    except Exception as e:
        return 'FAIL', f"{type(e).__name__}: {e}"

def test_file(filepath):
    """Test all code blocks in a file."""
    blocks = extract_code_blocks(filepath)
    if not blocks:
        return True, 0, 0, 0
    
    passed = failed = skipped = 0
    
    print(f"\nTesting {filepath}")
    print("-" * 60)
    
    for code, line_num in blocks:
        status, message = test_code_block(code, {})
        
        if status == 'PASS':
            passed += 1
            print(f"  Line {line_num}: ✓ PASS")
        elif status == 'SKIP':
            skipped += 1
            print(f"  Line {line_num}: - SKIP ({message})")
        else:
            failed += 1
            print(f"  Line {line_num}: ✗ FAIL ({message})")
            if '--verbose' in sys.argv:
                print(f"    Code: {code[:50]}...")
    
    success_rate = (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0
    print(f"\n  Summary: {passed} passed, {failed} failed, {skipped} skipped")
    print(f"  Success rate: {success_rate:.1f}%")
    
    return failed == 0, passed, failed, skipped

def main():
    """Run tests on documentation files."""
    files = [
        "docs/index.md",
        "docs/api/client.md", 
        "docs/query-patterns.md",
    ]
    
    total_passed = total_failed = total_skipped = 0
    all_success = True
    
    for filepath in files:
        if Path(filepath).exists():
            success, passed, failed, skipped = test_file(filepath)
            total_passed += passed
            total_failed += failed
            total_skipped += skipped
            if not success:
                all_success = False
    
    print("\n" + "=" * 60)
    print("TOTAL RESULTS")
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_failed}")
    print(f"  Skipped: {total_skipped}")
    
    if all_success:
        print("\n✅ All documentation tests passed!")
        return 0
    else:
        print("\n❌ Some documentation tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

# Run the tests
echo ""
uv run python tests/run_doc_tests.py "$@"

# Clean up
rm -f tests/run_doc_tests.py

echo ""
echo "✅ Documentation testing complete"