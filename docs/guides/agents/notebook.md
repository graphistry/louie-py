# Notebook Agent Guide

The Notebook agent works with **Louie notebooks** (your threads of cells on the Louie server): it lists and reads them, copies results between them, and searches their run history. It does not open, run, or convert Jupyter `.ipynb` files.

## Overview

- **NotebookTool** - Read and organize Louie notebooks with natural language

> **Agent name:** the agent is `NotebookTool`, not `NotebookAgent`. Current Louie servers reject the older name with `400 Invalid agent 'NotebookAgent'`.

## What it can do

| Capability | Example |
|---|---|
| List your notebooks | `lui("List my notebooks", agent="NotebookTool")` |
| Read a notebook's cells and results | `lui("Summarize what notebook D_abc123 found", agent="NotebookTool")` |
| Copy a result from another notebook | `lui("Copy the fraud table from notebook D_abc123 into this one", agent="NotebookTool")` |
| Search run history | `lui("Which queries in this notebook failed in the last 2 hours?", agent="NotebookTool")` |

### Creating and editing cells

Creating notebooks and appending, editing, or re-running cells is available only when your Louie server administrator enables notebook editing. It is off by default; when it is off, the agent answers that it cannot make the change (for example, "Notebook not created"):

```python
from louieai.notebook import lui

lui("Create a notebook named 'Weekly triage' with a markdown intro cell", agent="NotebookTool")
lui("Re-run the last cell of notebook D_abc123", agent="NotebookTool")
```

## Usage Examples

```python
from louieai.notebook import lui

# Find earlier work
lui("List my notebooks about login anomalies", agent="NotebookTool")

# Pull context from an earlier investigation into this one
lui("Read notebook D_abc123 and summarize its conclusions", agent="NotebookTool")
lui("Copy the top-talkers table from notebook D_abc123", agent="NotebookTool")

# Debug a long session
lui("Show the tools used and any errors in this notebook's history", agent="NotebookTool")
```

## Working with Jupyter

To generate Python for your own Jupyter notebook, use the [Code Agent](code.md). Each `lui(...)` call in Jupyter already records its question and answer in a Louie notebook, which `lui.url` links to.

## Next Steps

- Learn about the [Code Agent](code.md) for generating and running Python
- See the [Agents Overview](index.md) for choosing an agent
