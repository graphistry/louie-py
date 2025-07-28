# Type Export System Design

## Overview

This document outlines the design for an automated type export system between `graphistrygpt` (source of truth) and `louie-py` (consumer for documentation).

## Goals

1. **Accuracy**: Documentation always matches server capabilities
2. **Automation**: Minimal manual intervention
3. **Versioning**: Track changes between versions
4. **Examples**: Include real-world usage examples
5. **Maintainability**: Easy to update and extend

## Architecture

### Components

```
graphistrygpt/                          louie-py/
├── models/elements.py                  ├── scripts/
│   └── Element types (source)          │   └── import_element_types.py
├── scripts/                            ├── data/
│   └── export_element_types.py         │   └── element_types.json
└── exports/                            └── docs/api/
    └── element_types.json                  └── response-types.md (generated)
```

### Data Flow

1. **Export** (graphistrygpt): Extract types → JSON Schema → File
2. **Transfer**: Manual copy or automated PR
3. **Import** (louie-py): Read JSON → Generate docs → Update files

## Export Format

### Schema Structure

```json
{
  "version": "1.0.0",
  "generated_at": "2025-07-27T08:00:00Z",
  "source_version": "git-sha-or-tag",
  "schema_version": "http://json-schema.org/draft-07/schema#",
  "metadata": {
    "description": "Louie.ai element types for API responses",
    "source_repo": "graphistrygpt",
    "export_script": "scripts/export_element_types.py"
  },
  "element_union": {
    // Full discriminated union schema
  },
  "element_types": {
    "TextElement": {
      "schema": { /* JSON Schema */ },
      "description": "Natural language, code, or structured text responses",
      "examples": [
        {
          "name": "Markdown response",
          "value": {
            "type": "TextElement",
            "text": "## Analysis Results\n\nThe data shows...",
            "language": "Markdown"
          }
        },
        {
          "name": "JSON response",
          "value": {
            "type": "TextElement",
            "text": "{\"result\": \"success\"}",
            "language": "JSON"
          }
        }
      ],
      "common_queries": [
        "Summarize the data",
        "Explain the correlation",
        "Generate a report"
      ]
    },
    "DfElement": {
      "schema": { /* JSON Schema */ },
      "description": "DataFrame responses from database queries",
      "examples": [ /* ... */ ],
      "common_queries": [
        "Query PostgreSQL for sales data",
        "Get user statistics from ClickHouse"
      ]
    }
    // ... other element types
  },
  "response_patterns": {
    "single_element": {
      "description": "Most queries return a single element",
      "example": "Query database for user count"
    },
    "multi_element": {
      "description": "Complex queries can return multiple elements",
      "example": "Query data, create visualization, and summarize findings"
    }
  }
}
```

### Versioning Strategy

1. **Semantic Versioning**: Major.Minor.Patch
   - Major: Breaking changes to element structure
   - Minor: New element types or fields
   - Patch: Documentation updates

2. **Compatibility Matrix**:
   ```json
   {
     "compatibility": {
       "1.0.0": "louie-py >= 0.1.0",
       "1.1.0": "louie-py >= 0.2.0"
     }
   }
   ```

3. **Change Log**:
   ```json
   {
     "changes": [
       {
         "version": "1.1.0",
         "date": "2025-07-28",
         "changes": ["Added FooElement", "Deprecated BarElement"]
       }
     ]
   }
   ```

## Implementation Details

### Export Script (graphistrygpt)

Location: `graphistrygpt/scripts/export_element_types.py`

```python
#!/usr/bin/env python3
"""Export Louie.ai element types for documentation."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from graphistrygpt.models.elements import (
    ElementUnion,
    TextElement,
    DfElement,
    GraphElement,
    # ... all element types
)

# Version should be updated for changes
EXPORT_VERSION = "1.0.0"

def get_element_examples() -> Dict[str, list]:
    """Return example instances for each element type."""
    return {
        "TextElement": [
            {
                "name": "Natural language response",
                "value": TextElement(
                    text="Based on the analysis, sales increased 15%",
                    language="Markdown"
                ).model_dump()
            }
        ],
        # ... more examples
    }

def get_common_queries() -> Dict[str, list]:
    """Return common queries that generate each element type."""
    return {
        "TextElement": [
            "Summarize the key findings",
            "Explain the data patterns"
        ],
        "DfElement": [
            "Query PostgreSQL for customer data",
            "Get sales metrics from ClickHouse"
        ],
        # ... more queries
    }

def export_types():
    """Export all element types to JSON Schema format."""
    
    # Get individual schemas
    element_types = {}
    for element_class in ElementUnion.__args__:
        name = element_class.__name__
        element_types[name] = {
            "schema": element_class.model_json_schema(),
            "description": element_class.__doc__ or f"{name} element",
            "examples": get_element_examples().get(name, []),
            "common_queries": get_common_queries().get(name, [])
        }
    
    # Build export
    export_data = {
        "version": EXPORT_VERSION,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source_version": get_git_sha(),
        "schema_version": "http://json-schema.org/draft-07/schema#",
        "metadata": {
            "description": "Louie.ai element types for API responses",
            "source_repo": "graphistrygpt",
            "export_script": "scripts/export_element_types.py"
        },
        "element_union": ElementUnion.model_json_schema(),
        "element_types": element_types,
        "response_patterns": {
            "single_element": {
                "description": "Most queries return a single element",
                "example": "Query database for user count"
            },
            "multi_element": {
                "description": "Complex queries can return multiple elements",
                "example": "Query data, create visualization, and summarize"
            }
        }
    }
    
    # Write to file
    output_path = Path(__file__).parent.parent / "exports" / "element_types.json"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(export_data, f, indent=2, sort_keys=True)
    
    print(f"✅ Exported element types to {output_path}")
    print(f"   Version: {EXPORT_VERSION}")
    print(f"   Types: {len(element_types)}")

if __name__ == "__main__":
    export_types()
```

