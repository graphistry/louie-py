# Notebook Agent Guide

The Notebook agent works with Louie notebooks (the threads of cells on your Louie server): it finds, reads, and reuses earlier notebooks, and can create, edit, and run cells.

## Overview

- **NotebookTool** - AI-powered Louie notebook reading, editing, and execution

## NotebookTool

The NotebookTool understands:
- Notebook structure and cells
- Code execution order
- Markdown documentation
- Output handling and display

Reading notebooks, listing them, copying results between them, and searching their run history always work. Creating notebooks and adding, editing, or running cells require notebook editing to be enabled on your Louie server (it is off by default); without it, the agent has no tools to make the change.

### Basic Usage

```python
from louieai.notebook import lui

# Create new notebook
lui("Create a new notebook for data analysis", agent="NotebookTool")

# Add cells
lui("Add a code cell that imports pandas and numpy", agent="NotebookTool")

# Execute notebook
lui("Run all cells in the current notebook", agent="NotebookTool")
```

### Notebook Creation

```python
# Data science notebook
lui("""
Create a data science notebook with:
- Title and description markdown cell
- Import statements cell
- Data loading cell
- Analysis cells
- Visualization cells
""", agent="NotebookTool")

# Tutorial notebook
lui("""
Create a tutorial notebook explaining:
- Concept introduction (markdown)
- Code example
- Exercise for the reader
- Solution (hidden initially)
""", agent="NotebookTool")

# Report notebook
lui("""
Generate a report notebook containing:
- Executive summary
- Data analysis with code
- Visualizations
- Conclusions and recommendations
""", agent="NotebookTool")
```

### Cell Management

```python
# Add cells
lui("""
Add a new cell after the current one that:
- Loads data from CSV
- Shows first 5 rows
- Displays basic statistics
""", agent="NotebookTool")

# Edit cells
lui("""
Update the visualization cell to:
- Use seaborn instead of matplotlib
- Add proper labels and title
- Save the figure
""", agent="NotebookTool")

```

### Code Execution

```python
# Run specific cells
lui("""
Execute:
- All data loading cells
- Skip visualization cells
""", agent="NotebookTool")

# Parameterized execution
lui("""
Run notebook with parameters:
- date_range = "2024-01-01 to 2024-12-31"
- include_details = True
""", agent="NotebookTool")

# Error handling
lui("""
Run notebook and:
- Continue on errors
- Log failed cells
- Mark problematic cells
""", agent="NotebookTool")
```

### Documentation

```python
# Add documentation
lui("""
Document this notebook:
- Add overview at the top
- Explain each code section
- Include example outputs
- Add references
""", agent="NotebookTool")

# Tidy for readers
lui("""
Tidy this notebook for readers:
- Rewrite debug cells as short notes
- Add a summary cell at the top
- Keep only key outputs
""", agent="NotebookTool")

```

## Common Patterns

### Data Analysis Workflow

```python
# Complete analysis notebook
lui("""
Create a complete analysis notebook:
1. Data loading and validation
2. Exploratory data analysis
3. Feature engineering
4. Statistical analysis
5. Visualizations
6. Export results
""", agent="NotebookTool")

# Reproducible research
lui("""
Set up reproducible notebook:
- Environment setup cell
- Random seed setting
- Data versioning
- Results checksums
""", agent="NotebookTool")
```

### Machine Learning Pipeline

```python
# ML notebook template
lui("""
Create ML pipeline notebook:
1. Data preprocessing
2. Train/test split
3. Model training
4. Evaluation metrics
5. Hyperparameter tuning
6. Final predictions
""", agent="NotebookTool")

# Experiment tracking
lui("""
Add experiment tracking:
- Log parameters
- Track metrics
- Save model artifacts
- Compare runs
""", agent="NotebookTool")
```

### Reporting and Dashboards

```python
# Automated reports
lui("""
Generate weekly report notebook:
- Pull latest data
- Run standard analyses
- Create visualizations
- Format for email
""", agent="NotebookTool")

# Interactive dashboards
lui("""
Create dashboard notebook with:
- Parameter cells
- Query cells
- Interactive plots
""", agent="NotebookTool")
```

## Advanced Features

### Template Management

```python
# Create templates
lui("""
Copy this notebook into a new template notebook for:
- Data quality checks
- Remove specific values
- Keep structure and code
- Mark customizable sections
""", agent="NotebookTool")

# Apply templates
lui("""
Create new notebook from template:
- Use analysis template
- Fill in project parameters
- Update data sources
- Customize visualizations
""", agent="NotebookTool")
```

### Preparing to Share

```python
# Clean outputs
lui("""
Prepare notebook for sharing:
- Remove sensitive data
- Check for credentials
- Add license header
""", agent="NotebookTool")
```

### Collaboration Features

```python
# Review preparation
lui("""
Prepare for code review:
- Add docstrings
- Include type hints
- Add unit tests cells
- Document assumptions
""", agent="NotebookTool")
```

## Integration with Other Agents

```python
# Generate analysis code
lui("Write code to analyze customer churn", agent="CodeAgent")

# Create notebook from code
lui("""
Create a notebook from this analysis:
- Split into logical cells
- Add markdown explanations
- Include visualizations
- Make it runnable
""", agent="NotebookTool")

# Query data
lui("Get customer data for analysis", agent="PostgresAgent")

# Document findings
lui("Add conclusions based on the analysis", agent="TextAgent")
```

## Best Practices

### Cell Organization

```python
# Logical structure
lui("""
Organize notebook with:
- Clear section headers
- One concept per cell
- Imports at the top
- Helper functions grouped
- Main analysis flow
- Results at the end
""", agent="NotebookTool")
```

### Performance

```python
# Optimize execution
lui("""
Optimize notebook performance:
- Cache expensive operations
- Use efficient data structures
- Limit output size
- Add progress indicators
""", agent="NotebookTool")
```

### Maintainability

```python
# Future-proof notebooks
lui("""
Make notebook maintainable:
- Pin dependency versions
- Use configuration files
- Parameterize paths
- Add error handling
- Include tests
""", agent="NotebookTool")
```

## Next Steps

- Learn about [Code Agent](code.md) for generating notebook code
- Explore [TableAI Agent](tableai.md) for data analysis in notebooks
- See [Mermaid Agent](mermaid.md) for adding diagrams to notebooks
- Check the [Query Patterns Guide](../query-patterns.md) for more examples