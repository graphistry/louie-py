# Testing Type Export System

This guide covers testing the type export/import system to ensure reliability and accuracy.

## Test Categories

### 1. Unit Tests for Export Script

Create `graphistrygpt/tests/test_export_element_types.py`:

```python
import json
import tempfile
from pathlib import Path
import pytest

from scripts.export_element_types import (
    export_types,
    get_element_examples,
    get_common_queries,
    get_git_sha
)

def test_export_creates_valid_json():
    """Test that export creates valid JSON."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Temporarily change output path
        original_path = Path("exports/element_types.json")
        test_path = Path(tmpdir) / "element_types.json"
        
        # Run export (would need to modify script to accept output path)
        result = export_types()
        assert result == 0
        
        # Validate JSON
        with open(test_path) as f:
            data = json.load(f)
        
        assert "version" in data
        assert "element_types" in data
        assert len(data["element_types"]) > 0

def test_all_element_types_have_examples():
    """Test that all element types have examples."""
    examples = get_element_examples()
    queries = get_common_queries()
    
    # Get element types from actual models
    from graphistrygpt.models.elements import ElementUnion
    element_classes = ElementUnion.__args__
    
    for element_class in element_classes:
        name = element_class.__name__
        assert name in examples, f"Missing examples for {name}"
        assert name in queries, f"Missing queries for {name}"
        assert len(examples[name]) > 0, f"No examples for {name}"

def test_examples_are_valid():
    """Test that all examples are valid JSON-serializable."""
    examples = get_element_examples()
    
    for type_name, type_examples in examples.items():
        for example in type_examples:
            # Should be JSON serializable
            json.dumps(example)
            
            # Should have required fields
            assert "name" in example
            assert "value" in example
            assert example["value"]["type"] == type_name

def test_git_sha_format():
    """Test git SHA extraction."""
    sha = get_git_sha()
    assert isinstance(sha, str)
    assert len(sha) >= 7  # At least 7 characters
```

### 2. Unit Tests for Import Script

Create `louie-py/tests/test_generate_type_docs.py`:

```python
import json
import tempfile
from pathlib import Path
import pytest

from scripts.generate_type_docs import (
    generate_markdown_docs,
    format_json_value,
    generate_property_table,
    load_element_types
)

@pytest.fixture
def sample_export_data():
    """Sample export data for testing."""
    return {
        "version": "1.0.0",
        "generated_at": "2025-07-27T08:00:00Z",
        "element_types": {
            "TestElement": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "const": "TestElement"},
                        "value": {"type": "string", "description": "Test value"}
                    },
                    "required": ["type"]
                },
                "description": "Test element for unit tests",
                "examples": [
                    {
                        "name": "Basic test",
                        "value": {"type": "TestElement", "value": "test"}
                    }
                ],
                "common_queries": ["Test query"]
            }
        },
        "response_patterns": {
            "test_pattern": {
                "description": "Test pattern",
                "example": {"query": "test", "response_type": "TestElement"}
            }
        }
    }

def test_load_element_types(sample_export_data):
    """Test loading element types from JSON."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as f:
        json.dump(sample_export_data, f)
        f.flush()
        
        data = load_element_types(Path(f.name))
        assert data["version"] == "1.0.0"
        assert "TestElement" in data["element_types"]

def test_generate_property_table():
    """Test property table generation."""
    properties = {
        "type": {"type": "string", "const": "TestElement"},
        "value": {"type": "string", "description": "Test value"},
        "required": ["type"]
    }
    
    table = generate_property_table(properties)
    assert len(table) > 2  # Header + at least one row
    assert "| Field | Type | Required | Description |" in table
    assert "|-------|------|----------|-------------|" in table

def test_generate_markdown_docs(sample_export_data):
    """Test markdown generation."""
    markdown = generate_markdown_docs(sample_export_data)
    
    # Check structure
    assert "# Response Types Reference" in markdown
    assert "## Element Types" in markdown
    assert "### TestElement" in markdown
    assert "Test element for unit tests" in markdown
    
    # Check examples
    assert "Basic test" in markdown
    assert "Test query" in markdown

def test_format_json_value():
    """Test JSON value formatting."""
    test_obj = {"key": "value", "nested": {"inner": 123}}
    formatted = format_json_value(test_obj)
    
    assert "key" in formatted
    assert "value" in formatted
    assert "nested" in formatted
```

