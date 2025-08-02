# Kepler Agent Guide

The Kepler agent creates powerful geospatial visualizations using Kepler.gl, enabling interactive exploration of location-based data with advanced mapping features.

## Overview

- **KeplerAgent** - AI-powered geospatial visualization from natural language descriptions

## KeplerAgent

The KeplerAgent understands:
- Geospatial data formats and projections
- Map layer types (points, arcs, hexbins, heatmaps)
- Time-based animations
- Geographic clustering and analysis

### Basic Usage

```python
from louieai.notebook import lui

# Simple point map
lui("Show customer locations on a map", agent="KeplerAgent")

# Delivery routes
lui("Visualize delivery routes between warehouses and customers", agent="KeplerAgent")

# Density heatmap
lui("Create a heatmap of crime incidents by neighborhood", agent="KeplerAgent")
```

### Location Analytics

```python
# Store performance analysis
lui("""
Map our retail stores with:
- Size based on revenue
- Color based on year-over-year growth
- Show 5-mile radius coverage areas
""", agent="KeplerAgent")

# Supply chain visualization
lui("""
Visualize our supply chain network showing:
- Suppliers as blue points
- Warehouses as green squares
- Distribution routes as animated arcs
- Volume as line thickness
""", agent="KeplerAgent")

# Real estate analysis
lui("""
Create a map of property listings with:
- Price as color gradient
- Size based on square footage
- Filters for property type
- Neighborhood boundaries
""", agent="KeplerAgent")
```

### Movement and Flow

```python
# Transportation patterns
lui("""
Show taxi trip patterns for NYC including:
- Pickup and dropoff locations
- Animated trips over time
- Peak hours highlighted
- Trip duration as arc height
""", agent="KeplerAgent")

# Migration flows
lui("""
Visualize population migration between cities:
- Origin-destination arcs
- Migration volume as thickness
- Color by demographic segment
- Time animation by year
""", agent="KeplerAgent")

# Delivery optimization
lui("""
Map delivery routes with:
- Actual vs optimal paths
- Delivery time windows
- Vehicle capacity utilization
- Traffic impact visualization
""", agent="KeplerAgent")
```

### Spatial Analysis

```python
# Clustering analysis
lui("""
Show customer clusters using:
- Hexagonal binning for density
- Average spend per hex
- Click to see customer details
- Time-based filters
""", agent="KeplerAgent")

# Coverage analysis
lui("""
Analyze service coverage showing:
- Current coverage areas
- Gaps in coverage
- Population density overlay
- Competitor locations
""", agent="KeplerAgent")

# Risk mapping
lui("""
Create a risk assessment map with:
- Flood zones
- Historical incident data
- Asset locations
- Evacuation routes
""", agent="KeplerAgent")
```

### Time-based Visualizations

```python
# Event progression
lui("""
Animate the spread of events over time:
- Daily new cases as points
- Cumulative spread as heatmap
- Time slider for playback
- Speed controls
""", agent="KeplerAgent")

# Traffic patterns
lui("""
Show traffic patterns throughout the day:
- Hourly congestion levels
- Incident locations
- Flow direction arrows
- Peak hour highlighting
""", agent="KeplerAgent")

# Seasonal analysis
lui("""
Visualize seasonal business patterns:
- Monthly sales by location
- Seasonal trends
- Weather overlay
- Year-over-year comparison
""", agent="KeplerAgent")
```

## Advanced Features

### Multi-layer Maps

```python
# Complex urban analysis
lui("""
Create a multi-layer city analysis with:
Layer 1: Population density (heatmap)
Layer 2: Public transport routes (lines)
Layer 3: Points of interest (icons)
Layer 4: Traffic flow (animated arcs)
""", agent="KeplerAgent")

# Environmental monitoring
lui("""
Build an environmental dashboard showing:
- Air quality sensors (colored points)
- Wind patterns (arrows)
- Industrial zones (polygons)
- Affected areas (gradient overlay)
""", agent="KeplerAgent")
```

### 3D Visualizations

```python
# Building analysis
lui("""
Create a 3D city visualization with:
- Building heights from data
- Color by property value
- Sunlight simulation
- Zoning overlays
""", agent="KeplerAgent")

# Terrain visualization
lui("""
Show elevation data with:
- 3D terrain rendering
- Hiking trails overlay
- Risk zones highlighted
- Viewshed analysis
""", agent="KeplerAgent")
```

