# Graph Agent Guide

The Graph agents create powerful network visualizations using Graphistry, offering both AI-assisted graph generation and direct graph specification.

## Overview

- **GraphAgent** - AI-powered graph creation from natural language
- **GraphPassthroughAgent** - Direct graph JSON specification
- **GraphUMAPPassthroughAgent** - Graph with UMAP layout algorithm

## GraphAgent (AI-Assisted)

The GraphAgent understands:
- Network relationships in your data
- Optimal visualization layouts
- Node and edge styling based on data attributes
- Graph analysis requirements

### Basic Usage

```python
from louieai.notebook import lui

# Simple network visualization
lui("Create a graph showing connections between users", agent="GraphAgent")

# Hierarchical visualization
lui("Show the organizational hierarchy as a tree graph", agent="GraphAgent")

# Flow visualization
lui("Visualize the data flow between our microservices", agent="GraphAgent")
```

### Security and Fraud Analysis

```python
# Fraud network detection
lui("""
Create a graph showing suspicious transaction patterns
where nodes are accounts and edges are money transfers,
highlighting potential fraud rings
""", agent="GraphAgent")

# Attack path visualization
lui("""
Visualize the network attack paths showing how
an attacker moved laterally through our systems
""", agent="GraphAgent")

# User behavior analysis
lui("""
Show unusual user access patterns as a graph where
nodes are users and resources, edges are access events
""", agent="GraphAgent")
```

### Social Network Analysis

```python
# Community detection
lui("""
Create a social network graph showing communities
and influencers, with node size based on centrality
""", agent="GraphAgent")

# Communication patterns
lui("""
Visualize email communication patterns between departments,
showing volume and frequency with edge weights
""", agent="GraphAgent")

# Collaboration networks
lui("""
Show how teams collaborate on projects with
nodes as people and edges as shared project work
""", agent="GraphAgent")
```

### Supply Chain and Logistics

```python
# Supply chain visualization
lui("""
Create a graph of our supply chain showing
suppliers, warehouses, and distribution centers
with delivery routes and volumes
""", agent="GraphAgent")

# Dependency analysis
lui("""
Visualize software dependencies as a graph
highlighting circular dependencies and version conflicts
""", agent="GraphAgent")

# Process flow
lui("""
Show the manufacturing process flow with
nodes as stages and edges as material movement
""", agent="GraphAgent")
```

## GraphPassthroughAgent (Direct Specification)

For direct control over graph structure and styling:

### Basic Graph Structure

```python
# Direct graph specification
lui("""
{
  "nodes": [
    {"id": "A", "label": "Node A", "size": 10, "color": "blue"},
    {"id": "B", "label": "Node B", "size": 20, "color": "red"},
    {"id": "C", "label": "Node C", "size": 15, "color": "green"}
  ],
  "edges": [
    {"source": "A", "target": "B", "weight": 5},
    {"source": "B", "target": "C", "weight": 3},
    {"source": "C", "target": "A", "weight": 2}
  ]
}
""", agent="GraphPassthroughAgent")
```

### Advanced Styling

```python
# Complex graph with custom styling
lui("""
{
  "nodes": [
    {
      "id": "server1",
      "label": "Web Server",
      "type": "server",
      "cpu_usage": 75,
      "memory": 8192,
      "point_size": 30,
      "point_color": "#FF6B6B",
      "point_icon": "server"
    },
    {
      "id": "db1", 
      "label": "Database",
      "type": "database",
      "connections": 150,
      "point_size": 40,
      "point_color": "#4ECDC4",
      "point_icon": "database"
    }
  ],
  "edges": [
    {
      "source": "server1",
      "target": "db1",
      "requests_per_sec": 1000,
      "latency_ms": 5,
      "edge_weight": 10,
      "edge_color": "#95E1D3",
      "edge_label": "1000 req/s"
    }
  ],
  "bindings": {
    "node_size": "cpu_usage",
    "node_color": "type",
    "edge_weight": "requests_per_sec",
    "edge_color": "latency_ms"
  }
}
""", agent="GraphPassthroughAgent")
```

### Time-based Graphs

```python
# Temporal network
lui("""
{
  "nodes": [
    {"id": "user1", "label": "Alice", "joined_date": "2024-01-01"},
    {"id": "user2", "label": "Bob", "joined_date": "2024-01-15"},
    {"id": "user3", "label": "Carol", "joined_date": "2024-02-01"}
  ],
  "edges": [
    {
      "source": "user1",
      "target": "user2", 
      "timestamp": "2024-01-20T10:30:00",
      "interaction_type": "message"
    },
    {
      "source": "user2",
      "target": "user3",
      "timestamp": "2024-02-05T14:15:00", 
      "interaction_type": "call"
    }
  ],
  "bindings": {
    "edge_color": "interaction_type",
    "point_title": "joined_date"
  }
}
""", agent="GraphPassthroughAgent")
```

## GraphUMAPPassthroughAgent

For graphs with UMAP (Uniform Manifold Approximation and Projection) layout:

```python
# UMAP layout for complex networks
lui("""
{
  "nodes": [...],  
  "edges": [...],
  "layout": {
    "algorithm": "umap",
    "n_neighbors": 15,
    "min_dist": 0.1,
    "metric": "euclidean"
  }
}
""", agent="GraphUMAPPassthroughAgent")
```

## Best Practices

### When to Use Each Agent

