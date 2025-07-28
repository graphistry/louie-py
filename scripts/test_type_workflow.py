#!/usr/bin/env python3
"""Test the complete type export/import workflow."""

import json
import subprocess
from pathlib import Path


def test_complete_workflow():
    """Test the complete workflow with example data."""
    print("🧪 Testing type export/import workflow")
    print("=" * 50)

    # Step 1: Verify example data exists
    example_file = Path("plans/element-types-example.json")
    if not example_file.exists():
        print("❌ Example data not found")
        return False

    print("✅ Example data found")

    # Step 2: Validate example data
    try:
        with open(example_file) as f:
            data = json.load(f)
        print(f"✅ Example data is valid JSON ({len(data['element_types'])} types)")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in example: {e}")
        return False

    # Step 3: Copy to data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    data_file = data_dir / "element_types.json"
    data_file.write_text(example_file.read_text())
    print("✅ Copied example to data directory")

    # Step 4: Run import script
    try:
        result = subprocess.run(
            ["uv", "run", "python", "scripts/generate_type_docs.py"],
            capture_output=True,
            text=True,
            check=True,
        )
        print("✅ Import script ran successfully")
        print(f"   Output: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Import script failed: {e}")
        print(f"   Error: {e.stderr}")
        return False

    # Step 5: Verify generated documentation
    output_file = Path("docs/api/response-types-generated.md")
    if not output_file.exists():
        print("❌ Generated documentation not found")
        return False

    content = output_file.read_text()
    if len(content) < 1000:  # Sanity check
        print("❌ Generated documentation seems too short")
        return False

    print("✅ Generated documentation looks good")

    # Step 6: Verify content
    required_sections = [
        "# Response Types Reference",
        "## Element Types",
        "### TextElement",
        "### DfElement",
        "## Type Detection",
    ]

    for section in required_sections:
        if section not in content:
            print(f"❌ Missing section: {section}")
            return False

    print("✅ All required sections present")

    # Step 7: Check for common issues
    if "TODO" in content or "FIXME" in content:
        print("⚠️  Found TODO/FIXME in generated docs")

    print("\n🎉 Complete workflow test passed!")
    print("\nNext steps:")
    print("1. Review generated documentation")
    print("2. Test with real graphistrygpt export")
    print("3. Set up automation")

    return True


if __name__ == "__main__":
    success = test_complete_workflow()
    exit(0 if success else 1)
