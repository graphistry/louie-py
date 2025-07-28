# Louie.ai Documentation Catalog

## Official Sources

### Primary Documentation
- **GitHub Repository**: https://github.com/graphistry/louie.ai-docs
  - Topics: Admin and user guides
  - Relevance: Server documentation, some API info

- **Louie.ai Homepage**: https://louie.ai/
  - Topics: Platform overview, features, access
  - Relevance: Marketing/overview, not API-specific

- **PyGraphistry Documentation**: https://pygraphistry.readthedocs.io/en/0.34.11/ecosystem.html
  - Topics: Integration with Graphistry, Louie.AI as genAI-native experience
  - Relevance: Client-relevant for authentication and integration

### Platform Features (from web search)

#### Core Capabilities
- **AI Notebooks**: Use natural language, queries, and code for investigation, creation, and automation
- **AI Dashboards**: Create reusable data tools, including generative AI steps like summaries
- **API**: Work with Louie and its systems headlessly for automation and custom apps

#### Database Connectivity
- Databricks
- Kusto (including graph)
- Splunk
- SQL databases (Postgres, ClickHouse, etc.)
- OpenSearch
- Growing list of native database connectors

#### Visualization & Analysis Tools
- PyGraphistry graphs
- UMAP clustering visualization
- Kepler GL maps
- Matplotlib/Seaborn charts
- Perspective charts (heatmaps, etc.)
- TableAI (semantic dataframe actions)
- Web search integration

#### Deployment Options
- Managed cloud service
- Self-hosted on public clouds
- On-premises deployment
- Air-gapped environments

## Community & Blog Resources

### LinkedIn Posts
- Leo Meyerovich (founder) posts about platform development
- Topics: Privacy, writing, coding, talking to databases
- Relevance: Product updates, vision

### Other Mentions
- US Cyber Command AI alert volume reduction competition winner
- Hacker News discussions
- Graph The Planet 2024 GenAI Edition conference

## API-Specific Information Found

### Confirmed API Features
1. **Headless operation** for automation and custom apps
2. **Integration** with PyGraphistry for authentication
3. **genAI-native notebooks** API for talking to data & databases
4. **genAI-native dashboards** API for building and sharing

### Missing Documentation (Not Found)
- Specific API reference documentation
- Python client SDK details
- dthread conversation API specifics
- Cell creation API methods
- Authentication flow details
- Request/response formats
- Rate limits and quotas

## V1 vs V2 Feature Categorization

### V1 (Minimal Client) - Focus Areas
1. PyGraphistry authentication integration
2. Create dthread (conversation thread)
3. Add cell to dthread
4. Talk to databases and get answers/dataframes back
5. Basic error handling and response parsing

### V2 (Future Features)
1. Advanced visualization creation (UMAP, Kepler, Perspective)
2. TableAI integration
3. Web search capabilities
4. Dashboard creation and management
5. Cross-filtering (when API-accessible)
6. Advanced database connector management
7. Custom tool/plugin integration

## Documentation Gaps for Client Library

### Critical Missing Pieces
1. **API Endpoint Documentation**: No public API reference found
2. **Authentication Details**: How to authenticate beyond PyGraphistry
3. **Request Formats**: Structure for creating dthreads and cells
4. **Response Formats**: What data structures are returned
5. **Error Codes**: API-specific error handling
6. **Code Examples**: Working examples of API usage
7. **Rate Limiting**: API usage limits and best practices

### Next Steps
- Contact Graphistry/Louie.ai team for API documentation access
- Explore the GitHub documentation repository more thoroughly
- Consider reverse-engineering from any available client code
- Focus initial documentation on PyGraphistry integration patterns