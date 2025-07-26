# Contributing to LouieAI Python Library

Thank you for your interest in contributing! We welcome contributions via pull requests and appreciate your help in making this project better.

## Quick Start

**New to the project?** Start with our [Developer Guide](https://louieai.readthedocs.io/en/latest/development/) for complete technical setup, tool usage, and troubleshooting.

**Experienced developer?** Fork, clone, and run:
```bash
uv pip install -e ".[dev]" && pre-commit install && pytest -q
```

## Developer Certificate of Origin

By contributing to this project, you are agreeing to the Developer Certificate of Origin (DCO). All commits must be signed off with:

```
Signed-off-by: Your Name <your.email@example.com>
```

You can do this automatically by using the `-s` flag when committing:

```bash
git commit -s -m "Your commit message"
```

The full DCO text is available at https://developercertificate.org/

This lightweight approach (no CLAs or paperwork!) ensures contributions can be legally included while keeping the process simple.

## Contribution Workflows

### Feature Development
1. **Open an issue** describing the feature (if not already exists)
2. **Create a branch**: `git checkout -b feature/description`
3. **Develop and test**: Follow our [Developer Guide](https://louieai.readthedocs.io/en/latest/development/)
4. **Submit PR**: Link to the issue, describe changes, ensure CI passes
5. **Review process**: Address feedback and iterate as needed

### Bug Fixes
1. **Reproduce the bug** locally first
2. **Create a branch**: `git checkout -b bugfix/description`
3. **Fix and add tests** to prevent regression
4. **Submit PR**: Include reproduction steps and fix description
5. **Verify fix**: Ensure the original issue is resolved

### Documentation Contributions
1. **Identify documentation gaps** or errors
2. **Create a branch**: `git checkout -b docs/description`
3. **Update documentation**: 
   - User docs in `docs/`
   - Dev docs in [Developer Guide](https://louieai.readthedocs.io/en/latest/development/)
   - API docs: Update docstrings in source code (auto-generated via mkdocstrings)
4. **Test locally**: 
   - Run `mkdocs serve` to preview changes
   - Run `mkdocs build --strict` to ensure no warnings
5. **Submit PR**: Include screenshots if visual changes

## Code Review Process

### For Contributors
- **Self-review**: Use pre-commit hooks and run full test suite
- **CI compliance**: All checks must pass (lint, format, type-check, tests)
- **Documentation**: Update relevant docs for user-facing changes
- **Tests**: Include test coverage for new functionality

### For Maintainers
- **Review criteria**: Code quality, test coverage, documentation completeness
- **Response time**: We aim to respond to PRs within 3 business days
- **Approval process**: At least one maintainer approval required
- **Merge strategy**: Squash and merge with descriptive commit messages

## Pull Request Guidelines

### PR Title Format
```
type: brief description

Examples:
feat: add async support for LouieClient
fix: handle network timeouts correctly
docs: update installation instructions
chore: upgrade development dependencies
```

### PR Description Template
```markdown
## Summary
Brief description of changes and motivation.

## Changes
- List of specific changes made
- Include any breaking changes

## Testing
- [ ] Tests added/updated
- [ ] Manual testing completed
- [ ] CI checks passing

## Documentation
- [ ] Documentation updated if needed
- [ ] Developer guide updated if needed

Closes #<issue-number>
```

## Release Contributions

### For Maintainers
Our [Developer Guide](https://louieai.readthedocs.io/en/latest/development/) includes complete release process documentation:
- Version bumping strategy
- Release notes preparation
- PyPI publishing workflow
- Post-release verification

### For Contributors
- **Feature requests**: Open issues to discuss before implementation
- **Breaking changes**: Require discussion and planning
- **Version planning**: Major features should target upcoming releases

## Community Guidelines

### Code of Conduct
This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

### Communication
- **Issues**: For bug reports, feature requests, and questions
- **Discussions**: For general questions and community interaction
- **PR comments**: For specific code review feedback

### Using AI Tools (Optional)
This project uses an AI co-pilot approach for some development tasks. We have an AI planning template under `AI_PROGRESS/PLAN_TEMPLATE.md`. If you'd like to use an AI assistant to help code, you can follow a similar approach. This is entirely optional but can help maintain consistency and traceability.

## Getting Help

- **Technical setup**: See our [Developer Guide](https://louieai.readthedocs.io/en/latest/development/)
- **Questions**: Open a GitHub issue or discussion
- **Security issues**: Follow instructions in [SECURITY.md](SECURITY.md)
- **General project info**: Check the [README](README.md)

## Recognition

All contributors are valued and will be recognized in our project. Significant contributions may be highlighted in release notes and project documentation.

---

**Ready to contribute?** Start with our [Developer Guide](https://louieai.readthedocs.io/en/latest/development/) for complete technical details, then jump in! We're excited to work with you.