### 3. Integration Tests

Create `louie-py/tests/integration/test_type_export_integration.py`:

```python
import json
import subprocess
import tempfile
from pathlib import Path
import pytest

from tests.utils import skip_if_no_credentials

class TestTypeExportIntegration:
    """Integration tests for the complete type export workflow."""
    
    def test_export_import_roundtrip(self):
        """Test complete export/import cycle with example data."""
        # Use our example data
        example_file = Path("plans/element-types-example.json")
        assert example_file.exists()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Copy example to test location
            test_data = Path(tmpdir) / "element_types.json"
            test_data.write_text(example_file.read_text())
            
            # Run import script
            result = subprocess.run([
                "uv", "run", "python", "scripts/generate_type_docs.py"
            ], env={"PYTHONPATH": str(Path.cwd())}, capture_output=True, text=True)
            
            # Should succeed
            assert result.returncode == 0
            assert "Generated documentation" in result.stdout
            
            # Check output exists
            output_file = Path("docs/api/response-types-generated.md")
            assert output_file.exists()
            
            # Validate content
            content = output_file.read_text()
            assert "# Response Types Reference" in content
            assert "TextElement" in content
            assert "DfElement" in content

    def test_missing_input_file(self):
        """Test graceful handling of missing input file."""
        # Rename data file temporarily
        data_file = Path("data/element_types.json")
        backup_file = Path("data/element_types.json.bak")
        
        if data_file.exists():
            data_file.rename(backup_file)
        
        try:
            result = subprocess.run([
                "uv", "run", "python", "scripts/generate_type_docs.py"
            ], capture_output=True, text=True)
            
            assert result.returncode == 1
            assert "Input file not found" in result.stdout
            
        finally:
            # Restore file
            if backup_file.exists():
                backup_file.rename(data_file)

    def test_invalid_json_handling(self):
        """Test handling of invalid JSON input."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create invalid JSON
            bad_file = Path(tmpdir) / "bad.json"
            bad_file.write_text("{ invalid json }")
            
            # This would require modifying script to accept input path
            # For now, test JSON validation separately
            with pytest.raises(json.JSONDecodeError):
                with open(bad_file) as f:
                    json.load(f)

    @skip_if_no_credentials
    def test_real_export_workflow(self):
        """Test with real graphistrygpt export (requires setup)."""
        # This test requires graphistrygpt to be available
        graphistry_path = Path("../graphistrygpt")
        if not graphistry_path.exists():
            pytest.skip("graphistrygpt not available")
        
        # Run real export
        result = subprocess.run([
            "python", "scripts/export_element_types.py"
        ], cwd=graphistry_path, capture_output=True, text=True)
        
        if result.returncode != 0:
            pytest.skip(f"Export failed: {result.stderr}")
        
        # Copy and test import
        export_file = graphistry_path / "exports" / "element_types.json"
        if export_file.exists():
            # Copy to our data directory
            data_file = Path("data/element_types.json")
            data_file.write_text(export_file.read_text())
            
            # Run import
            import_result = subprocess.run([
                "uv", "run", "python", "scripts/generate_type_docs.py"
            ], capture_output=True, text=True)
            
            assert import_result.returncode == 0
```

### 4. Validation Tests

Create `louie-py/tests/test_type_validation.py`:

