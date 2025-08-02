# Perspective Agent Guide

The Perspective agents create powerful interactive data tables and visualizations using the Perspective.js library, offering high-performance analytics on large datasets.

## Overview

- **PerspectiveAgent** - AI-powered table and chart creation from natural language
- **PerspectivePassthroughAgent** - Direct Perspective configuration without AI interpretation

## PerspectiveAgent (AI-Assisted)

The PerspectiveAgent understands:
- Data table structures and relationships
- Aggregation and pivot operations
- Chart type selection based on data
- Interactive filtering and sorting

### Basic Usage

```python
from louieai.notebook import lui

# Simple data table
lui("Create an interactive table of sales data", agent="PerspectiveAgent")

# Pivot table analysis
lui("Show revenue by product category and region as a pivot table", agent="PerspectiveAgent")

# Time series visualization
lui("Display monthly trends with interactive filtering", agent="PerspectiveAgent")
```

### Business Analytics

```python
# Executive dashboard
lui("""
Create an executive dashboard showing:
- Revenue by region (map)
- Top products (bar chart)
- Monthly trends (line chart)
- Customer segments (treemap)
""", agent="PerspectiveAgent")

# Financial analysis
lui("""
Build a P&L statement view with:
- Drill-down capabilities by department
- Year-over-year comparison
- Variance analysis highlighting
""", agent="PerspectiveAgent")

# Sales performance
lui("""
Create a sales leaderboard with:
- Rep performance metrics
- Goal attainment visualization
- Sortable and filterable columns
""", agent="PerspectiveAgent")
```

### Real-time Analytics

```python
# Live trading dashboard
lui("""
Build a real-time trading dashboard showing:
- Current positions with P&L
- Market data with sparklines
- Risk metrics with color coding
""", agent="PerspectiveAgent")

# Operations monitoring
lui("""
Create a live operations dashboard displaying:
- Service health status
- Request volumes over time
- Error rates with alerts
""", agent="PerspectiveAgent")

# IoT sensor data
lui("""
Visualize streaming sensor data with:
- Real-time updates
- Anomaly highlighting
- Historical comparison
""", agent="PerspectiveAgent")
```

### Data Exploration

```python
# Multi-dimensional analysis
lui("""
Create an exploration view where users can:
- Drag and drop dimensions
- Switch between chart types
- Apply complex filters
- Export filtered data
""", agent="PerspectiveAgent")

# Cohort analysis
lui("""
Build a cohort retention table with:
- Color-coded retention rates
- Expandable cohort details
- Time period selection
""", agent="PerspectiveAgent")

# A/B test results
lui("""
Display A/B test results with:
- Statistical significance indicators
- Confidence intervals
- Segment breakdowns
""", agent="PerspectiveAgent")
```

## PerspectivePassthroughAgent (Direct Configuration)

For direct Perspective configuration with full control:

### Basic Configuration

```python
# Direct table configuration
lui("""
{
  "plugin": "datagrid",
  "columns": ["date", "product", "revenue", "quantity"],
  "aggregates": {
    "revenue": "sum",
    "quantity": "sum"
  },
  "sort": [["revenue", "desc"]],
  "filter": [["date", ">=", "2024-01-01"]]
}
""", agent="PerspectivePassthroughAgent")
```

### Advanced Pivot Tables

```python
# Complex pivot configuration
lui("""
{
  "plugin": "datagrid",
  "row_pivots": ["region", "product_category"],
  "column_pivots": ["quarter"],
  "columns": ["revenue", "profit_margin", "units_sold"],
  "aggregates": {
    "revenue": "sum",
    "profit_margin": "avg",
    "units_sold": "sum"
  },
  "sort": [["revenue", "desc"]],
  "plugin_config": {
    "columns": {
      "revenue": {"number_format": "currency"},
      "profit_margin": {"number_format": "percentage"},
      "units_sold": {"number_format": "integer"}
    }
  }
}
""", agent="PerspectivePassthroughAgent")
```

### Chart Visualizations