**Use GraphAgent when:**
- You want to describe the visualization in natural language
- You need help choosing appropriate visual encodings
- You want automatic layout optimization
- You're exploring data relationships

**Use GraphPassthroughAgent when:**
- You have exact graph structure to visualize
- You need precise control over styling
- You're programmatically generating graphs
- You want specific Graphistry features

### Performance Optimization

```python
# AI optimizes for large graphs
lui("""
Create a graph of our entire user network (1M+ nodes)
but make it performant and highlight only important communities
""", agent="GraphAgent")

# Direct optimization control
lui("""
{
  "nodes": large_node_list,
  "edges": large_edge_list,
  "settings": {
    "render_mode": "gpu",
    "point_size": 2,
    "edge_curvature": 0,
    "edge_opacity": 0.1,
    "strongGravity": true,
    "dissuadeHubs": true
  }
}
""", agent="GraphPassthroughAgent")
```

## Common Patterns

### Fraud Detection Networks

```python
# AI-generated fraud visualization
lui("""
Create a fraud detection graph showing:
- Suspicious accounts as red nodes
- Normal accounts as blue nodes  
- Transaction amounts as edge thickness
- Highlight circular money flows
""", agent="GraphAgent")

# Direct fraud network specification
lui("""
{
  "nodes": fraud_accounts_df.to_dict('records'),
  "edges": suspicious_transactions_df.to_dict('records'),
  "bindings": {
    "node_color": "risk_score",
    "node_size": "transaction_count",
    "edge_weight": "amount",
    "edge_color": "suspicion_level"
  },
  "filters": {
    "risk_score": {"min": 0.7},
    "amount": {"min": 10000}
  }
}
""", agent="GraphPassthroughAgent")
```

### Knowledge Graphs

```python
# AI builds knowledge graph
lui("""
Create a knowledge graph from our documentation showing
how different concepts and systems are related
""", agent="GraphAgent")

# Direct knowledge graph
lui("""
{
  "nodes": [
    {"id": "python", "type": "language", "level": "core"},
    {"id": "pandas", "type": "library", "level": "data"},
    {"id": "graphistry", "type": "library", "level": "viz"},
    {"id": "louieai", "type": "platform", "level": "ai"}
  ],
  "edges": [
    {"source": "pandas", "target": "python", "relation": "requires"},
    {"source": "louieai", "target": "graphistry", "relation": "uses"},
    {"source": "louieai", "target": "pandas", "relation": "processes"}
  ],
  "layout": {
    "algorithm": "hierarchical",
    "direction": "LR"
  }
}
""", agent="GraphPassthroughAgent")
```

### Real-time Monitoring

```python
# AI creates monitoring dashboard
lui("""
Create a real-time infrastructure monitoring graph showing:
- Service health as node colors (green/yellow/red)
- Request flow as edges
- Current load as node size
""", agent="GraphAgent")

# Direct monitoring graph
lui("""
{
  "nodes": services_health_df.to_dict('records'),
  "edges": service_calls_df.to_dict('records'),
  "bindings": {
    "node_color": "health_status",
    "node_size": "cpu_percent",
    "edge_weight": "calls_per_minute",
    "edge_color": "avg_latency_ms"
  },
  "settings": {
    "play": 1000,  # Animate every second
    "showArrows": true,
    "edgeCurvature": 0.2
  }
}
""", agent="GraphPassthroughAgent")
```

## Integration with Other Agents

```python
# Get data from database
lui("Find all related transactions for investigation", agent="PostgresAgent")
transaction_df = lui.df

# Create graph visualization
lui("""
Visualize these transactions as a network showing
money flow patterns and suspicious connections
""", agent="GraphAgent")

# Analyze the graph
lui("What communities or patterns do you see in this network?", agent="LouieAgent")

# Generate report
lui("Create a summary report of the network analysis findings", agent="TextAgent")
```

## Advanced Features

### Custom Encodings

```python
# AI with specific encoding requests
lui("""
Create a graph where:
- Node size represents transaction volume
- Node color shows risk level (gradient from green to red)
- Edge thickness is transaction frequency
- Use force-directed layout with high repulsion
""", agent="GraphAgent")

# Direct encoding control
lui("""
{
  "nodes": nodes_df.to_dict('records'),
  "edges": edges_df.to_dict('records'),
  "encodings": {
    "node": {
      "size": {
        "field": "volume",
        "scale": "log",
        "range": [5, 50]
      },
      "color": {
        "field": "risk_score",
        "scale": "linear",
        "domain": [0, 1],
        "range": ["#00ff00", "#ff0000"]
      }
    },
    "edge": {
      "width": {
        "field": "frequency",
        "scale": "sqrt",
        "range": [1, 10]
      }
    }
  }
}
""", agent="GraphPassthroughAgent")
```

### Graph Analytics

```python
# AI-powered analytics
lui("""
Create a graph and calculate:
- Centrality measures for each node
- Community detection
- Shortest paths between suspicious nodes
""", agent="GraphAgent")

# Include analytics in visualization
lui("""
{
  "nodes": nodes_with_metrics,
  "edges": edges,
  "compute": {
    "pagerank": true,
    "community": "louvain",
    "degree": true
  },
  "bindings": {
    "node_size": "pagerank",
    "node_color": "community"
  }
}
""", agent="GraphPassthroughAgent")
```

## Next Steps

- Learn about other visualization agents in the [Agents Reference](../../reference/agents.md#data-visualization-agents)
- Check the [Query Patterns Guide](../query-patterns.md) for more examples