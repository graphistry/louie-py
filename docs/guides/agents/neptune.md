# Neptune Agent Guide

Access AWS Neptune graph database using Cypher queries.

## Overview

- **NeptuneAgent** - AI-powered natural language to Cypher
- **NeptunePassthroughAgent** - Direct Cypher execution

## Usage Examples

```python
# AI-assisted graph queries  
lui("Find users connected to user123", agent="NeptuneAgent")

# Direct Cypher
lui("MATCH (u:User)-[:PURCHASED]->(p:Product) RETURN u.name, p.name", 
    agent="NeptunePassthroughAgent")
```

## Common Patterns

- Graph traversals and path finding
- Community detection
- Recommendation engines
- Fraud network analysis

## Integration

Query graph data, then visualize with GraphAgent or analyze with TableAIAgent.