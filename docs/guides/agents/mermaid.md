# Mermaid Agent Guide

The Mermaid agents create diagrams and flowcharts using Mermaid syntax, enabling visualization of processes, architectures, and relationships.

## Overview

- **MermaidAgent** - AI-powered diagram generation from natural language
- **MermaidPassthroughAgent** - Direct Mermaid syntax without AI interpretation

## MermaidAgent (AI-Assisted)

The MermaidAgent understands:
- Process flows and workflows
- System architectures
- Sequence diagrams
- Entity relationships
- Gantt charts and timelines

### Basic Usage

```python
from louieai.notebook import lui

# Simple flowchart
lui("Create a flowchart of our order processing workflow", agent="MermaidAgent")

# System architecture
lui("Draw our microservices architecture diagram", agent="MermaidAgent")

# Sequence diagram
lui("Show the authentication flow between client and server", agent="MermaidAgent")
```

### Process Diagrams

```python
# Business process
lui("""
Create a flowchart showing our customer onboarding process:
- Initial signup
- Email verification
- KYC checks
- Account activation
- Welcome email
""", agent="MermaidAgent")

# Decision flows
lui("""
Draw a decision tree for loan approval process with:
- Credit score check
- Income verification
- Risk assessment
- Approval/rejection paths
""", agent="MermaidAgent")

# State machines
lui("""
Visualize order states and transitions:
- Pending → Processing → Shipped → Delivered
- Include cancellation and return flows
""", agent="MermaidAgent")
```

### Architecture Diagrams

```python
# System architecture
lui("""
Draw our cloud architecture showing:
- Load balancers
- Web servers
- Application servers
- Databases
- Cache layers
- Message queues
""", agent="MermaidAgent")

# Data flow architecture
lui("""
Visualize our data pipeline:
- Data sources (APIs, databases, files)
- ETL processes
- Data warehouse
- Analytics tools
- Reporting dashboards
""", agent="MermaidAgent")

# Network topology
lui("""
Create a network diagram with:
- Multiple VPCs
- Subnets and availability zones
- Security groups
- VPN connections
- Internet gateways
""", agent="MermaidAgent")
```

### Sequence Diagrams

```python
# API interactions
lui("""
Show the API request flow:
- Client sends request
- API gateway validates
- Microservice processes
- Database query
- Response returned
""", agent="MermaidAgent")

# Authentication flow
lui("""
Diagram OAuth2 authentication:
- User login request
- Redirect to auth provider
- User consent
- Authorization code
- Token exchange
- Access granted
""", agent="MermaidAgent")

# Distributed transactions
lui("""
Illustrate distributed transaction flow:
- Order service initiates
- Payment service processes
- Inventory service updates
- Notification service alerts
- Rollback on failure
""", agent="MermaidAgent")
```

### Entity Relationships

```python
# Database schema
lui("""
Create an ER diagram for our e-commerce database:
- Users (id, email, name)
- Orders (id, user_id, total, status)
- Products (id, name, price, category)
- OrderItems (order_id, product_id, quantity)
Show relationships and cardinality
""", agent="MermaidAgent")

# Class diagrams
lui("""
Draw class diagram for our payment system:
- Payment abstract class
- CreditCardPayment
- PayPalPayment
- BankTransfer
Include methods and inheritance
""", agent="MermaidAgent")

# Component relationships
lui("""
Show component dependencies:
- Frontend modules
- API services
- Shared libraries
- External dependencies
""", agent="MermaidAgent")
```

## MermaidPassthroughAgent (Direct Syntax)

For direct Mermaid syntax control:

### Flowcharts

```python
# Direct flowchart syntax
lui("""
flowchart TD
    A[Start] --> B{Is it Friday?}
    B -->|Yes| C[Party!]
    B -->|No| D[Work]
    D --> E[Check Calendar]
    E --> B
    C --> F[Weekend]
    
    style A fill:#f9f,stroke:#333,stroke-width:4px
    style C fill:#9f9,stroke:#333,stroke-width:2px
""", agent="MermaidPassthroughAgent")
```

### Sequence Diagrams

```python
# Direct sequence diagram
lui("""
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant D as Database
    participant C as Cache
    
    U->>F: Click "Login"
    F->>A: POST /auth/login
    A->>C: Check session
    alt Session exists
        C-->>A: Return user data
    else No session
        A->>D: Validate credentials
        D-->>A: User record
        A->>C: Store session
    end
    A-->>F: Auth token
    F-->>U: Redirect to dashboard
    
    Note over C: Sessions expire after 1 hour
""", agent="MermaidPassthroughAgent")
```

### State Diagrams

```python
# Direct state diagram
lui("""
stateDiagram-v2
    [*] --> Draft
    Draft --> Submitted: Submit for review
    Submitted --> UnderReview: Assign reviewer
    UnderReview --> Approved: Approve
    UnderReview --> Rejected: Reject
    UnderReview --> Draft: Request changes
    Rejected --> Draft: Revise
    Approved --> Published: Publish
    Published --> Archived: Archive
    Archived --> [*]
    
    Draft: Draft\n- Edit content\n- Save changes
    UnderReview: Under Review\n- Reviewer assigned\n- Comments added
    Published: Published\n- Visible to public\n- Version locked
""", agent="MermaidPassthroughAgent")
```

### Gantt Charts

