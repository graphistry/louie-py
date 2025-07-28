# Documentation Restructuring Proposal

## README.md Structure (User-Focused)

### 1. Header
- Project name and tagline
- Badges (CI, PyPI version, License)
- One-paragraph description of what LouieAI does

### 2. Features (Brief list)
- Key capabilities in bullet points
- Focus on what users can achieve

### 3. Installation
- System requirements (Python 3.11+, Graphistry account)
- PyPI installation (uv/pip)
- Brief note about alpha status

### 4. Quick Start
- Simple code example showing basic usage
- Link to full documentation for more examples

### 5. Documentation
- Link to API Reference
- Link to User Guide
- Link to Examples

### 6. Support
- How to report issues
- Link to discussions

### 7. Contributing
- Brief invitation to contribute
- Link to CONTRIBUTING.md

### 8. License
- Apache 2.0 with brief explanation
- Link to LICENSE file

**Content to Remove from README:**
- Testing section (move to DEVELOP.md)
- Detailed error handling examples (move to User Guide)
- Development installation instructions
- CI scripts information

## CONTRIBUTING.md Structure (Process/Human-Focused)

### 1. Welcome Message
- Thank contributors
- Express openness to contributions

### 2. Quick Start for Contributors
- Brief overview with link to DEVELOP.md for technical setup
- Fork and clone basics

### 3. Developer Certificate of Origin
- Explain DCO requirement
- Show how to sign-off commits

### 4. Contribution Types & Workflows
- Feature development process
- Bug fix process
- Documentation contribution process
- Each with clear steps but link to DEVELOP.md for technical details

### 5. Code Review Process
- What to expect
- Response times
- Review criteria

### 6. Community Guidelines
- Code of Conduct
- Communication channels
- How to get help

### 7. Recognition
- How contributors are recognized

**Content to Move to DEVELOP.md:**
- Technical setup commands
- Testing details
- Tool usage specifics

## DEVELOP.md Structure (New - Technical/Setup-Focused)

### 1. Development Environment Setup
- Python version requirements
- Virtual environment setup with uv
- Installing development dependencies
- Pre-commit hooks setup

### 2. Project Structure
- Directory layout explanation
- Key modules overview
- Configuration files

### 3. Development Workflow
- Git workflow (gitflow)
- Branch naming conventions
- Commit message format

### 4. Testing
- Running tests locally (moved from README)
- CI scripts explanation
- Writing new tests
- Test structure (unit vs integration)
- Coverage requirements

### 5. Code Quality Tools
- Linting (ruff)
- Type checking (mypy)
- Formatting
- Documentation building

### 6. Debugging
- Common issues and solutions
- Environment variables
- Logging

### 7. Release Process
- Version management
- Creating releases
- Publishing to PyPI

### 8. AI-Assisted Development
- Optional AI co-pilot workflow
- Reference to ai/templates/PLAN.md

### 9. Technical Resources
- Architecture decisions
- API design principles
- Performance considerations