```python
# Multi-series line chart
lui("""
{
  "plugin": "y_line",
  "row_pivots": ["product_line"],
  "columns": ["date", "revenue"],
  "aggregates": {
    "revenue": "sum"
  },
  "sort": [["date", "asc"]],
  "plugin_config": {
    "legend": {
      "position": "top"
    },
    "axes": {
      "y": {
        "label": "Revenue ($)",
        "format": "currency"
      },
      "x": {
        "label": "Date",
        "format": "date"
      }
    }
  }
}
""", agent="PerspectivePassthroughAgent")

# Heatmap visualization
lui("""
{
  "plugin": "heatmap",
  "row_pivots": ["hour_of_day"],
  "column_pivots": ["day_of_week"],
  "columns": ["transaction_count"],
  "aggregates": {
    "transaction_count": "sum"
  },
  "plugin_config": {
    "color_scheme": "viridis",
    "show_values": true
  }
}
""", agent="PerspectivePassthroughAgent")
```

### Custom Calculations

```python
# Calculated columns
lui("""
{
  "plugin": "datagrid",
  "columns": ["revenue", "cost", "profit", "margin"],
  "expressions": {
    "profit": "\"revenue\" - \"cost\"",
    "margin": "(\"revenue\" - \"cost\") / \"revenue\" * 100"
  },
  "aggregates": {
    "revenue": "sum",
    "cost": "sum",
    "profit": "sum",
    "margin": "avg"
  },
  "plugin_config": {
    "columns": {
      "margin": {
        "number_format": "percentage",
        "color_mode": "gradient",
        "gradient": {
          "positive": "#00ff00",
          "negative": "#ff0000"
        }
      }
    }
  }
}
""", agent="PerspectivePassthroughAgent")
```

## Best Practices

### When to Use Each Agent

**Use PerspectiveAgent when:**
- You want to describe visualizations in business terms
- You need help choosing appropriate chart types
- You want automatic aggregation setup
- You're exploring data interactively

**Use PerspectivePassthroughAgent when:**
- You have exact visualization requirements
- You need custom calculated fields
- You want specific formatting control
- You're building reusable dashboards

### Performance Optimization

```python
# AI optimizes for large datasets
lui("""
Create a high-performance view of our million-row
transaction dataset with smart aggregations
""", agent="PerspectiveAgent")

# Direct optimization settings
lui("""
{
  "plugin": "datagrid",
  "columns": ["date", "amount", "category"],
  "aggregates": {
    "amount": "sum"
  },
  "row_pivots": ["category"],
  "settings": {
    "render_threshold": 50000,
    "virtual_mode": true,
    "lazy_load": true
  }
}
""", agent="PerspectivePassthroughAgent")
```

### Interactive Features

```python
# AI adds interactivity
lui("""
Make this sales dashboard interactive with:
- Clickable drill-downs
- Cross-filtering between charts
- Export capabilities
""", agent="PerspectiveAgent")

# Direct interaction config
lui("""
{
  "plugin": "datagrid",
  "selectable": true,
  "editable": false,
  "plugin_config": {
    "exportable": true,
    "filter_dropdown": true,
    "column_toggles": true,
    "row_selection": true,
    "context_menu": {
      "enabled": true,
      "items": ["copy", "export", "reset"]
    }
  }
}
""", agent="PerspectivePassthroughAgent")
```

## Common Patterns

### Financial Dashboards

```python
# AI creates financial views
lui("""
Build a CFO dashboard with:
- Cash flow waterfall chart
- Expense breakdown by category
- Budget vs actual comparison
- Forecast accuracy metrics
""", agent="PerspectiveAgent")

# Direct financial config
lui("""
{
  "plugin": "y_bar",
  "row_pivots": ["account_category", "account"],
  "columns": ["actual", "budget", "variance"],
  "expressions": {
    "variance": "\"actual\" - \"budget\"",
    "variance_pct": "(\"actual\" - \"budget\") / \"budget\" * 100"
  },
  "sort": [["variance", "asc"]],
  "plugin_config": {
    "series": {
      "actual": {"color": "#1f77b4"},
      "budget": {"color": "#ff7f0e"},
      "variance": {
        "color_mode": "gradient",
        "gradient": {
          "positive": "#2ca02c",
          "negative": "#d62728"
        }
      }
    }
  }
}
""", agent="PerspectivePassthroughAgent")
```

### Customer Analytics

