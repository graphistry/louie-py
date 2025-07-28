# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- AI collaboration framework with comprehensive guidelines
- Task planning template for structured AI-assisted development
- Publishing guide for PyPI releases
- ReadTheDocs configuration validation scripts
- GitHub Actions workflow for automated PyPI publishing
- Testing section in README with quick start instructions

### Changed
- Updated documentation dependencies to latest versions
- Enhanced CI pipeline with ReadTheDocs validation
- Improved development documentation with RTD validation info

### Fixed
- Fixed ReadTheDocs configuration with proper build.jobs structure

## [0.1.0] - 2025-07-26

### Added
- Initial release of LouieAI Python client library
- `LouieClient` class for interacting with Louie.ai API
- Robust error handling with detailed HTTP and network error messages
- JSON error message extraction from API responses
- Bearer token authentication via PyGraphistry integration
- Comprehensive test suite with 4 tests covering success and error scenarios
- Type hints throughout codebase with `py.typed` marker
- User documentation with usage examples and architecture guide
- Developer documentation with setup, tool usage, and troubleshooting
- Contributing guidelines with workflow examples and PR templates
- Modern development tooling:
  - Ruff for linting and formatting (replaces Black + separate linter)
  - MyPy for strict type checking
  - Pre-commit hooks for automated code quality
  - pytest with parallel testing support (pytest-xdist)
- Dynamic versioning with setuptools_scm (git tag-based)
- GitHub Actions CI/CD with Python 3.11, 3.12, 3.13 testing
- MkDocs documentation site with Material theme
- Professional project structure with all standard OSS files

### Changed
- Minimum Python version requirement from 3.8 to 3.11
- Dependencies modernized to 2025 versions:
  - graphistry 0.34 → 0.40.0
  - pandas 1.0 → 2.0.0  
  - pyarrow 8.0 → 21.0.0
  - httpx 0.28 → 0.28.0
- Development dependencies updated to latest stable versions
- Code style modernized to use Python 3.11+ features (union types, modern dict/list)

### Fixed
- Resolved pytest collection errors in development environment
- Fixed mypy configuration for external dependencies
- Corrected type annotations for better IDE support
- Streamlined import organization and code formatting

### Security
- Added security policy with responsible disclosure guidelines
- Configured strict type checking to prevent common runtime errors
- Implemented comprehensive error handling to avoid information leaks