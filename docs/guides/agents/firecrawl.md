# Firecrawl Agent Guide

The Firecrawl agent enables web scraping and data extraction from websites, turning unstructured web content into structured data for analysis.

## Overview

- **FirecrawlAgent** - AI-powered web scraping and content extraction

## FirecrawlAgent

The FirecrawlAgent understands:
- Web page structure and content
- Data extraction patterns
- Multi-page crawling
- Content cleaning and formatting

### Basic Usage

```python
from louieai.notebook import lui

# Simple page scraping
lui("Extract the main content from https://example.com/article", agent="FirecrawlAgent")

# Product information
lui("Scrape product details from this e-commerce page", agent="FirecrawlAgent")

# News aggregation
lui("Collect headlines from this news website", agent="FirecrawlAgent")
```

### Content Extraction

```python
# Article extraction
lui("""
Extract from this blog post:
- Title
- Author
- Publication date
- Main content
- Tags/categories
""", agent="FirecrawlAgent")

# Product catalog
lui("""
Scrape product information including:
- Product name
- Price
- Description
- Images
- Reviews
- Availability
""", agent="FirecrawlAgent")

# Contact information
lui("""
Find and extract:
- Company name
- Address
- Phone numbers
- Email addresses
- Social media links
""", agent="FirecrawlAgent")
```

### Multi-page Crawling

```python
# Paginated results
lui("""
Crawl all pages of search results and extract:
- Item titles
- Prices
- Links
- Follow pagination automatically
""", agent="FirecrawlAgent")

# Site navigation
lui("""
Starting from the homepage, crawl:
- All product categories
- Extract products from each category
- Limit to 100 pages total
""", agent="FirecrawlAgent")

# Documentation sites
lui("""
Scrape entire documentation site:
- Table of contents
- All documentation pages
- Code examples
- Maintain hierarchy
""", agent="FirecrawlAgent")
```

### Structured Data Extraction

```python
# Table extraction
lui("""
Extract all tables from this page and convert to:
- Structured DataFrames
- Include headers
- Handle merged cells
- Clean formatting
""", agent="FirecrawlAgent")

# Form data
lui("""
Extract form fields and options:
- Input field names and types
- Dropdown options
- Default values
- Validation rules
""", agent="FirecrawlAgent")

# Metadata extraction
lui("""
Extract page metadata:
- Meta tags
- Open Graph data
- Schema.org markup
- JSON-LD data
""", agent="FirecrawlAgent")
```

## Common Use Cases

### Market Research

```python
# Competitor analysis
lui("""
Analyze competitor website:
- Product offerings
- Pricing information
- Feature comparisons
- Customer reviews
""", agent="FirecrawlAgent")

# Price monitoring
lui("""
Track prices across multiple sites:
- Product name
- Current price
- Historical price if available
- Stock status
""", agent="FirecrawlAgent")
```

### Content Aggregation

```python
# News monitoring
lui("""
Aggregate news from multiple sources about:
- Specific keywords
- Company mentions
- Industry updates
- Publication dates
""", agent="FirecrawlAgent")

# Job listings
lui("""
Collect job postings matching:
- Job title
- Company
- Location
- Salary range
- Requirements
""", agent="FirecrawlAgent")
```

### Data Collection

```python
# Research data
lui("""
Extract research data:
- Statistical tables
- Chart data
- Citations
- Methodology sections
""", agent="FirecrawlAgent")

# Directory scraping
lui("""
Extract business listings:
- Business name
- Category
- Contact details
- Hours of operation
- Reviews/ratings
""", agent="FirecrawlAgent")
```

## Advanced Features

### Dynamic Content

```python
# JavaScript-rendered content
lui("""
Extract content from this React/Vue/Angular app:
- Wait for dynamic loading
- Capture AJAX-loaded data
- Handle infinite scroll
""", agent="FirecrawlAgent")

# Interactive elements
lui("""
Extract data that requires interaction:
- Click tabs to reveal content
- Expand accordions
- Load more buttons
""", agent="FirecrawlAgent")
```

### Data Cleaning

```python
# Clean extracted data
lui("""
Extract and clean:
- Remove ads and popups
- Strip formatting tags
- Normalize whitespace
- Convert to plain text
""", agent="FirecrawlAgent")

# Format conversion
lui("""
Extract content and convert to:
- Markdown format
- Clean HTML
- Structured JSON
- CSV for tables
""", agent="FirecrawlAgent")
```

### Filtering and Selection

```python
# Selective extraction
lui("""
Extract only:
- Main article content
- Skip navigation and sidebars
- Ignore advertisements
- Focus on relevant sections
""", agent="FirecrawlAgent")

# Pattern matching
lui("""
Find and extract all:
- Email addresses
- Phone numbers
- Prices with currency
- Dates in any format
""", agent="FirecrawlAgent")
```

## Best Practices

### Respectful Scraping

```python
# Rate limiting
lui("""
Scrape this site respectfully:
- Maximum 1 request per second
- Respect robots.txt
- Use appropriate user agent
- Handle rate limit responses
""", agent="FirecrawlAgent")
```

### Error Handling

```python
# Robust extraction
lui("""
Extract data with fallbacks:
- Primary selectors
- Alternative selectors
- Default values for missing data
- Error reporting
""", agent="FirecrawlAgent")
```

### Data Quality

```python
# Validation
lui("""
Extract and validate:
- Check data completeness
- Verify expected formats
- Flag anomalies
- Report extraction confidence
""", agent="FirecrawlAgent")
```

## Integration with Other Agents

```python
# Scrape data
lui("Extract product catalog from competitor site", agent="FirecrawlAgent")
scraped_data = lui.df

# Analyze with SQL
lui("Store this scraped data in our database", agent="PostgresAgent")

# Create visualizations
lui("Visualize price comparisons across competitors", agent="PerspectiveAgent")

# Generate insights
lui("Analyze competitive positioning based on this data", agent="LouieAgent")
```

## Output Formats

### Structured Data

```python
# DataFrame output
lui("""
Extract as DataFrame:
- Column headers from page
- Consistent data types
- Handle missing values
- Index by unique identifier
""", agent="FirecrawlAgent")
```

### Nested Data

```python
# Hierarchical extraction
lui("""
Extract nested structure:
- Categories
  - Subcategories
    - Products
      - Attributes
Maintain relationships
""", agent="FirecrawlAgent")
```

### Raw Content

```python
# Full page capture
lui("""
Capture entire page:
- HTML source
- Rendered content
- Resources (images, CSS)
- Screenshot
""", agent="FirecrawlAgent")
```

## Legal and Ethical Considerations

**Important**: Always ensure you have permission to scrape websites and comply with:
- Website terms of service
- Robots.txt directives
- Rate limiting requirements
- Copyright laws
- Data protection regulations (GDPR, CCPA)

## Next Steps

- Learn about [TableAI Agent](tableai.md) for analyzing extracted tables
- Explore [Code Agent](code.md) for processing scraped data
- See [OpenSearch Agent](opensearch.md) for indexing web content
- Check the [Query Patterns Guide](../query-patterns.md) for more examples