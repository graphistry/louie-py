# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `louie()` accepts `frontend_url`, forwarded to the `Cursor` that controls `lui.url`.
  It was reachable only by constructing a `Cursor` around `louieai._client.LouieClient`,
  so documenting the desktop link override meant publishing a private import. Passing it
  previously raised `TypeError` from `LouieClient`, so nothing that worked before changes.
- `upload_image(prompt, image, filename=...)` and the notebook forms
  `lui(image, prompt, filename=...)` / `lui(prompt, image, filename=...)` accept
  `filename=`, like `upload_binary` (#59). The name is sent as given, so include the
  extension. `lui()` takes the image as a path, bytes, PIL image, or a file object whose
  name has an image extension; pass a nameless file object (such as `io.BytesIO`) to
  `upload_image` directly.

### Documentation
- Agent guides used names Louie servers reject with `400 Invalid agent` (#52). **Upgrade
  note:** update your code as well: `SplunkAgent` / `SplunkPassthroughAgent` are now `Splunk` /
  `SplunkPassthrough`, `KustoAgent` / `KustoPassthroughAgent` are now `Kusto` /
  `KustoPassthrough`, and `NotebookAgent` is now `NotebookTool`. `FirecrawlAgent` and
  `UploadAgent` no longer exist: web scraping goes through `LouieAgent`'s web search tool,
  and uploads use `UploadPassthroughAgent`.
- Removed the Snowflake and Athena agent guides: no Louie deployment runs those agents.
- Notebook guide: the agent works on Louie notebooks, not Jupyter files. Creating, editing,
  and running cells requires notebook editing to be enabled on the server. Dropped the
  examples no server supports: reordering cells, clearing outputs, widgets, exporting to
  other formats, git preparation, scheduling, and CI/CD.
- Web scraping guide: web search must be enabled on the server, and Firecrawl is its
  premium provider. Dropped what the web tools can't do: clicking through pages, waiting
  for or scrolling dynamic content, screenshots, and rate-limit or user-agent control.
- Agent guides note which agents Louie Desktop does not include (the SQL agents, Spanner,
  Neptune, TableAI) and that `KeplerAgent` needs a map tile source on the server.
- New [Connecting: Web vs Desktop](docs/getting-started/connecting.md) page. Louie Desktop
  serves its API on `http://127.0.0.1:10013`, which nothing in the docs said — every
  `server_url` example targeted Louie Web, so desktop users had no address to point at.
  The page covers each deployment's URL, anonymous desktop sessions, `louie://` thread
  deep links, `LOUIE_URL`, and the failure modes of getting it wrong.
- Server tables in both authentication guides now name Louie Web vs Louie Desktop and list
  the desktop port. `server_url` is documented in the auth options reference; it was
  missing from the table despite being the setting that decides which server you reach.
- Anonymous-auth examples moved off `http://localhost:8513` to `http://127.0.0.1:10013`.
  `/auth/anonymous` is a Louie Desktop feature, so the example now uses the desktop port.
  Same change in the `LouieClient` and `louie()` docstrings, which feed the API reference.

### Fixed
- Server error details were dropped on chat and upload requests (#52). `lui(..., agent="X")`,
  `add_cell`, and the upload calls raised a bare `400 Bad Request`; the body naming the
  problem (`Invalid agent 'X'`) was already closed, so `e.response.text` raised
  `StreamClosed` too. The `httpx.HTTPStatusError` message now carries a one-line
  `Server detail: ...` (at most 500 characters), and `e.response` stays readable.
- Expired login tokens are now refreshed on `add_cell` (#52). Its refresh-and-retry check
  reads the 401 body for a JWT error, which was unreadable on this streamed call, so it
  failed instead of refreshing once and retrying.
- Upload calls (`upload_dataframe`, `upload_image`, `upload_binary`) now refresh an expired
  login token and retry once, like `add_cell` (#56). Their `@auto_retry_auth` decorator
  looked up `self.auth_manager`, which `UploadClient` lacked, so every 401 was re-raised.
  Image and binary uploads read your file object once and resend those same bytes on retry,
  so a reader without `seek()` or a stream not at position 0 is resent unchanged.
- `upload_image` sent a file object without a name (such as `io.BytesIO`) as `image.bin`,
  so the server kept it as opaque binary instead of an image (#59). The server routes
  uploads by filename extension, so the client now takes the extension from the file
  signature whenever the name it derives (from a path or file object, or `image` for raw
  bytes) has no image extension: `screenshot.bin` holding a PNG is sent as
  `screenshot.png`, and a nameless stream as `image.png`. A name passed as `filename=` is
  never changed. Bytes with no known image signature are sent as
  `application/octet-stream` under their own name, or `image.bin` when they have none.
- Orgs whose slug contains `_` got `401 Could not validate credentials` on every request
  (#53). The `X-Graphistry-Org` header rewrote `my_org` to `my-org`, naming an org that
  doesn't exist. This includes the default `louie(graphistry_client=g)` flow, which
  picks up the slug from the PyGraphistry client.
  - The header now carries the org slug exactly when the Graphistry client confirms it
    as its active org. That covers `graphistry_client=g` and credential logins with
    `org_name=`. It also covers slugs that are not lowercase, such as an
    admin-assigned `Acme_Corp`.
  - Other values are converted the way the Graphistry server generates slugs.
    Underscores are kept and accents are transliterated (`café` -> `cafe`).
    Characters such as `.`, `@`, `&` and `'` are dropped rather than turned into `-`.
    Personal-org usernames now map to the server's slug: `John.Doe` -> `johndoe`; it
    used to be `john-doe`, which doesn't exist. Display names map as before:
    `"My Org"` -> `my-org`.
  - `org_name` is documented as the org slug (the ID in `/o/<slug>/` URLs), not a
    display name.
- README's custom-server example called `LouieClient(server_url=..., server=...)`. Neither
  half worked: `LouieClient` is not exported from `louieai`, and `server=` has been
  rejected with "use graphistry_server instead" since it was renamed. Replaced with the
  public `louie()` API. The README also claimed `LOUIE_URL` defaults to
  `https://louie.ai`; the default is `https://den.louie.ai`.
- Stop shipping internal material in the sdist. `plan.md`, `weekly_report.md`, `tests/`,
  and `.env.example` were published in every release through 0.9.0 because setuptools'
  default sdist sweeps in top-level files and the test tree. Added `MANIFEST.in`; the
  sdist is 23% smaller. Wheels were never affected.
- Untrack `plan.md` and `weekly_report.md`. Both were internal working notes tracked since
  2025-08-02. `.gitignore` now covers them, anchored as `/plan.md` so the plan skill's
  `plans/<task>/plan.md` convention still works.

### Internal
- `tests/unit/agent_catalog.py` lists the agent names Louie servers run, and
  `tests/unit/test_docs_agent_names.py` fails if docs, notebook cells, README, or `src`
  docstrings pass any other name as `agent=` (#52).
- `tests/unit/test_packaging_hygiene.py` fails if internal material becomes tracked again
  or if `MANIFEST.in` loses its exclusions. Written after the fact — nothing had been
  checking, which is why this shipped for a year.
- `scripts/ci/check_sdist.py` opens the built archives and rejects internal paths or
  credential-shaped content. Rules can be right while the artifact is wrong, so this runs
  in CI's `install-test` (which already builds) and again in `publish.yml` before each
  upload — the last point at which a mistake is still recallable.
- The artifact screen also sweeps the extracted archive with `detect-secrets`, compared
  against `.secrets.baseline`, covering the classes the deterministic gate misses: AWS
  keys, private key blocks, keyword-adjacent values, high-entropy strings. Archive paths
  are normalized back to repository paths first — a wheel ships `louieai/` where the repo
  has `src/louieai/`, and `PKG-INFO`/`METADATA` are generated from `README.md`.
  `detect-secrets scan` enumerates files through git, so in an extracted archive a bare
  scan reports zero findings regardless of contents; `--all-files` is required and a test
  pins it.
- Every unavailable prerequisite now fails the screen instead of passing it. A missing
  baseline, comparer, or `detect-secrets` binary previously returned "clean" — the same
  defect as a gate whose failure branch is unreachable.
- `tests/unit/security/test_release_artifact_gates.py` proves the gates *reject*: 9 leak
  types x 2 artifact types, planted into real `.tar.gz` and `.whl` archives. Controls: a
  clean archive of each type must pass, each sweep-caught leak must survive with the sweep
  disabled (so a rotted sweep cannot hide behind the literal gate), and a missing
  `detect-secrets` fails the module rather than skipping it.

## [0.9.0] - 2026-07-26

### Added
- Default-off `include_reasoning` support across client, Cursor, Jupyter, and all upload paths.
- Final-safe `final_text*` and explicit `reasoning_text*` accessors on `Response`, Cursor, and history proxies.
- Lossless `stream_messages`, run/phase/status/token, terminal, and returned `trace_events` accessors.

### Changed
- **Breaking:** `Response.text` now honours the server's explicit `final_answer` pointer
  whether or not `include_reasoning` was set. It previously did so only when reasoning was
  requested, and otherwise returned the first text element. Affects responses where the
  server names a final answer that is not the first text element. `final_text` was already
  correct and is unchanged.
- **Breaking:** `Response.text_elements` now excludes reasoning, matching `Response.text` —
  the singular and plural of the same accessor disagreed. Use `elements` for the unfiltered
  union or `reasoning_elements` for reasoning. No effect unless `include_reasoning=True`.
- Streaming, singleshot, upload, and notebook paths now share typed/legacy/concatenated JSON accumulation with position-aware replacement.
- Notebook displays label and collapse identifiable reasoning, show execution phase/status, and escape untrusted streamed HTML.
- `traces` documentation now describes server trace events; provisional model reasoning uses `include_reasoning`.

### Fixed
- `ResponseProxy.elements` (`lui.elements`, `lui[-n].elements`, `Cursor.elements`) read a
  `message` key for error text, but the server sends `ExceptionElement.text`, so every error
  surfaced the literal `"Unknown error"` while the real message was dropped. Reads `text`
  first, with `message` retained as a legacy fallback.
- `ResponseProxy.elements` entries now carry the source element `id`, so they can be
  correlated with `Response.final_answer_id`, and are emitted in server position order
  instead of being regrouped by type (an error raised midway is no longer hoisted first).

### Compatibility
- Reasoning stays off by default. `Response.text` keeps its historical first-text behaviour
  when the server sends no explicit final-answer pointer, and Cursor keeps its latest-text
  fallback.

### Security
- Both secret-detection gate modes were structurally unable to fail: they branched on the
  exit code of `detect-secrets scan --baseline`, which is an update command that always
  exits 0. Replaced with an explicit baseline comparison, and added a deterministic gate for
  Graphistry personal keys that entropy heuristics do not reach.
- Pre-commit now scans the git index rather than the working tree, honours renames, and
  fails closed on a missing or corrupt baseline.
- Development credentials referenced by tests have been rotated; test fixtures, docs, and
  `.env.example` now use RFC 2606 example domains and public endpoints.

### Internal
- CI installs from `uv.lock` (`uv sync --locked`), so lint, format, and type results are
  reproducible. Previously it resolved unpinned floors and silently drifted.
- `.env` is opt-in for tests via `LOUIE_TEST_MODE=integration`, so a run with no credentials
  stays offline instead of dialling a real service.

### Documentation
- `docs/api/response-types.md` groups the 30 `Response` members into everyday, opt-in
  reasoning, and power/debug tiers.
- Point the advertised documentation URL at `louie-py.readthedocs.io`. `pyproject.toml`
  and `CONTRIBUTING.md` linked `louieai.readthedocs.io`, which 404s, so the PyPI
  "Documentation" link was broken on every release. The CONTRIBUTING troubleshooting
  link pointed at a page that does not exist on either host and now points at the
  authentication guide.

## [0.8.1] - 2026-04-14

### Fixed
- **Streaming timeouts**: `stream_response()` now uses client's `timeout`/`streaming_timeout` instead of hardcoded 120s read timeout that silently dropped responses
- **Empty DataFrame warnings**: Attach `pd.DataFrame()` for DfElements with `shape: [0, 0]` instead of fetching from server (workaround for #40)
- **RuntimeWarning on timeout**: Users see a visible warning in notebook output instead of silent empty `texts=[]`

### Added
- **`user_agent`** param on `Cursor` — sets `creation_user_agent` on DataThread (`"API"` or `"Louie"`)
- **`folder`** param on `Cursor` — organizes threads into folders
- **`frontend_url`** param on `Cursor` — override auto-detected thread URL
- **Desktop deep links**: `Cursor.url` auto-detects localhost and produces `louie://n/` deep links
- **`ShareMode`** and **`UserAgent`** Literal types in `_types.py`, applied throughout

## [0.8.0] - 2026-04-10

### Added
- **Streaming protocol compat**: Type-discriminated NDJSON message routing for `StreamingApiMessageRunUpdate`, `StreamingApiMessageTrace`, and other new server message types (graphistry/graphistrygpt#2628). Falls back to legacy `payload`-presence check for old servers.

### Changed
- `_parse_jsonl_response()` now routes on `data.get("type")` first, with `isinstance(elem, dict)` guard for Trace array payloads.

### Server compatibility
- **Louie >= 0.14.x (develop)**: Works via legacy fallback (no `type` field)
- **Louie with graphistry/graphistrygpt#2628**: Works via type-discriminated routing

## [0.7.1] - 2026-01-25

### Added
- Targeted pandas 2.x/3.x compatibility tests in CI.

### Changed
- pandas requirement updated to `>=2,<4` (supports 2.x and 3.x).
- Dropped direct `pytz` dependency; now only transitive via pandas 2.x.

### Fixed
- Secret detection CI no longer rewrites `.secrets.baseline` on check-only runs.

## [0.7.0] - 2026-01-16

### Added
- **Distributed tracing**: W3C `traceparent` propagation for correlating requests with OpenTelemetry
  - Automatic OTel context propagation when available
  - Session-level trace ID for correlation when OTel is not configured
  - `Cursor.new()` children inherit parent trace ID for session-wide correlation
  - Zero configuration required - works automatically

### Changed
- `LouieClient._get_headers()` now accepts `session_trace_id` and `traceparent` parameters
- All HTTP methods (`add_cell`, `upload_*`, streaming) propagate trace context

## [0.6.2] - 2025-12-22

### Added
- **Dthread naming + folders**: Thread name/folder are supported across create, add, list, and upload helpers, plus notebook cursor flows.
- **Thread lookup by name**: `get_thread_by_name()` resolves threads by name via the unified identifier endpoint.
- **Anonymous desktop auth (optional)**: Anonymous token flow for local desktop servers via `/auth/anonymous`, with `anonymous`/`token` client options.

### Changed
- **Thread listing**: `list_threads()` now parses both `data` and `items` response shapes and supports client-side folder filtering.
- 🔥 **Breaking**: `server` and `anonymous_token` were removed; use `graphistry_server` and `token` instead.
- **Secret detection**: CI now uses a temp baseline to avoid rewriting `.secrets.baseline` timestamps when nothing changes.

## [0.6.1] - 2025-11-06

### Added
- **Table AI overrides**: `LouieClient.add_cell()` and `UploadClient.upload_dataframe()` accept structured Table AI overrides and automatically route to the singleshot endpoint when any override is supplied, including callable shorthand support and dataframe hydration for override responses.
- **`TableAIOverrides` dataclass**: Public helper (exported from `louieai`) with JSON-safe normalization to simplify setting semantic/evidence/ask modes and options.

### Changed
- `LouieClient.__call__()` forwards additional keyword arguments to ensure override kwargs work with the callable interface.

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