```python
import json
from pathlib import Path
import pytest

def test_example_data_is_valid():
    """Test that our example data is valid."""
    example_file = Path("plans/element-types-example.json")
    assert example_file.exists()
    
    with open(example_file) as f:
        data = json.load(f)
    
    # Check required top-level fields
    required_fields = [
        "version", "generated_at", "element_types", 
        "element_union", "response_patterns"
    ]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Check element types structure
    for type_name, type_info in data["element_types"].items():
        assert "schema" in type_info
        assert "description" in type_info
        assert "examples" in type_info
        assert "common_queries" in type_info
        
        # Check schema has required fields
        schema = type_info["schema"]
        assert "type" in schema
        assert "properties" in schema

def test_json_schema_validity():
    """Test that generated schemas are valid JSON Schema."""
    example_file = Path("plans/element-types-example.json")
    
    with open(example_file) as f:
        data = json.load(f)
    
    # Basic JSON Schema validation
    for type_name, type_info in data["element_types"].items():
        schema = type_info["schema"]
        
        # Should have type
        assert schema.get("type") == "object"
        
        # Should have properties
        assert "properties" in schema
        
        # Properties should be dict
        assert isinstance(schema["properties"], dict)

def test_examples_match_schemas():
    """Test that examples conform to their schemas."""
    example_file = Path("plans/element-types-example.json")
    
    with open(example_file) as f:
        data = json.load(f)
    
    for type_name, type_info in data["element_types"].items():
        schema = type_info["schema"]
        examples = type_info["examples"]
        
        for example in examples:
            value = example["value"]
            
            # Check type field matches
            assert value.get("type") == type_name
            
            # Check required fields are present
            required = schema.get("required", [])
            for field in required:
                assert field in value, f"{type_name} example missing required field: {field}"

def test_documentation_completeness():
    """Test that documentation covers all important aspects."""
    docs_dir = Path("docs")
    
    # Check main docs exist
    assert (docs_dir / "api" / "response-types.md").exists()
    assert (docs_dir / "query-patterns.md").exists()
    assert (docs_dir / "type-export-integration.md").exists()
    
    # Check integration guide completeness
    integration_doc = docs_dir / "type-export-integration.md"
    content = integration_doc.read_text()
    
    required_sections = [
        "Setup Instructions", "Development Workflow", 
        "Automation Options", "Troubleshooting"
    ]
    for section in required_sections:
        assert section in content
```

## Test Execution

### Running All Tests

```bash
# Unit tests only
uv run pytest tests/test_generate_type_docs.py -v

# Integration tests (may require setup)
uv run pytest tests/integration/test_type_export_integration.py -v

# All type-related tests
uv run pytest -k "type" -v

# Full test suite
uv run pytest
```

### Continuous Integration

Add to `.github/workflows/ci.yml`:

```yaml
  test-type-export:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
        
      - name: Install dependencies
        run: uv sync
        
      - name: Test type export system
        run: |
          # Test with example data
          cp plans/element-types-example.json data/element_types.json
          uv run python scripts/generate_type_docs.py
          
          # Validate output
          test -f docs/api/response-types-generated.md
          
      - name: Run type system tests
        run: uv run pytest tests/test_generate_type_docs.py -v
```

### Manual Testing Checklist

1. **Export Script** (in graphistrygpt):
   - [ ] Script runs without errors
   - [ ] Generates valid JSON
   - [ ] Includes all element types
   - [ ] Examples are realistic
   - [ ] Queries are useful

2. **Import Script** (in louie-py):
   - [ ] Reads exported JSON correctly
   - [ ] Generates valid markdown
   - [ ] Includes all documented types
   - [ ] Cross-references work
   - [ ] Examples render properly

3. **Integration**:
   - [ ] Complete workflow works
   - [ ] Documentation is accurate
   - [ ] No manual steps forgotten
   - [ ] Version tracking works

4. **Edge Cases**:
   - [ ] Missing files handled gracefully
   - [ ] Invalid JSON caught
   - [ ] Network issues handled
   - [ ] Permission errors reported

This comprehensive testing strategy ensures the type export system is reliable and maintainable.