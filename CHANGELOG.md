# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2025-09-25

### Added
- **Upload support**: Complete DataFrame, image, and binary file upload functionality
  - New methods: `upload_dataframe()`, `upload_image()`, `upload_binary()`
  - Natural notebook interface via `lui(df, "analyze this")` or `lui("query", df)`
  - Support for multiple formats: parquet, csv, json, jsonl, arrow
  - Automatic format detection and serialization
  - Configurable parsing options per format
- **JSONL format**: Explicit support for JSONL (newline-delimited JSON) format
- **Image analysis**: Upload and analyze images (PNG, JPEG, GIF, etc.)
- **Binary file support**: Upload PDFs, Office docs, and other binary files
- **Streaming display**: Enhanced streaming support for uploads in notebooks

### Changed
- Moved `nbclient` from main to dev/docs dependencies (not needed at runtime)
- Removed unnecessary `_upload.py` exclusion from ruff formatter

### Fixed
- Fixed JSONL parsing for concatenated JSON responses from server
- Fixed context manager syntax errors in upload implementation
- Resolved all linting and formatting issues in upload code

## [0.5.7] - 2025-08-05

### Fixed
- **Double display in Jupyter notebooks**: Fixed issue where responses were displayed twice when calling `lui("query")` in notebooks
  - Modified `_repr_html_` to show only session metadata instead of response content
  - Response content is now displayed only once via streaming or `_display()` method
  - Prevents duplicate display while maintaining useful session information

## [0.5.6] - 2025-08-04

### Fixed
- **Cursor properties**: `lui.df`, `lui.text`, and `lui.g` now correctly return the **last** (most recent) result instead of the first
  - This matches user expectations where the most recent result is typically most relevant
  - Affects both `Cursor` and `ResponseProxy` classes

### Added
- **Thread management documentation**: Added comprehensive documentation for `.url` and `.thread_id` properties
- **Thread Management section** in notebook API docs with examples for sharing analysis results

### Improved
- **Security documentation**: Enhanced credential storage guidelines for AI assistants
- **Cursor.url property**: Enhanced docstring with examples and use cases

## [0.5.5] - 2025-08-04

### Fixed
- **Vibes investigation notebook**: Fixed remaining table references to use underscored `o365_management_activity_flat_tcook` instead of hyphenated names
- **Notebook output cleaning**: Enhanced to handle `display_data` output type in addition to `execute_result`

## [0.5.4] - 2025-08-04

### Fixed
- **Vibes investigation notebook**: Fixed Databricks table references to use correct `o365_management_activity_flat_tcook` table name instead of incorrect hyphenated names

## [0.5.3] - 2025-08-04

### Added
- **Cursor.new() method** for creating fresh conversation threads while preserving authentication and configuration
- **Thread naming support** via `name` parameter in both `louie()` factory and `new()` method
- **Share mode validation** with clear error messages for invalid modes
- **DataFrame metadata preservation** in elements (id, df_id, block_id fields)
- **Notebook build utilities**:
  - `build-notebook.sh` for executing notebooks with environment authentication
  - `validate-notebook.py` for checking execution status and secrets
  - `clean-notebook-outputs.py` for redacting sensitive data from outputs
- **Demo video** added to documentation homepage
- **CI improvements**:
  - Concurrency control to cancel previous runs on new push
  - Light smoke test stage for faster feedback

### Fixed
- **DatabricksAgent empty text elements**: ResponseProxy.elements now properly checks content/text/value fields
- **Notebook output cleaning**: Fixed to redact sensitive data instead of removing entire outputs
- **Pre-commit hook**: Now recognizes `****` as legitimate redaction pattern

### Changed
- **Vibes tutorial notebook** updated to use `lui.new()` pattern instead of deprecated `new_thread()`
- **Pre-commit hook** improved to handle redaction patterns in security tools

### Documentation
- Added comprehensive examples for `Cursor.new()` method
- Updated vibes tutorial with DataFrame ID extraction pattern
- Improved notebook authentication documentation

## [0.5.2] - 2025-08-03

