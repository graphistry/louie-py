# Type Export Integration Guide

This guide explains how to integrate the type export system between graphistrygpt and louie-py to keep documentation synchronized with server capabilities.

## Overview

The type export system automatically generates documentation from Pydantic models in graphistrygpt, ensuring that louie-py documentation always reflects the actual server response types.

## Architecture

```
graphistrygpt                          louie-py
├── models/elements.py                 ├── data/
│   └── Element types (source)         │   └── element_types.json (imported)
├── scripts/                           ├── scripts/
│   └── export_element_types.py        │   └── generate_type_docs.py
└── exports/                           └── docs/api/
    └── element_types.json                 └── response-types.md (generated)
```

## Setup Instructions

### Step 1: Install Export Script in graphistrygpt

1. Copy the export script to graphistrygpt:
   ```bash
   cp louie-py/templates/export_element_types.py graphistrygpt/scripts/
   ```

2. Make it executable:
   ```bash
   chmod +x graphistrygpt/scripts/export_element_types.py
   ```

3. Create exports directory:
   ```bash
   mkdir -p graphistrygpt/exports
   ```

### Step 2: First Export

1. Navigate to graphistrygpt:
   ```bash
   cd graphistrygpt
   ```

2. Run the export script:
   ```bash
   python scripts/export_element_types.py
   ```

3. Verify the export:
   ```bash
   ls -la exports/element_types.json
   ```

### Step 3: Import to louie-py

1. Copy the exported file:
   ```bash
   cp graphistrygpt/exports/element_types.json louie-py/data/
   ```

2. Generate documentation:
   ```bash
   cd louie-py
   uv run python scripts/generate_type_docs.py
   ```

3. Review the generated documentation:
   ```bash
   ls -la docs/api/response-types-generated.md
   ```

## Development Workflow

### When Element Types Change

1. **Update Types** in graphistrygpt:
   - Modify `models/elements.py`
   - Add new element types or fields
   - Update docstrings

2. **Export Types**:
   ```bash
   cd graphistrygpt
   python scripts/export_element_types.py
   ```

3. **Update Version** (if needed):
   - Edit `EXPORT_VERSION` in export script
   - Add changelog entry

4. **Transfer to louie-py**:
   ```bash
   cp graphistrygpt/exports/element_types.json louie-py/data/
   ```

5. **Generate Documentation**:
   ```bash
   cd louie-py
   uv run python scripts/generate_type_docs.py
   ```

6. **Review and Commit**:
   - Check generated documentation
   - Update examples if needed
   - Commit both repos

### Testing New Examples

1. **Add Examples** to export script:
   ```python
   def get_element_examples():
       return {
           "NewElement": [
               {
                   "name": "Example name",
                   "value": NewElement(...).model_dump()
               }
           ]
       }
   ```

2. **Add Common Queries**:
   ```python
   def get_common_queries():
       return {
           "NewElement": [
               "Query pattern that returns NewElement",
               "Another example query"
           ]
       }
   ```

3. **Test Export/Import**:
   ```bash
   # Export
   cd graphistrygpt
   python scripts/export_element_types.py
   
   # Import
   cp exports/element_types.json ../louie-py/data/
   cd ../louie-py
   uv run python scripts/generate_type_docs.py
   ```

## Automation Options

### Option 1: Manual Process (Current)

1. Developer runs export script
2. Copies JSON file
3. Runs import script
4. Reviews and commits

**Pros**: Simple, full control
**Cons**: Manual steps, can be forgotten

### Option 2: GitHub Actions

Create `.github/workflows/export-types.yml` in graphistrygpt:

```yaml
name: Export Element Types

on:
  push:
    paths:
      - 'models/elements.py'
      - 'models/element/**'
  workflow_dispatch:

jobs:
  export-types:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          
      - name: Install dependencies
        run: pip install -e .
        
      - name: Export types
        run: python scripts/export_element_types.py
        
      - name: Create Pull Request to louie-py
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.LOUIE_PY_PAT }}
          path: ../louie-py
          title: 'Update element types from graphistrygpt'
          body: |
            Auto-generated PR from graphistrygpt element type changes.
            
            Changes:
            - Updated element_types.json
            - Regenerated documentation
          branch: update-element-types
```

### Option 3: Git Hooks

