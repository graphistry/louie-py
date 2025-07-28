#!/usr/bin/env python3
"""Safe testing of documentation examples with proper mocking."""

import re
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def extract_python_blocks(markdown_file: Path) -> list[tuple[str, int, str]]:
    """Extract Python code blocks from a markdown file."""
    content = markdown_file.read_text()
    blocks = []

    # Match ```python blocks
    pattern = r"```python\n(.*?)\n```"

    for match in re.finditer(pattern, content, re.DOTALL):
        code = match.group(1)
        line_num = content[: match.start()].count("\n") + 1

        # Get context (previous non-empty line)
        lines_before = content[: match.start()].strip().split("\n")
        context = lines_before[-1] if lines_before else "Unknown context"

        blocks.append((code, line_num, context))

    return blocks


def preprocess_code(code: str) -> str:
    """Preprocess code to handle common patterns in docs.

    - Replace placeholder credentials
    - Handle import statements
    """
    # Replace placeholder credentials
    code = code.replace('"your_user"', '"test_user"')
    code = code.replace('"your_pass"', '"test_pass"')
    code = code.replace("hub.graphistry.com", "test.graphistry.com")

    return code


def test_documentation_file(doc_file: Path):
    """Test all examples in a documentation file."""
    if not doc_file.exists():
        print(f"File not found: {doc_file}")
        return False

    blocks = extract_python_blocks(doc_file)
    print(f"\nTesting {len(blocks)} Python blocks from {doc_file}")

    # Import from current directory
    sys.path.insert(0, str(Path(__file__).parent))
    from doc_fixtures import create_mock_client

    # Track success
    total = len(blocks)
    passed = 0
    failed = 0
    skipped = 0

    for i, (code, line_num, context) in enumerate(blocks):
        print(f"\n{i + 1}. Line {line_num}: {context[:60]}...")

        # Preprocess code
        code = preprocess_code(code)

        # Skip shell commands and non-Python code
        if any(code.strip().startswith(x) for x in ["$", "pip ", "uv "]):
            print("   SKIP: Shell command")
            skipped += 1
            continue

        # Skip template code
        if "..." in code or "# TODO" in code:
            print("   SKIP: Template/incomplete code")
            skipped += 1
            continue

        # Test the code
        try:
            # Create fresh mocks for each test
            mock_client = create_mock_client()

            # Patch imports
            with (
                patch("graphistry.register") as mock_register,
                patch("graphistry.api_token", return_value="fake-token"),
                patch(
                    "graphistry.nodes",
                    return_value=Mock(edges=Mock(return_value=Mock())),
                ),
            ):
                # Create execution namespace
                namespace = {
                    "__builtins__": __builtins__,
                    "print": print,
                }

                # Execute imports first with patching
                if "import graphistry" in code or "from louieai import" in code:
                    with patch.dict(
                        "sys.modules",
                        {
                            "louieai": Mock(LouieClient=Mock(return_value=mock_client)),
                            "graphistry": Mock(
                                register=mock_register,
                                api_token=Mock(return_value="fake-token"),
                                nodes=Mock(
                                    return_value=Mock(edges=Mock(return_value=Mock()))
                                ),
                            ),
                        },
                    ):
                        exec(code, namespace)
                else:
                    # For code without imports, provide pre-imported objects
                    namespace.update(
                        {
                            "client": mock_client,
                            "LouieClient": Mock(return_value=mock_client),
                            "graphistry": Mock(register=mock_register),
                            "df": Mock(),
                            "df2": Mock(),
                            "g": Mock(),
                        }
                    )
                    exec(code, namespace)

                print("   ✓ PASS")
                passed += 1

        except Exception as e:
            print(f"   ✗ FAIL: {type(e).__name__}: {e}")
            if "--verbose" in sys.argv:
                print(f"   Code:\n{code}")
            failed += 1

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Summary for {doc_file.name}:")
    print(f"  Total blocks: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    print(
        f"  Success rate: {passed / (passed + failed) * 100:.1f}%"
        if (passed + failed) > 0
        else "  No executable blocks"
    )

    return failed == 0


def main():
    """Run documentation tests."""
    import argparse

    parser = argparse.ArgumentParser(description="Test documentation examples")
    parser.add_argument("files", nargs="*", help="Documentation files to test")
    parser.add_argument("--verbose", action="store_true", help="Show code on failures")
    parser.add_argument(
        "--all", action="store_true", help="Test all documentation files"
    )
    args = parser.parse_args()

    if args.all:
        # Test all markdown files in docs/
        doc_files = list(Path("docs").rglob("*.md"))
    elif args.files:
        doc_files = [Path(f) for f in args.files]
    else:
        # Default to main documentation files
        doc_files = [
            Path("docs/index.md"),
            Path("docs/api/client.md"),
            Path("docs/query-patterns.md"),
        ]

    all_passed = True
    for doc_file in doc_files:
        if not test_documentation_file(doc_file):
            all_passed = False

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