### Custom Styling

```python
# Branded maps
lui("""
Style the map with our brand colors:
- Custom base map
- Company color scheme
- Logo placement
- Branded tooltips
""", agent="KeplerAgent")

# Thematic maps
lui("""
Create a dark-themed dashboard map:
- Dark base map
- Neon accent colors
- High contrast data
- Minimal UI
""", agent="KeplerAgent")
```

## Common Patterns

### Business Intelligence

```python
# Sales territory mapping
lui("""
Map sales territories showing:
- Territory boundaries
- Rep assignments
- Customer locations
- Revenue by territory
- Opportunity pipeline
""", agent="KeplerAgent")

# Market analysis
lui("""
Analyze market penetration with:
- Customer density
- Competitor locations  
- Market share by region
- Growth opportunities
""", agent="KeplerAgent")
```

### Logistics and Operations

```python
# Fleet tracking
lui("""
Real-time fleet visualization:
- Vehicle locations
- Route progress
- Delivery status
- ETA calculations
- Traffic conditions
""", agent="KeplerAgent")

# Warehouse optimization
lui("""
Optimize warehouse locations showing:
- Current warehouses
- Demand heatmap
- Delivery distances
- Cost analysis
- Proposed locations
""", agent="KeplerAgent")
```

### Public Safety

```python
# Emergency response
lui("""
Emergency response map with:
- Incident locations
- Response unit positions
- Response time zones
- Hospital locations
- Evacuation routes
""", agent="KeplerAgent")

# Crime analysis
lui("""
Crime pattern analysis showing:
- Incident types by icon
- Time of day patterns
- Hot spot analysis
- Patrol routes
- Demographic overlays
""", agent="KeplerAgent")
```

## Integration with Other Agents

```python
# Get location data
lui("Extract customer addresses with coordinates", agent="PostgresAgent")
location_data = lui.df

# Create map visualization
lui("""
Map these customer locations with:
- Clustering by region
- Size by purchase volume
- Color by customer segment
""", agent="KeplerAgent")

# Analyze patterns
lui("What geographic patterns do you see?", agent="LouieAgent")

# Generate insights report
lui("Create a location intelligence report", agent="TextAgent")
```

## Best Practices

### Data Preparation

```python
# AI prepares geographic data
lui("""
Prepare this address data for mapping:
- Geocode addresses
- Validate coordinates
- Handle missing locations
- Add region groupings
""", agent="KeplerAgent")
```

### Performance Optimization

```python
# Handle large datasets
lui("""
Optimize this map with 1M+ points:
- Use clustering for zoom levels
- Implement data sampling
- Progressive loading
- GPU acceleration
""", agent="KeplerAgent")
```

### Interactive Features

```python
# Rich interactions
lui("""
Add interactivity:
- Click for details
- Hover tooltips
- Filter controls
- Layer toggles
- Export functionality
""", agent="KeplerAgent")
```

## Map Types Reference

### Point Maps
- Simple markers
- Sized points
- Icon markers
- Clustered points

### Line/Arc Maps
- Simple paths
- Weighted lines
- Animated flows
- Great circle arcs

### Area Maps
- Choropleth (filled regions)
- Hexagonal bins
- Grid aggregation
- Custom polygons

### Density Maps
- Heatmaps
- Contour maps
- Kernel density
- Grid heatmaps

### 3D Maps
- Extruded polygons
- 3D arcs
- Terrain models
- Building models

## Export and Sharing

```python
# Export configurations
lui("""
Export this map for:
- Static image (PNG)
- Interactive HTML
- Configuration JSON
- Video animation
""", agent="KeplerAgent")

# Embed in reports
lui("""
Prepare this map for embedding in:
- Dashboards
- Presentations  
- Web applications
- PDF reports
""", agent="KeplerAgent")
```

## Next Steps

- Learn about [Graph Agent](graph.md) for network visualizations
- Explore [Perspective Agent](perspective.md) for data tables
- See [Mermaid Agent](mermaid.md) for diagram generation
- Check the [Query Patterns Guide](../query-patterns.md) for more examples