### Import Script (louie-py)

Location: `louie-py/scripts/import_element_types.py`

```python
#!/usr/bin/env python3
"""Import element types and generate documentation."""

import json
from pathlib import Path
from typing import Any, Dict
import textwrap

def load_element_types(path: Path) -> Dict[str, Any]:
    """Load element types from JSON export."""
    with open(path) as f:
        return json.load(f)

def generate_markdown_docs(data: Dict[str, Any]) -> str:
    """Generate markdown documentation from element types."""
    md = []
    
    # Header
    md.append("# Response Types Reference")
    md.append("")
    md.append("*Generated from graphistrygpt element types*")
    md.append(f"*Version: {data['version']} | Generated: {data['generated_at']}*")
    md.append("")
    
    # Overview
    md.append("## Overview")
    md.append("")
    md.append(data['metadata']['description'])
    md.append("")
    
    # Element types
    md.append("## Element Types")
    md.append("")
    
    for name, info in data['element_types'].items():
        md.append(f"### {name}")
        md.append("")
        md.append(info['description'])
        md.append("")
        
        # Schema details
        schema = info['schema']
        if 'properties' in schema:
            md.append("**Fields:**")
            for field, field_info in schema['properties'].items():
                field_type = field_info.get('type', 'any')
                field_desc = field_info.get('description', '')
                md.append(f"- `{field}` ({field_type}): {field_desc}")
            md.append("")
        
        # Examples
        if info['examples']:
            md.append("**Examples:**")
            for example in info['examples']:
                md.append(f"- {example['name']}:")
                md.append("  ```python")
                md.append(f"  {example['value']}")
                md.append("  ```")
            md.append("")
        
        # Common queries
        if info['common_queries']:
            md.append("**Common Queries:**")
            for query in info['common_queries']:
                md.append(f'- "{query}"')
            md.append("")
    
    return "\n".join(md)

def main():
    """Import types and generate documentation."""
    # Paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    docs_dir = script_dir.parent / "docs" / "api"
    
    # Load data
    input_file = data_dir / "element_types.json"
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        print("   Copy from graphistrygpt/exports/element_types.json")
        return 1
    
    data = load_element_types(input_file)
    
    # Generate docs
    markdown = generate_markdown_docs(data)
    
    # Write output
    output_file = docs_dir / "response-types-generated.md"
    output_file.write_text(markdown)
    
    print(f"✅ Generated documentation: {output_file}")
    print(f"   Version: {data['version']}")
    print(f"   Types: {len(data['element_types'])}")
    
    return 0

if __name__ == "__main__":
    exit(main())
```

## Automation Strategy

### Phase 1: Manual Process
1. Run export script in graphistrygpt
2. Copy JSON file to louie-py
3. Run import script in louie-py
4. Review and commit changes

### Phase 2: Semi-Automated
1. GitHub Action in graphistrygpt runs export on changes
2. Creates PR to louie-py with updated types
3. Human review and merge

### Phase 3: Fully Automated
1. Webhook triggers on graphistrygpt changes
2. Automated compatibility check
3. Auto-merge if compatible
4. Alert on breaking changes

## Backwards Compatibility

### Non-Breaking Changes
- Adding new element types
- Adding optional fields
- Adding examples/documentation

### Breaking Changes (Require Major Version)
- Removing element types
- Removing required fields
- Changing field types
- Renaming discriminator values

### Compatibility Checking
```python
def check_compatibility(old_schema, new_schema):
    """Check if schemas are compatible."""
    # Check all old types still exist
    # Check all required fields still exist
    # Check field types haven't changed
    pass
```

## Testing Strategy

1. **Unit Tests**: Test export/import scripts
2. **Integration Tests**: Test with real element types
3. **Validation Tests**: Ensure generated docs are valid
4. **Compatibility Tests**: Test version compatibility

## Maintenance

### Regular Tasks
- Update examples when new patterns emerge
- Add common queries based on usage
- Version bump for changes
- Monitor for schema drift

### Documentation
- Keep this design doc updated
- Document any deviations
- Track version history

## Success Metrics

1. **Accuracy**: Docs match actual types 100%
2. **Freshness**: Updates within 24 hours
3. **Automation**: < 5 minutes manual work
4. **Quality**: Examples cover 80% use cases

## Next Steps

1. Implement export script
2. Implement import script
3. Test with current types
4. Add to CI pipeline
5. Document process