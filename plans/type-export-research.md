# Type Export Research for louie-py

## Overview

We need to export element types from `graphistrygpt` to keep `louie-py` documentation in sync with server capabilities. The types are Pydantic models in `graphistrygpt/models/elements.py`.

## Current State

### Element Types in graphistrygpt
- All element types inherit from `BlockValue` (Pydantic BaseModel)
- Main union type: `ElementUnion` with discriminator field "type"
- Types include:
  - `TextElement` - Natural language, code, JSON responses
  - `DfElement` / `DfElementFlat` - DataFrame results
  - `GraphElement` / `GraphElementFlat` - Graphistry visualizations
  - `PerspectiveElement` - Perspective charts
  - `KeplerElement` - Kepler.gl maps
  - `ExceptionElement` - Error information
  - `Base64ImageElement` - Generated images
  - `InputGroupElement` - Interactive inputs
  - `CallElement` - Agent call records

### Key Observations
1. Uses Pydantic with discriminated unions
2. Has "Flat" versions for serialization (DfElementFlat, GraphElementFlat)
3. Custom serializers for frontend vs disk modes
4. Rich type information with Literal types

## Industry Best Practices Research

### 1. Pydantic JSON Schema Export

**Approach**: Use Pydantic's built-in JSON Schema generation

```python
from pydantic import BaseModel
model_schema = ElementUnion.model_json_schema()
```

**Pros**:
- Built into Pydantic
- Generates standard JSON Schema
- Preserves discriminated unions
- Includes descriptions from docstrings

**Cons**:
- May need post-processing for cross-repo use
- Complex nested schemas can be verbose

**Examples**:
- FastAPI uses this for OpenAPI generation
- Many API documentation tools consume JSON Schema

### 2. TypedDict Export

**Approach**: Convert Pydantic models to TypedDict for type stubs

**Pros**:
- Pure Python typing
- Works with mypy/pyright
- Can generate .pyi files

**Cons**:
- Loses runtime validation
- Manual conversion needed
- Less rich than Pydantic

### 3. OpenAPI/Swagger Approach

**Approach**: Generate OpenAPI spec with schemas

**Pros**:
- Industry standard
- Great tooling ecosystem
- Can generate client code

**Cons**:
- Overkill for just type definitions
- More complex than needed

### 4. Custom JSON Export

**Approach**: Create custom export format optimized for our use case

```python
{
  "version": "1.0.0",
  "timestamp": "2025-07-27T00:00:00Z",
  "types": {
    "TextElement": {
      "fields": {...},
      "description": "...",
      "examples": [...]
    }
  }
}
```

**Pros**:
- Full control
- Can include examples
- Optimized for doc generation

**Cons**:
- Requires custom implementation
- Non-standard format

## Recommended Approach

### Phase 1: Pydantic JSON Schema Export

1. **Export Script** (`graphistrygpt/scripts/export_element_types.py`):
   ```python
   from graphistrygpt.models.elements import ElementUnion
   import json
   from datetime import datetime
   
   schema = {
       "version": "1.0.0",
       "generated_at": datetime.utcnow().isoformat(),
       "element_union": ElementUnion.model_json_schema(),
       "element_types": {}
   }
   
   # Export individual types for easier consumption
   for element_type in ElementUnion.__args__:
       schema["element_types"][element_type.__name__] = element_type.model_json_schema()
   
   with open("element_types.json", "w") as f:
       json.dump(schema, f, indent=2)
   ```

2. **Import Script** (`louie-py/scripts/generate_type_docs.py`):
   ```python
   import json
   from pathlib import Path
   
   def generate_markdown_from_schema(schema):
       # Generate markdown documentation
       # Include field types, descriptions, examples
       pass
   ```

### Phase 2: Enhanced Export with Examples

Add example values and use cases to the export:

```python
{
  "TextElement": {
    "schema": {...},
    "examples": [
      {
        "description": "Natural language response",
        "value": {"type": "TextElement", "text": "Analysis complete", "language": "Markdown"}
      }
    ],
    "common_queries": [
      "Summarize the data",
      "Explain the correlation"
    ]
  }
}
```

### Phase 3: Automation

1. GitHub Action in graphistrygpt to export on changes
2. Automated PR to louie-py when types change
3. Version tracking between repos

## Tools for Documentation Generation

### 1. mkdocstrings
- Can work with JSON Schema
- Generate API docs from schemas
- Already in our stack

### 2. jsonschema2md
- Converts JSON Schema to Markdown
- Simple and effective
- Can be customized

### 3. Custom Jinja2 Templates
- Full control over output
- Can include examples
- Easy to maintain

## Implementation Plan

1. **Start Simple**: Basic JSON Schema export
2. **Add Examples**: Enhance with real-world examples
3. **Automate**: CI/CD integration
4. **Iterate**: Improve based on usage

## Decision: Use Pydantic JSON Schema

**Rationale**:
- Leverages existing Pydantic features
- Standard format with good tooling
- Can be enhanced incrementally
- FastAPI/Pydantic ecosystem compatibility

**Next Steps**:
1. Create export script in graphistrygpt
2. Create import/doc generation in louie-py
3. Test with current element types
4. Add examples and query patterns
5. Automate the process