### Fixed
- Fixed streaming read logic to prevent text truncation in `lui.text`
  - Track last activity time instead of total elapsed time for timeouts
  - Only timeout after periods of inactivity, not during active streaming
  - Accept responses with at least one line (thread ID) instead of requiring 2
  - Merge incremental text updates instead of overwriting elements
  - Improve logging with warnings about potential truncation

### Added
- Comprehensive "Vibes Investigation Tutorial" notebook
  - Installation, setup, and basic usage examples
  - Agent usage examples (DatabricksPassthroughAgent, DatabricksAgent, LouieAgent)
  - DataFrame access patterns and investigation workflows
  - Prompt template examples for reusable investigations

### Changed
- Configure ruff to ignore F821 (undefined names) in tutorial notebooks for intentional placeholders

## [0.5.1] - 2025-08-03

### Fixed
- Fixed Databricks DataFrame population bug where `lui.df` returned None after DatabricksPassthroughAgent queries
- Enhanced DataFrame ID extraction to support nested `data.df_id` structures from various agents
- Added support for more DataFrame element type variations (DataFrame, dataframe)
- Improved error logging with thread ID, URL, and full element context for better debugging

## [0.5.0] - 2025-08-03

### Added
- Python 3.13 support with CI matrix testing
- CI scripts for formatting, linting, type checking, and testing
- Comprehensive test coverage improvements (from ~30% to 86%)
- Additional unit tests for edge cases and error handling
- Session-scoped fixture to prevent global cursor initialization in tests

### Changed
- Improved test isolation to prevent network connections during CI runs
- Enhanced mock patterns for httpx.Client to handle both direct instantiation and context manager usage
- Simplified CallableModule test for Python 3.13 compatibility

### Fixed
- Fixed httpx.Client mocking pattern across multiple test files
- Fixed integration tests that were attempting real network connections
- Fixed performance test thresholds for CI environment
- Fixed test_client_callable.py mock reference errors
- Fixed dataframe fetching test to properly test "no df_id" case
- Fixed documentation example test that required authentication

## [0.4.0] - 2025-08-02

### Added
- AI collaboration framework with comprehensive guidelines
- Task planning template for structured AI-assisted development
- Publishing guide for PyPI releases
- ReadTheDocs configuration validation scripts
- GitHub Actions workflow for automated PyPI publishing
- Testing section in README with quick start instructions
- Configurable timeout settings for long-running agentic workflows:
  - `timeout` parameter in LouieClient (default: 300s)
  - `streaming_timeout` parameter for per-chunk timeouts (default: 120s)
  - Environment variables: `LOUIE_TIMEOUT` and `LOUIE_STREAMING_TIMEOUT`
- Clear timeout error messages with guidance for increasing limits
- Warning messages for requests taking longer than 30 seconds
- Real-time streaming display for Jupyter notebooks:
  - Progressive response updates as content is generated
  - Automatic display refresh without flicker
  - Faster time-to-first-content for better user experience
  - Works seamlessly with text, dataframes, and error responses
- Arrow dataframe fetching support:
  - Automatic fetching via `/api/dthread/{thread_id}/df/block/{block_id}/arrow` endpoint
  - Support for both `df_id` and `block_id` fields
  - Graceful error handling when dataframe fetch fails
- Comprehensive agent guides for 40+ specialized agents with hierarchical navigation
- Response Types documentation rewritten for 95% accuracy matching implementation

### Changed
- Updated documentation dependencies to latest versions
- Enhanced CI pipeline with ReadTheDocs validation
- Improved development documentation with RTD validation info
- LouieClient now uses streaming API for chat endpoint
- Improved error handling for server-sent events (SSE) streaming
- Reorganized documentation navigation with hierarchical agent guide structure
- Server URL standardized to production endpoint (https://den.louie.ai)

### Fixed
- Fixed ReadTheDocs configuration with proper build.jobs structure
- Fixed timeout issues with streaming responses from Louie API
- Fixed integration tests to handle both PyGraphistry and direct Louie authentication
- Fixed Response Types documentation accuracy (was 30% accurate, now 95% accurate)
- Fixed import syntax errors in authentication guide
- Fixed CallableModule initialization to handle None module
- Fixed error handling notebook to use real error patterns instead of fictional exceptions

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