```python
# AI builds customer views
lui("""
Create a customer segmentation view showing:
- RFM analysis grid
- Customer lifetime value distribution
- Churn risk indicators
""", agent="PerspectiveAgent")

# Direct segmentation config
lui("""
{
  "plugin": "treemap",
  "row_pivots": ["segment", "sub_segment"],
  "columns": ["customer_count", "total_revenue", "avg_ltv"],
  "aggregates": {
    "customer_count": "count",
    "total_revenue": "sum",
    "avg_ltv": "avg"
  },
  "plugin_config": {
    "size_column": "customer_count",
    "color_column": "avg_ltv",
    "color_scheme": "blues",
    "show_labels": true
  }
}
""", agent="PerspectivePassthroughAgent")
```

### Real-time Monitoring

```python
# AI creates monitoring view
lui("""
Build a real-time system monitoring dashboard with:
- Live metric updates
- Alert thresholds
- Historical comparison
""", agent="PerspectiveAgent")

# Direct monitoring config
lui("""
{
  "plugin": "y_line",
  "columns": ["timestamp", "cpu_usage", "memory_usage", "request_rate"],
  "aggregates": {
    "cpu_usage": "avg",
    "memory_usage": "avg",
    "request_rate": "sum"
  },
  "sort": [["timestamp", "desc"]],
  "limit": 1000,
  "plugin_config": {
    "realtime": true,
    "y_axis": {
      "cpu_usage": {
        "label": "CPU %",
        "threshold": 80,
        "threshold_color": "#ff0000"
      },
      "memory_usage": {
        "label": "Memory %",
        "threshold": 90,
        "threshold_color": "#ff0000"
      }
    },
    "refresh_interval": 1000
  }
}
""", agent="PerspectivePassthroughAgent")
```

## Integration with Other Agents

```python
# Query data with database agent
lui("Get sales metrics by region and product", agent="PostgresAgent")
sales_data = lui.df

# Create interactive visualization
lui("""
Create an interactive dashboard from this sales data with:
- Geographic heatmap
- Product performance table
- Time series trends
""", agent="PerspectiveAgent")

# Add advanced analytics
lui("Add predictive trends to the visualization", agent="CodeAgent")

# Document insights
lui("Generate a report explaining the key findings", agent="TextAgent")
```

## Advanced Features

### Custom Themes

```python
# AI applies branding
lui("""
Style this dashboard with our corporate colors
and branding guidelines
""", agent="PerspectiveAgent")

# Direct theme config
lui("""
{
  "plugin": "datagrid",
  "theme": {
    "colors": {
      "primary": "#003366",
      "secondary": "#0066cc",
      "success": "#28a745",
      "warning": "#ffc107",
      "danger": "#dc3545"
    },
    "font": {
      "family": "Arial, sans-serif",
      "size": "12px"
    },
    "grid": {
      "row_height": 30,
      "header_height": 40,
      "border_color": "#e0e0e0"
    }
  }
}
""", agent="PerspectivePassthroughAgent")
```

### Composite Views

```python
# AI creates dashboard layout
lui("""
Create a 4-panel dashboard with:
- KPIs at the top
- Charts on the left
- Detailed table on the right
- Filters at the bottom
""", agent="PerspectiveAgent")

# Direct composite config
lui("""
{
  "layout": {
    "type": "grid",
    "columns": 3,
    "rows": 3,
    "panels": [
      {
        "position": {"col": 0, "row": 0, "colspan": 3},
        "view": {
          "plugin": "datagrid",
          "columns": ["kpi", "value", "change"],
          "plugin_config": {"style": "kpi"}
        }
      },
      {
        "position": {"col": 0, "row": 1, "colspan": 2},
        "view": {
          "plugin": "y_bar",
          "columns": ["category", "revenue"]
        }
      },
      {
        "position": {"col": 2, "row": 1, "rowspan": 2},
        "view": {
          "plugin": "datagrid",
          "columns": ["product", "sales", "profit"]
        }
      }
    ]
  }
}
""", agent="PerspectivePassthroughAgent")
```

## Next Steps

- Learn about [Kepler Agent](kepler.md) for geospatial visualizations
- Explore [Graph Agent](graph.md) for network visualizations
- See [Mermaid Agent](mermaid.md) for diagram generation
- Check the [Query Patterns Guide](../query-patterns.md) for more examples