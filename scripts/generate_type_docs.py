#!/usr/bin/env python3
"""Import element types and generate documentation.

This script reads the exported element types from graphistrygpt
and generates markdown documentation for the louie-py client.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def load_element_types(path: Path) -> dict[str, Any]:
    """Load element types from JSON export."""
    with open(path) as f:
        data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"Expected dict from JSON file, got {type(data)}")
        return data


def format_json_value(value: Any, indent: int = 2) -> str:
    """Format a JSON value for display in markdown."""
    if isinstance(value, dict):
        # Pretty print with indentation
        lines = json.dumps(value, indent=2).split("\n")
        # Add extra indentation for markdown
        return "\n".join(" " * indent + line for line in lines)
    return json.dumps(value, indent=2)


def generate_property_table(properties: dict[str, Any]) -> list[str]:
    """Generate a markdown table for schema properties."""
    lines = []
    lines.append("| Field | Type | Required | Description |")
    lines.append("|-------|------|----------|-------------|")

    required = properties.get("required", [])

    for prop_name, prop_info in properties.items():
        if prop_name == "required":
            continue

        prop_type = prop_info.get("type", "any")
        if "enum" in prop_info:
            prop_type = f"enum: {', '.join(prop_info['enum'])}"
        elif "const" in prop_info:
            prop_type = f"const: '{prop_info['const']}'"

        is_required = "Yes" if prop_name in required else "No"
        description = prop_info.get("description", "")

        lines.append(f"| `{prop_name}` | {prop_type} | {is_required} | {description} |")

    return lines


def generate_markdown_docs(data: dict[str, Any]) -> str:
    """Generate markdown documentation from element types."""
    md = []

    # Header
    md.append("# Response Types Reference")
    md.append("")
    md.append(
        "Louie.ai returns different types of elements based on your "
        "natural language queries. Understanding these types helps you "
        "handle responses effectively."
    )
    md.append("")
    md.append(
        f"*Generated from graphistrygpt element types v{data['version']} "
        f"on {datetime.now().strftime('%Y-%m-%d')}*"
    )
    md.append("")

    # Table of Contents
    md.append("## Table of Contents")
    md.append("")
    md.append("1. [Overview](#overview)")
    md.append("2. [Element Types](#element-types)")
    for name in sorted(data["element_types"].keys()):
        anchor = name.lower().replace("element", "-element")
        md.append(f"   - [{name}](#{anchor})")
    md.append("3. [Response Patterns](#response-patterns)")
    md.append("4. [Type Detection](#type-detection)")
    md.append("5. [Examples](#examples)")
    md.append("")

    # Overview
    md.append("## Overview")
    md.append("")
    md.append(
        "The beauty of Louie's API is that you don't need different methods "
        "for different capabilities - just ask in natural language and Louie "
        "returns the appropriate response type."
    )
    md.append("")
    md.append("```python")
    md.append("# Simple query, appropriate response")
    md.append(
        'response = client.add_cell(thread.id, "Your request in natural language")'
    )
    md.append("```")
    md.append("")

    # Element Types
    md.append("## Element Types")
    md.append("")

    for name in sorted(data["element_types"].keys()):
        info = data["element_types"][name]
        anchor = name.lower().replace("element", "-element")

        md.append(f"### {name}")
        md.append("")
        md.append(info["description"])
        md.append("")

        # Schema details
        schema = info["schema"]
        if "properties" in schema:
            md.append("**Properties:**")
            md.append("")
            md.extend(generate_property_table(schema["properties"]))
            md.append("")

        # Common queries
        if info.get("common_queries"):
            md.append("**Common Queries:**")
            for query in info["common_queries"]:
                md.append(f'- "{query}"')
            md.append("")

        # Examples
        if info.get("examples"):
            md.append("**Examples:**")
            md.append("")
            for example in info["examples"]:
                md.append(f"*{example['name']}:*")
                md.append("```python")
                # Show the response structure
                md.append("response = client.add_cell(thread.id, query)")
                md.append("# Response structure:")
                md.append(format_json_value(example["value"]))
                md.append("```")
                md.append("")

        # Handling code
        md.append("**Handling:**")
        md.append("```python")

        if name == "TextElement":
            md.append("# Access text content")
            md.append("if response.type == 'TextElement':")
            md.append("    content = response.text")
            md.append("    language = response.language")
            md.append("    print(f'{language}: {content}')")

        elif name == "DfElement":
            md.append("# Extract DataFrame")
            md.append("if hasattr(response, 'to_dataframe'):")
            md.append("    df = response.to_dataframe()")
            md.append("    if df is not None:")
            md.append("        print(f'Retrieved {len(df)} rows')")

        elif name == "GraphElement":
            md.append("# Get visualization URL")
            md.append("if response.type == 'GraphElement':")
            md.append(
                "    viz_url = f'https://hub.graphistry.com/graph/graph.html"
                "?dataset={response.dataset_id}'"
            )
            md.append("    print(f'View visualization: {viz_url}')")

        elif name == "ExceptionElement":
            md.append("# Handle errors")
            md.append("if response.type == 'ExceptionElement':")
            md.append("    print(f'Error: {response.text}')")
            md.append("    if response.traceback:")
            md.append("        print(f'Traceback: {response.traceback}')")

        md.append("```")
        md.append("")

    # Response Patterns
    md.append("## Response Patterns")
    md.append("")

    if "response_patterns" in data:
        for pattern_name, pattern_info in data["response_patterns"].items():
            md.append(f"### {pattern_name.replace('_', ' ').title()}")
            md.append("")
            md.append(pattern_info["description"])
            md.append("")

            if "example" in pattern_info:
                example = pattern_info["example"]
                md.append("**Example:**")
                md.append(f'- Query: "{example.get("query", "N/A")}"')

                if "response_type" in example:
                    md.append(f"- Returns: `{example['response_type']}`")
                elif "response_types" in example:
                    types = ", ".join(f"`{t}`" for t in example["response_types"])
                    md.append(f"- Returns: {types}")

                md.append("")

    # Type Detection
    md.append("## Type Detection")
    md.append("")
    md.append("### Method 1: Type Property")
    md.append("```python")
    md.append("if response.type == 'TextElement':")
    md.append("    # Handle text response")
    md.append("elif response.type == 'DfElement':")
    md.append("    # Handle DataFrame response")
    md.append("elif response.type == 'GraphElement':")
    md.append("    # Handle visualization")
    md.append("elif response.type == 'ExceptionElement':")
    md.append("    # Handle error")
    md.append("```")
    md.append("")

    md.append("### Method 2: Duck Typing")
    md.append("```python")
    md.append("# Check for DataFrame")
    md.append(
        "if hasattr(response, 'to_dataframe') and response.to_dataframe() is not None:"
    )
    md.append("    df = response.to_dataframe()")
    md.append("")
    md.append("# Check for visualization")
    md.append("if hasattr(response, 'dataset_id'):")
    md.append("    viz_url = build_graphistry_url(response.dataset_id)")
    md.append("")
    md.append("# Check for text")
    md.append("if hasattr(response, 'text'):")
    md.append("    content = response.text")
    md.append("```")
    md.append("")

    # Complete Examples
    md.append("## Examples")
    md.append("")

    md.append("### Basic Query")
    md.append("```python")
    md.append("from louieai import LouieClient")
    md.append("")
    md.append("client = LouieClient()")
    md.append("thread = client.create_thread(name='Analysis')")
    md.append("")
    md.append("# Query returns DfElement")
    md.append(
        'response = client.add_cell(thread.id, "Query PostgreSQL for user statistics")'
    )
    md.append("if hasattr(response, 'to_dataframe'):")
    md.append("    df = response.to_dataframe()")
    md.append("    print(df.describe())")
    md.append("```")
    md.append("")

    md.append("### Multi-Element Response")
    md.append("```python")
    md.append("# Complex query returns multiple elements")
    md.append('response = client.add_cell(thread.id, """')
    md.append("    1. Query sales data from ClickHouse")
    md.append("    2. Create a UMAP visualization")
    md.append("    3. Summarize the key findings")
    md.append('""")')
    md.append("")
    md.append("# Handle multiple elements (hypothetical API)")
    md.append("for element in response.elements:")
    md.append("    if element.type == 'DfElement':")
    md.append("        df = element.to_dataframe()")
    md.append("    elif element.type == 'GraphElement':")
    md.append("        print(f'Visualization: {element.dataset_id}')")
    md.append("    elif element.type == 'TextElement':")
    md.append("        print(f'Summary: {element.text}')")
    md.append("```")
    md.append("")

    # Footer
    md.append("## Next Steps")
    md.append("")
    md.append("- See [Query Patterns](../query-patterns.md) for more examples")
    md.append("- Check [Client API](client.md) for method details")
    md.append("- Review [Testing Guide](../testing.md) for integration examples")

    return "\n".join(md)


def main():
    """Import types and generate documentation."""
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "data"
    docs_dir = project_root / "docs" / "api"

    # Load data
    input_file = data_dir / "element_types.json"
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        print("   Copy from graphistrygpt/exports/element_types.json")
        print(
            "   Or use the example: "
            "cp plans/element-types-example.json data/element_types.json"
        )
        return 1

    print(f"📄 Loading element types from: {input_file}")
    data = load_element_types(input_file)

    # Generate docs
    print("📝 Generating markdown documentation...")
    markdown = generate_markdown_docs(data)

    # Write output
    output_file = docs_dir / "response-types-generated.md"
    output_file.write_text(markdown)

    print(f"✅ Generated documentation: {output_file}")
    print(f"   Version: {data['version']}")
    print(f"   Types: {len(data['element_types'])}")
    print("")
    print("Next steps:")
    print("1. Review the generated documentation")
    print("2. Replace docs/api/response-types.md if satisfied")
    print("3. Update with real examples from testing")

    return 0


if __name__ == "__main__":
    exit(main())