Create `graphistrygpt/.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Check if elements.py changed
if git diff --cached --name-only | grep -q "models/elements.py"; then
    echo "Element types changed, running export..."
    python scripts/export_element_types.py
    
    # Stage the export if it changed
    if git diff --name-only | grep -q "exports/element_types.json"; then
        git add exports/element_types.json
        echo "Added updated element_types.json to commit"
    fi
fi
```

## Version Management

### Semantic Versioning

- **Major (1.0.0 → 2.0.0)**: Breaking changes
  - Removed element types
  - Changed required fields
  - Modified discriminator values

- **Minor (1.0.0 → 1.1.0)**: New features
  - Added element types
  - Added optional fields
  - Enhanced examples

- **Patch (1.0.0 → 1.0.1)**: Documentation
  - Updated examples
  - Fixed descriptions
  - Improved queries

### Compatibility Checking

Add to export script:

```python
def check_compatibility(old_file, new_data):
    """Check if new export is compatible with previous version."""
    if not old_file.exists():
        return True  # First export
        
    with open(old_file) as f:
        old_data = json.load(f)
    
    # Check for removed types
    old_types = set(old_data['element_types'].keys())
    new_types = set(new_data['element_types'].keys())
    removed = old_types - new_types
    
    if removed:
        print(f"⚠️  Breaking change: Removed types: {removed}")
        return False
    
    # Check for changed required fields
    for type_name in old_types & new_types:
        old_schema = old_data['element_types'][type_name]['schema']
        new_schema = new_data['element_types'][type_name]['schema']
        
        old_required = old_schema.get('required', [])
        new_required = new_schema.get('required', [])
        
        if set(old_required) != set(new_required):
            print(f"⚠️  Breaking change in {type_name}: Required fields changed")
            return False
    
    return True
```

## Troubleshooting

### Common Issues

1. **Import Errors in Export Script**:
   ```bash
   # Ensure graphistrygpt dependencies are installed
   cd graphistrygpt
   pip install -e .
   ```

2. **JSON Schema Validation Errors**:
   ```bash
   # Check Pydantic version compatibility
   pip list | grep pydantic
   ```

3. **Missing Examples**:
   - Add examples to `get_element_examples()`
   - Ensure all element types have at least one example

4. **Documentation Generation Fails**:
   ```bash
   # Check JSON format
   python -m json.tool data/element_types.json
   
   # Run with debug output
   python scripts/generate_type_docs.py --verbose
   ```

### Validation Script

Create `louie-py/scripts/validate_types.py`:

```python
#!/usr/bin/env python3
"""Validate imported element types."""

import json
from pathlib import Path

def validate_export():
    """Validate the exported types JSON."""
    data_file = Path("data/element_types.json")
    
    if not data_file.exists():
        print("❌ No element_types.json found")
        return False
    
    with open(data_file) as f:
        data = json.load(f)
    
    required_fields = ['version', 'element_types', 'element_union']
    for field in required_fields:
        if field not in data:
            print(f"❌ Missing required field: {field}")
            return False
    
    print(f"✅ Valid export with {len(data['element_types'])} types")
    return True

if __name__ == "__main__":
    validate_export()
```

## Best Practices

1. **Always Test the Full Pipeline**:
   ```bash
   # Complete test
   cd graphistrygpt && python scripts/export_element_types.py
   cp exports/element_types.json ../louie-py/data/
   cd ../louie-py && uv run python scripts/generate_type_docs.py
   ```

2. **Keep Examples Realistic**:
   - Use actual field values
   - Include edge cases
   - Show common use patterns

3. **Document Breaking Changes**:
   - Update version appropriately
   - Add changelog entries
   - Notify users in advance

4. **Regular Maintenance**:
   - Update examples based on real usage
   - Add new query patterns
   - Remove obsolete examples

## Security Considerations

1. **No Sensitive Data**:
   - Don't include real credentials in examples
   - Use placeholder values
   - Sanitize any real data

2. **Repository Access**:
   - Use deploy keys for automation
   - Limit permissions to necessary files
   - Review automated PRs

3. **Validation**:
   - Validate JSON before committing
   - Check for schema completeness
   - Test generated documentation

## Success Metrics

- **Accuracy**: Documentation matches actual types 100%
- **Freshness**: Updates within 24 hours of changes
- **Automation**: < 5 minutes manual work per update
- **Quality**: Examples cover 80% of use cases
- **Reliability**: Zero failed exports/imports

This integration ensures that louie-py documentation stays perfectly synchronized with graphistrygpt capabilities while minimizing manual maintenance overhead.