```python
# Direct Gantt chart
lui("""
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    axisFormat %b %d
    
    section Planning
    Requirements gathering    :done,    des1, 2024-01-01, 2024-01-14
    Technical design         :done,    des2, after des1, 2w
    Architecture review      :done,    des3, 2024-01-28, 3d
    
    section Development
    Backend development      :active,  dev1, 2024-02-01, 45d
    Frontend development     :active,  dev2, after des3, 50d
    API integration         :         dev3, after dev1, 2w
    
    section Testing
    Unit testing            :         test1, after dev1, 1w
    Integration testing     :         test2, after dev3, 2w
    UAT                    :         test3, after test2, 1w
    
    section Deployment
    Production setup        :         dep1, after test2, 3d
    Go live                :milestone, after test3
""", agent="MermaidPassthroughAgent")
```

## Best Practices

### When to Use Each Agent

**Use MermaidAgent when:**
- You want to describe diagrams in plain language
- You need help choosing diagram types
- You want automatic layout optimization
- You're documenting processes quickly

**Use MermaidPassthroughAgent when:**
- You have specific Mermaid syntax
- You need precise control over styling
- You want custom themes
- You're creating reusable templates

### Styling and Themes

```python
# AI applies styling
lui("""
Create a flowchart with our brand colors:
- Use blue for start/end nodes
- Green for success paths
- Red for error paths
- Include our logo
""", agent="MermaidAgent")

# Direct theme control
lui("""
%%{init: {
    'theme': 'dark',
    'themeVariables': {
        'primaryColor': '#1f2937',
        'primaryTextColor': '#fff',
        'primaryBorderColor': '#7C0000',
        'lineColor': '#F8B229',
        'secondaryColor': '#006100',
        'tertiaryColor': '#fff'
    }
}}%%
flowchart LR
    A[Input] --> B{Process}
    B -->|Success| C[Output]
    B -->|Error| D[Error Handler]
    D --> E[Log Error]
    E --> B
""", agent="MermaidPassthroughAgent")
```

## Common Patterns

### Software Development

```python
# CI/CD pipeline
lui("""
Create a CI/CD pipeline diagram showing:
- Code commit
- Build process
- Test stages
- Deployment environments
- Rollback procedures
""", agent="MermaidAgent")

# Git workflow
lui("""
Visualize our Git branching strategy:
- Main branch
- Development branch
- Feature branches
- Hotfix process
- Release branches
""", agent="MermaidAgent")
```

### Business Processes

```python
# Sales funnel
lui("""
Draw a sales funnel showing:
- Lead generation
- Qualification
- Proposal
- Negotiation
- Closing
- Show conversion rates
""", agent="MermaidAgent")

# Customer journey
lui("""
Map the customer journey:
- Awareness
- Consideration
- Purchase
- Onboarding
- Retention
- Advocacy
""", agent="MermaidAgent")
```

### Technical Documentation

```python
# API architecture
lui("""
Document our API structure:
- Gateway layer
- Authentication service
- Business logic services
- Data access layer
- External integrations
""", agent="MermaidAgent")

# Database transactions
lui("""
Show transaction flow for order processing:
- Begin transaction
- Update inventory
- Process payment
- Create shipment
- Commit or rollback
""", agent="MermaidAgent")
```

## Integration with Other Agents

```python
# Analyze system with code
lui("Analyze our codebase structure", agent="CodeAgent")

# Generate architecture diagram
lui("""
Based on the code analysis, create an architecture
diagram showing main components and dependencies
""", agent="MermaidAgent")

# Document the architecture
lui("Generate documentation for this architecture", agent="TextAgent")

# Create interactive visualization
lui("Convert this to an interactive network graph", agent="GraphAgent")
```

## Advanced Features

### Subgraphs and Grouping

```python
# Complex system with subgraphs
lui("""
Create a microservices diagram with:
- Frontend cluster
- API gateway cluster
- Service mesh
- Database cluster
Group related services together
""", agent="MermaidAgent")

# Direct subgraph syntax
lui("""
flowchart TB
    subgraph Frontend
        A[React App]
        B[Mobile App]
    end
    
    subgraph API Layer
        C[Gateway]
        D[Auth Service]
        E[User Service]
    end
    
    subgraph Data Layer
        F[(User DB)]
        G[(Order DB)]
        H[(Cache)]
    end
    
    A & B --> C
    C --> D & E
    D & E --> F
    E --> G & H
""", agent="MermaidPassthroughAgent")
```

### Interactive Elements

```python
# Clickable diagrams
lui("""
Create a system diagram with clickable components
that link to their documentation
""", agent="MermaidAgent")

# Direct interactive syntax
lui("""
flowchart LR
    A[Home Page] -->|Click| B[Login Page]
    B --> C{Authenticated?}
    C -->|Yes| D[Dashboard]
    C -->|No| E[Error Page]
    
    click A "https://docs.example.com/home" "Home Documentation"
    click B "https://docs.example.com/login" "Login Documentation"
    click D "https://docs.example.com/dashboard" "Dashboard Documentation"
""", agent="MermaidPassthroughAgent")
```

## Export Options

```python
# Export formats
lui("""
Export this diagram as:
- SVG for web
- PNG for documents
- PDF for printing
- Mermaid source for editing
""", agent="MermaidAgent")

# Embed in documentation
lui("""
Prepare this diagram for:
- Markdown documents
- HTML pages
- Confluence wiki
- GitHub README
""", agent="MermaidAgent")
```

## Next Steps

- Learn about [Graph Agent](graph.md) for network visualizations
- Explore [Perspective Agent](perspective.md) for data tables
- See [Code Agent](code.md) for generating diagram code
- Check the [Query Patterns Guide](../query-patterns.md) for more examples