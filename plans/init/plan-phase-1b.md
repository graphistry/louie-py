LouieAI_Bootstrap Plan - Phase 1B (Tests, Docs & CI)
THIS PLAN FILE: AI_PROGRESS/LouieAI_Bootstrap/plan-phase-1b.md
Created: 2025-07-25 21:01:56 PST
Current Phase: 1B - Tests, Documentation & CI Setup
Previous Plan: [Phase 1A - Repository Setup](plan-phase-1a.md)
Next Phase: [Phase 2 - Core Functionality](plan-phase-2.md)
Overview: [Plan Overview](plan-overview.md)

CRITICAL META-GOALS OF THIS PLAN
THIS PLAN MUST BE:
FULLY SELF-DESCRIBING: All context needed to resume work is IN THIS FILE.
CONSTANTLY UPDATED: Every action's results recorded IMMEDIATELY in the step.
THE SINGLE SOURCE OF TRUTH: If it's not in the plan, it didn't happen.
SAFE TO RESUME: Any AI can pick up work by reading ONLY this file.
REMEMBER: External memory is unreliable. This plan is your ONLY memory.
CRITICAL: NEVER LEAVE THIS PLAN
YOU WILL FAIL IF YOU DON'T FOLLOW THIS PLAN EXACTLY
TO DO DIFFERENT THINGS, YOU MUST FIRST UPDATE THIS PLAN FILE TO ADD STEPS THAT EXPLICITLY DEFINE THOSE CHANGES.
Anti-Drift Protocol - READ THIS EVERY TIME
THIS PLAN IS YOUR ONLY MEMORY. TREAT IT AS SACRED.
The Three Commandments:
RELOAD BEFORE EVERY ACTION: Your memory has been wiped. This plan is all you have.
UPDATE AFTER EVERY ACTION: If you don't write it down, it never happened.
TRUST ONLY THE PLAN: Not your memory, not your assumptions, ONLY what's written here.
Critical Rules:
ONE TASK AT A TIME – Never jump ahead.
NO ASSUMPTIONS – The plan is the only truth. If you need new info, update the plan with new steps to investigate, document, replan, act, and validate.
NO OFFROADING – If it's not in the plan, don't do it.
Step Execution Protocol – MANDATORY FOR EVERY ACTION
BEFORE EVERY SINGLE ACTION, NO EXCEPTIONS:
RELOAD PLAN: cat AI_PROGRESS/LouieAI_Bootstrap/plan-phase-1b.md | head -200
FIND YOUR TASK: Locate the current 🔄 IN_PROGRESS step.
EXECUTE: ONLY do what that step says.
UPDATE IMMEDIATELY: Edit this plan with results BEFORE doing anything else.
VERIFY: tail -50 AI_PROGRESS/LouieAI_Bootstrap/plan-phase-1b.md
THE ONLY SECTION YOU UPDATE IS "Steps" – EVERYTHING ELSE IS READ-ONLY NEVER:
Make decisions without reading the plan first.
Create branches without the plan telling you to.
Create PRs without the plan telling you to.
Switch contexts without updating the plan.
Do ANYTHING without the plan.
If Confused:
STOP.
Reload this plan.
Find the last ✅ completed step.
Continue from there.

Context (READ-ONLY)
Phase 1B Overview
Phase 1B completes the Phase 1 setup by adding:
- Tests for the LouieClient
- Documentation scaffolding (MkDocs and ReadTheDocs)
- All required files (README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY)
- AI planning template
- GitHub Actions workflows for CI and release
- Final verification and PR creation

Prerequisites from Phase 1A:
- Core directory structure exists
- pyproject.toml is configured
- LouieClient class is implemented
- Package is installable with dev dependencies

Success Criteria for Phase 1B: 
By the end of Phase 1B, the repository should be:
- Fully tested with passing test suite
- Documented with MkDocs configuration ready for ReadTheDocs
- Complete with all community files (README with badges, CONTRIBUTING, etc.)
- CI/CD ready with GitHub Actions workflows
- Pushed to GitHub with all CI checks passing
- Ready for merge to main branch

Quick Reference (READ-ONLY)
# Reload plan
cat AI_PROGRESS/LouieAI_Bootstrap/plan-phase-1b.md | head -200

# Local validation before pushing
ruff . && mypy .
pytest -xsv

# CI monitoring (via GitHub CLI):
gh pr checks <PR-number> --repo <owner>/louieai --watch
gh run watch <run-id>
watch -n 30 'gh pr checks <PR-number> --repo <owner>/louieai'

# Debugging CI early exit example:
echo "DEBUG: Early exit" && exit 0

LIVE PLAN (THE ONLY SECTION YOU UPDATE)
Context Preservation (Update ONLY if directed by a step)
<!-- Only update these sections if a step specifically says to -->
Key Decisions Made
<!-- Document WHY things were done certain ways -->
[Docs Framework Decision]: Went with MkDocs for documentation due to its simplicity and compatibility with readthedocs (and personal preference for Markdown). This keeps documentation lightweight and easy for contributors to edit.

Lessons Learned
<!-- Document what failed and why to avoid repeating -->
[Placeholder]: This section will capture any mistakes or necessary adjustments encountered during execution.

Important Commands
<!-- Document complex commands that worked -->
# Example: Used curl to fetch standard license text directly from Apache:
curl -sSL "https://www.apache.org/licenses/LICENSE-2.0.txt" -o LICENSE

Steps
Step 1.4.0: Add a basic test for LouieClient
Status: ⏳ PENDING
Started: [timestamp]
Action: We write a minimal test to ensure the package and LouieClient work as expected in stub form. Claude should:
Create a test module: Open a new file tests/test_louie_client.py.
Write test content: Add a basic test function. We won't call the real API (to avoid external dependency), but we can test some logic:
For example, test that if graphistry.api_token() returns None, our client raises the intended error. We can simulate that by monkeypatching graphistry.api_token.
Also test that our class stores the server_url correctly.
import builtins
import pytest
import louieai
import graphistry

class DummyResponse:
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self._data = data or {}
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code} Error")
    def json(self):
        return self._data

def test_client_uses_graphistry_token(monkeypatch):
    # Monkeypatch graphistry.api_token to return a dummy token
    monkeypatch.setattr(graphistry, "api_token", lambda: "fake-token")
    # Monkeypatch httpx.post to simulate a successful response
    import httpx
    monkeypatch.setattr(httpx, "post", lambda url, json, headers, timeout: DummyResponse(data={"result": "ok"}))
    client = louieai.LouieClient()
    result = client.ask("hello")
    assert result == {"result": "ok"}
    # The fake token should have been used in headers; we can't directly check the headers here,
    # but we know our DummyResponse returned data without raising, meaning our code likely worked.

def test_client_no_token(monkeypatch):
    # Monkeypatch graphistry.api_token to return None
    monkeypatch.setattr(graphistry, "api_token", lambda: None)
    client = louieai.LouieClient()
    with pytest.raises(RuntimeError) as excinfo:
        client.ask("anything")
    err = str(excinfo.value)
    assert "No Graphistry API token" in err
Explanation:
We create a DummyResponse class to mimic httpx.Response partially. raise_for_status will throw if status >= 400 to simulate an HTTP error.
In test_client_uses_graphistry_token: we monkeypatch graphistry.api_token to always return "fake-token". Then monkeypatch httpx.post to a lambda that returns DummyResponse with {"result": "ok"}. That means when client.ask() calls httpx.post, it gets our dummy response. We then check that result equals the dummy data. (We assume if headers were wrong, maybe not relevant as DummyResponse doesn't care. This just tests flow.)
In test_client_no_token: monkeypatch graphistry.api_token to None, then ensure calling ask raises RuntimeError and the message contains our expected substring.
We use pytest.raises to check exception.
Importing louieai ensures that our __init__.py exposure of LouieClient works.
We used monkeypatch fixture (pytest provides it, so it should be available).
Note: We import httpx inside the test after monkeypatch; but we should import at top. Actually, monkeypatching after import is fine. We might do import httpx at module level instead for clarity, then monkeypatch attribute.
Ensure to import pytest to use raises.
Run tests: Execute pytest -q tests/test_louie_client.py. Both tests should pass:
For the first test, if something is off in our implementation (like if we mis-typed graphistry.api_token call), the monkeypatch might not intercept. But since we used the correct attribute, it should.
For the second test, we expect our error message "No Graphistry API token found..." which we assert partially.
If tests fail, adjust code accordingly. Possibly adjustments:
If the monkeypatch of httpx.post doesn't work because our client imported httpx differently (but we import at top of client, so monkeypatching httpx.post should apply, as long as it's in same module).
Or if our exception is slightly different in wording, adjust assertion.
Commit tests: Add tests/test_louie_client.py to git and commit as "test: add initial tests for LouieClient".
Final Phase1 verification: Now run the full test suite and tools:
pytest -xvs for all tests (should run our 2 tests, pass).
ruff . and mypy . again to ensure no new issues (our tests might introduce some:
e.g., ruff might complain if DummyResponse doesn't follow naming conventions (class name is fine). Or unused import of builtins (we didn't end up using builtins, remove that import).
Mypy might complain about monkeypatch setattr signatures but usually not.
Fix any minor things (like remove unused imports).
All checks should be green.
Success Criteria:
We have at least two tests covering key behaviors.
Running pytest yields "2 passed" (or similar) with no failures.
Lint and type-check still pass across code and tests. (If some linter rule complains about test style, e.g., maybe line length, we adjust formatting).
The commit history now contains the test addition.
Result:
[Fill this in with commands, output, decisions, errors, etc.]

Step 1.5.0: Configure documentation scaffolding (MkDocs and ReadTheDocs)
Status: ⏳ PENDING
Started: [timestamp]
Action: Set up the basic documentation infrastructure so that Read the Docs can build it. Claude should:
Create docs index: In the docs/ directory, create an index.md file. This will be the homepage of our docs. Write a brief introduction:
# LouieAI Python Client

Welcome to the **LouieAI** Python client library documentation.

**LouieAI** is Graphistry's genAI-native investigation platform. This library allows Python applications to interact with LouieAI via its API, leveraging Graphistry authentication.

## Installation

You can install the package via pip:
```bash
uv pip install louieai
```
(Note: The package may not be on PyPI yet if you're reading early.)

## Usage Example

```python
import graphistry
from louieai import LouieClient

# First, authenticate with Graphistry (replace with your credentials or key)
graphistry.register(api=3, username="your_user", password="your_pass")

client = LouieClient()
response = client.ask("What insights can you find about X dataset?")
print(response)
```

This will send the prompt to LouieAI and return a response (e.g., an answer or a visualization link).

See the [Architecture](architecture.md) page for more details on how LouieAI and Graphistry integrate.
- Ensure proper fencing of code blocks in Markdown. We provided a usage snippet and reference to an Architecture page we'll create.
- Keep content minimal but informative.
Create docs/architecture.md: This page will hold the architecture overview (very brief for now):
# Architecture Overview

The **LouieAI client library** is designed to be lightweight. It primarily wraps calls to the LouieAI REST API.

- It uses the [PyGraphistry](https://github.com/graphistry/pygraphistry) library for authentication. You must login to Graphistry (cloud or on-prem) using `graphistry.register()` before using LouieAI functions.
- The core class `LouieClient` handles communication with LouieAI. It takes your prompt or query and sends it to the LouieAI service at `den.louie.ai`, using your Graphistry auth token for authorization.
- Responses are returned as Python data structures (parsed from JSON). In future versions, the client may support additional features like streaming responses or advanced query parameters.

**Note:** LouieAI is an evolving platform. This client is in early development (Alpha) and currently provides a basic interface for prompts. Future enhancements will include more robust error handling, support for different endpoints (dashboards, agents, etc.), and asynchronous call support.
This is a stub overview; it sets the stage for more details later.
Create mkdocs config: In the project root, create mkdocs.yml with content:
site_name: LouieAI Client Documentation
site_url: https://louieai.readthedocs.io
nav:
  - Home: index.md
  - Architecture: architecture.md
docs_dir: docs
This simple config sets the site name and nav items (Home and Architecture).
We might want to include README as well, but typically we keep docs separate. We can integrate README later or link to it.
If using mkdocs-material, we could specify theme in config:
theme:
  name: material
(We have mkdocs-material installed, so let's use it.)
So final mkdocs.yml might be:
site_name: LouieAI Client
site_description: Documentation for the LouieAI Python client library.
site_url: https://louieai.readthedocs.io
nav:
  - Home: index.md
  - Architecture: architecture.md
theme:
  name: material
docs_dir: docs
Save this file.
Create ReadTheDocs config: Add a .readthedocs.yml at the root:
version: 2
build:
  os: ubuntu-22.04
  tools:
    python: "3.9"
  jobs:
    - requirements: docs/requirements.txt
sphinx:
  builder: "mkdocs"
Explanation:
We specify using mkdocs builder directly.
For ReadTheDocs to install our dependencies, one method is to use a docs/requirements.txt. Alternatively, since we have extras, we could instruct RTD to use uv pip install .[docs]. But easiest is to create docs/requirements.txt listing our needed packages:
Create docs/requirements.txt: In docs/requirements.txt, list:
louieai[docs]
This tells RTD to install our package with the docs extras (which includes mkdocs and material). This way, RTD will have the package (so it can import louieai if needed for autodoc, though we're not using autodoc now) and the doc generator.
Alternatively, list mkdocs and mkdocs-material explicitly here. But using the extra is neat, plus ensures it installs our package (which might be needed if we had code to auto-document, but as of now, not strictly necessary; however, installing the package also ensures Graphistry gets installed in doc build, which might not be needed unless we run code).
We'll go with installing our own package for simplicity.
Verify local docs build (optional): If we want, run mkdocs build locally to ensure no errors in config or markdown. It should generate a site in site/ directory. Check that.
MkDocs might emit warnings if e.g. there's no index or such, but we have index.
If any issues, fix them. (Make sure YAML is valid, etc.)
Stage and commit: Add docs/index.md, docs/architecture.md, mkdocs.yml, .readthedocs.yml, docs/requirements.txt to git. Commit with "docs: add MkDocs configuration and initial docs".
Success Criteria:
The docs/ folder has at least index.md and architecture.md with basic content.
mkdocs.yml exists and is correct (we can test by running mkdocs build or mkdocs serve locally).
.readthedocs.yml exists for RTD integration.
docs/requirements.txt ensures RTD will install the package with docs extras.
The commit is made. We expect that when pushed, ReadTheDocs (if configured with the repo) will pick up the config and successfully build the site.
Result:
[Fill this in with commands, output, decisions, errors, etc.]

Step 1.6.0: Write essential project documentation files (README, CONTRIBUTING, etc.)
Status: ⏳ PENDING
Started: [timestamp]
Action: Add the top-level documentation and community files. Claude should:
Create README.md: This is the public-facing description on GitHub and PyPI. Include:
Project name and short description.
Badges: We should add placeholders for CI status badge and PyPI version and license.
CI badge: Once we name our workflow (say "CI"), we can use: ![CI](https://github.com/<owner>/louieai/actions/workflows/ci.yml/badge.svg). We might not know the owner now, but if Graphistry or user is known, fill accordingly. If not, leave a template or note to fill in.
PyPI version badge: e.g., ![PyPI](https://img.shields.io/pypi/v/louieai.svg) which shows latest version on PyPI.
License badge: ![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg).
Introduction: what LouieAI is and what this client does.
Installation instructions (pip install).
Basic usage example (similar to what we put in docs index, but usually README also has one).
Links:
Louie.ai website (https://louie.ai),
PyGraphistry (maybe link to PyGraphistry GitHub or documentation),
Documentation (link to readthedocs page).
Contributing info: point to CONTRIBUTING.md for details and mention we welcome contributions.
Status: note that this is an initial release (alpha).
License mention.
An outline for README.md:
# LouieAI – Python Client Library

[![CI](https://github.com/<owner>/louieai/actions/workflows/ci.yml/badge.svg)](https://github.com/<owner>/louieai/actions/workflows/ci.yml)
[![PyPI Version](https://img.shields.io/pypi/v/louieai.svg)](https://pypi.org/project/louieai/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

**LouieAI** is an AI-driven investigative platform by [Graphistry](https://www.graphistry.com) that brings generative AI into data analysis. This repository contains the **Python client library** for LouieAI, allowing developers to send natural language prompts/queries to LouieAI and get results programmatically.

## Features
- **Easy Authentication**: Leverages PyGraphistry's authentication. Log in once with Graphistry, and LouieAI uses the same session.
- **Simple API**: Ask questions via the `LouieClient.ask(prompt)` method and receive answers or visualizations.
- **Integration**: Responses can include Graphistry visualizations, database queries, and more as generated by LouieAI.

*This package is in early development (Alpha stage). Core functionality is minimal but the scaffold for expansion is in place.*

## Installation

Requires Python 3.8+ and an existing Graphistry account.

Install from PyPI:
```bash
uv pip install louieai
```

(Until published, you can install from source via pip or uv:)
```bash
uv pip install git+https://github.com/<owner>/louieai.git
```

## Quick Start

```python
import graphistry
from louieai import LouieClient

# Authenticate to Graphistry (replace with your credentials or API token)
graphistry.register(api=3, username="your_user", password="your_pass")

client = LouieClient()
result = client.ask("Summarize the latest alerts in Splunk and graph the entities.")
print(result)
```

This will send your prompt to the LouieAI service. The result might be a JSON containing an answer or instructions (for example, a link to a Graphistry visualization).

See the [documentation](https://louieai.readthedocs.io) for more details and examples.

## Links

- [Louie.ai Homepage](https://louie.ai) – Learn about the LouieAI platform.
- [PyGraphistry Documentation](https://github.com/graphistry/pygraphistry) – Learn how to set up Graphistry, which is required for LouieAI.
- [Project Documentation](https://louieai.readthedocs.io) – Full documentation on ReadTheDocs.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. We have a structured AI-involved development workflow – check out the AI planning template in `AI_PROGRESS/` if you're interested in how we use AI to assist development.

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## License

Licensed under the Apache 2.0 License. See [LICENSE](LICENSE) for details.

**Why Apache-2.0?** The Louie Python client is Apache-2.0 licensed to maximize adoption and make it easy to embed in Splunk apps, Jupyter notebooks, and internal tools. Contribute code with a simple Signed-off-by: line—no paperwork required. While the Louie server and cloud agents remain under our commercial license, this open client ensures seamless integration everywhere.
Replace `<owner>` with the actual GitHub owner/org when known. If unknown, we leave a placeholder or put something like `graphistry` if likely hosted there.
- The example usage and installation refer to pip, and note the dev status.
- We link to docs and mention Graphistry and Louie.
Create CONTRIBUTING.md: Outline how to contribute:
# Contributing to LouieAI Python Library

Thank you for your interest in contributing! We welcome contributions via pull requests.

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

## Development Setup

- **Prerequisites**: Python 3.8+ and pip. You'll also need an account on Graphistry's platform to test against LouieAI.
- **Fork & Clone** this repository.
- **Install in dev mode**: `uv pip install -e ".[dev]"` to get all dependencies and tools.
- We use **pre-commit** hooks (to be set up in a later phase) for linting and formatting, and CI will run tests, linters (ruff), and mypy.

## Branching and GitFlow

We follow a GitFlow-like process:
- Work on a feature or fix in a branch (e.g., `feature/<name>` or `bugfix/<name>`).
- Submit a Pull Request to the `main` branch. Ensure all CI checks pass.
- Include a clear description of the change and reference any issue it addresses.

## Coding Guidelines

- Run `ruff` and `mypy` to ensure code style and type safety.
- Use type hints for all functions.
- Write or update tests for any new functionality (we aim for good coverage).
- Keep functions and classes documented with docstrings.

## Using AI Planning (Optional)

This project uses an AI co-pilot approach for some development tasks. We have an AI planning template under `AI_PROGRESS/PLAN_TEMPLATE.md`. If you'd like to use an AI assistant to help code, you can follow a similar approach (see `AI_PROGRESS/` for past plans). This is entirely optional but can help maintain consistency and traceability when using AI tools.

## Reporting Issues

Please open issues for bug reports or feature requests. Include as much detail as possible.

## Security

If you find a security vulnerability, please follow the instructions in [SECURITY.md](SECURITY.md).

-- Happy coding! --
We mention the AI planning template and how we use it, aligning with the user's request to include "starter prompt AI planning files".
We outline typical steps including DCO sign-off requirement.
We mention we plan to use pre-commit (even if not yet in Phase1, it's fine to hint).
Create CODE_OF_CONDUCT.md: We can use the standard Contributor Covenant text (version 2.1 or so). For brevity, outline:
# Contributor Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) Code of Conduct.

**Our Pledge**: In the interest of fostering an open and welcoming environment, we as contributors and maintainers pledge to make participation in our project a harassment-free experience for everyone.

**Our Standards**: ( *Include key points: use welcoming language, be respectful of differing viewpoints, gracefully accept constructive criticism, show empathy towards others.* )

**Enforcement**: Instances of abusive behavior may be reported to the project maintainers at [INSERT CONTACT EMAIL].

The full text of the Code of Conduct is linked above. By contributing to this project, you agree to abide by its terms.
(We condensed it. Optionally, include full text of v2.1 from Contributor Covenant, which is lengthy. For now, a summary plus link is okay. If needed, we can expand or use GitHub's CoC template later.)
Add a contact email (e.g., support@graphistry.com or a placeholder).
Create SECURITY.md: Provide guidance for vulnerability reporting:
# Security Policy

## Supported Versions
This project is in alpha; all versions are under active development.

## Reporting a Vulnerability
If you discover a security issue in this library or the LouieAI service:
- **Do not open a public issue.** Please report it confidentially by emailing security@graphistry.com (or another appropriate contact).
- Include as much information as possible to help us understand and reproduce the issue.
- We will acknowledge receipt within 5 working days and give you an estimate of the next steps.

We take security seriously and will address any issues as a priority.
Use a plausible email for Graphistry's security or a placeholder if unknown.
Prepare AI planning template: We have AI_PROGRESS directory from step 1.0.0. Now add the planning template file. Path: AI_PROGRESS/PLAN_TEMPLATE.md (or similar). Copy the content from the user-provided template:
Include the entire text from the beginning (Critical Rules, Step Execution Protocol, etc.) exactly as given, since it's meant to be copied for new tasks.
The template instructs to delete the meta section when using, but we keep it here as the template.
Ensure to escape any markdown inside if needed? Actually, it's mostly commented in the template (they used HTML comments for deletion hints).
Just include it as is, to ensure the same guidelines are available.
This will be a large file (~200+ lines). It's fine – it's not loaded normally except by contributors.
We should mention this in README or CONTRIBUTING which we did (pointing to it).
Stage and commit: Add all these files: README.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, AI_PROGRESS/PLAN_TEMPLATE.md. Commit with message "docs: add README, CONTRIBUTING, CoC, SECURITY, and AI planning template".
Success Criteria:
All listed files are present with comprehensive content.
The README contains expected sections (and placeholders are noted to update once repo is live).
CONTRIBUTING gives clear guidelines and references our AI planning process.
CODE_OF_CONDUCT and SECURITY provide necessary info.
The AI plan template is included verbatim so future tasks can use it.
The commit is done. Now our repository is essentially complete for Phase 1: it has code, tests, docs, CI config (to be done next), and all community docs.
Result:
[Fill this in with commands, output, decisions, errors, etc.]

Step 1.7.0: Add GitHub Actions workflows for CI and Publishing
Status: ⏳ PENDING
Started: [timestamp]
Action: Set up continuous integration and deployment workflows. Claude should:
Create CI workflow: In .github/workflows/ci.yml, define a workflow that runs on pushes and PRs. For example:
name: CI
on:
  push:
    branches: ["main", "develop", "feature/*"]
  pull_request:
    types: [opened, synchronize, reopened]
jobs:
  build-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: uv pip install -e ".[dev]"
      - name: Lint (ruff)
        run: ruff . --exit-zero  # Use exit-zero to not fail the job on lint warnings for now (optionally, enforce later)
      - name: Type Check (mypy)
        run: mypy .
      - name: Run Tests
        run: pytest -q
Explanation:
We run on push to main, develop, and any feature branch (so that even feature branch pushes get CI, not just PR).
We also run on PR creation/update.
We use a matrix to test multiple Python versions. This ensures compatibility across.
Steps: checkout, setup Python, install all dependencies (using dev extras so we get test and lint tools).
Then run ruff. We might set --exit-zero initially to not fail the build on lint issues until we're comfortable. But since we plan to keep code lint-clean, we can omit --exit-zero to enforce. We'll enforce (so remove --exit-zero if we trust our code).
Run mypy.
Run pytest quietly.
We might add -x to pytest to stop on first fail if desired, but in CI it's fine to run all. -q is just to keep log short.
If any step fails (non-zero exit), the job fails, which is what we want.
We are not building docs in CI (ReadTheDocs will handle docs).
We do not run packaging build here explicitly, but uv pip install -e implicitly builds. We might add a step to attempt uv pip wheel . or python -m build to ensure packaging is OK. Could do:
    - name: Build Package
      run: python -m build --wheel .
but requires adding uv pip install build before, unless we already have it via setuptools? Maybe skip for now. The packaging is simple enough.
Save ci.yml.
Create Release workflow: In .github/workflows/release.yml:
name: Publish to PyPI
on:
  push:
    tags:
      - "v*.*.*"
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.9"
      - name: Install build tools
        run: uv pip install build twine
      - name: Build package
        run: python -m build .
      - name: Publish
        env:
          TWINE_USERNAME: "__token__"
          TWINE_PASSWORD: "${{ secrets.PYPI_API_TOKEN }}"
        run: twine upload dist/*
Explanation:
Triggers on pushing a tag that matches vX.Y.Z format.
It checks out code, sets up Python.
Installs build and twine (to create distribution and upload).
Builds source and wheel into dist/ directory.
Then uses twine to upload. We use an API token stored in secrets (PYPI_API_TOKEN) with username __token__ as PyPI expects.
This will fail if PYPI_API_TOKEN is not set. We must instruct maintainers to add it (in Graphistry's GitHub secrets).
The job ends after uploading. (We could add a conditional to skip on PR, but since it only triggers on tags, PRs won't trigger it.)
Save release.yml.
(Optional) Pre-commit hooks: Actually, we planned to do pre-commit in Phase 3, so we skip adding .pre-commit-config.yaml now. We'll do that later. For now, CI covers most checks.
Stage and commit: Add the new YAML files. Commit as "ci: add GitHub Actions workflows for CI and release".
Success Criteria:
The .github/workflows/ci.yml and release.yml files are present and correctly configured (no YAML syntax errors).
CI is set up to run tests, lint, mypy on pushes/PRs and covers multiple Pythons.
Release workflow is ready to push to PyPI on tag (with the expectation that a secret is configured).
The commit is made. We should ensure to push these to test them, but since we can't here, we'll rely on review. Any issues noticed (like missing quotes or wrong indent) should be corrected now. We can do a quick yamllint if available. Otherwise, trusting formatting.
Result:
[Fill this in with commands, output, decisions, errors, etc.]

Step 1.8.0: Finalize Phase 1 – Push branch and verify CI passes
Status: ⏳ PENDING
Started: [timestamp]
Action: Conclude Phase 1 by pushing the changes to GitHub and making sure everything runs. Claude should:
Review all changes: Double-check that all files are in place:
LICENSE (Apache text),
Code under src/louieai/ (init and client),
Tests under tests/,
Docs in docs/ plus configs (mkdocs.yml, .readthedocs.yml),
Project docs (README, etc.),
Workflows in .github/workflows/.
Ensure no TODOs or placeholders left that should be replaced. Possibly update README's <owner> if we know who will own the repo (if Graphistry, maybe use graphistry).
But if unknown or private user, leave a note that it should be replaced.
Push branch: Run git push -u origin feature/initial-scaffold. If authentication required, ensure it's done.
Open Pull Request: This might be done via web or CLI (gh pr create --fill). The PR description can be brief referencing this plan.
Since this is the initial commit, in some workflows they push directly to main. But we follow branch/PR to trigger CI properly.
After opening PR, monitor GitHub Actions:
Check that the CI workflow starts for each Python matrix entry.
It will run install, ruff, mypy, pytest.
If any step fails:
If it's lint/mypy/test related, fix in code accordingly and update plan if needed.
If it's YAML or CI config issue (like a syntax mistake causing the workflow not to run at all), then the workflow might not trigger. If so, check the Actions tab for errors. Possibly the YAML has indent issues – fix and push again.
The most likely failure might be:
Mypy complaint if any or
Pytest failing because maybe no tests found is an error? Actually, with our tests, it should find 2 tests. If none, Pytest exit code 5 might fail the job. We covered that by adding tests.
ruff . might raise a nonzero exit on any warning (we did not add --exit-zero, so it enforces).
If any minor style issue was overlooked (like trailing whitespace or something), ruff will fail CI. We'll catch and fix such issues:
Run ruff --fix . locally to auto-fix if any, then push fix.
Installing dev dependencies might fail if a version constraint issue or missing package:
Eg, "types-requests" might not be needed for httpx and might not install if Python version conflict. If it fails, remove it or adjust.
Or PyPI name for graphistry is "graphistry" which we used, so that should be fine. If not, use pygraphistry (but I believe it's graphistry).
If Graphistry requires a specific Python or OS, but it's pure Python so should be fine.
Our test that monkeypatches httpx might need import adjustments if failing (but likely fine).
Once CI passes for all jobs (3.8 through 3.11), we have succeeded.
Merge PR: After approval (could be self-approved if no others) and CI green, merge into main.
After merge, optionally tag a release (maybe we wait until Phase 2 to do an actual release).
But we can consider tagging v0.0.1 as initial dev release to test the publish workflow. If we had PyPI token and wanted to test, we could, but often they'd wait for something more functional to release.
We'll plan official release after Phase 2. So no tagging now.
Mark Phase 1 complete: Document in plan that Phase 1 minimal setup is done and that we proceed to Phase 2 next.
Success Criteria:
The branch is successfully pushed and PR is created.
All CI checks run and pass on the PR (each Python version job passes all steps).
The PR is merged into main. The main branch now contains the Phase 1 commits.
The repository is now a functional Python package repository with baseline features, satisfying Phase 1 goals.
We have not published to PyPI yet, which is expected.
Phase 1 deliverables (structure, config, CI, docs, stub code) are achieved.
Result:
[Fill this in with commands, output, decisions, errors, etc.]

Phase 1 Complete
After completing Step 1.8.0, Phase 1 is complete. The repository now has:
- All code, tests, and documentation files
- GitHub Actions CI/CD workflows configured
- All community files (README, CONTRIBUTING, etc.)
- CI passing on all Python versions
- Repository merged to main branch

The package is ready for Phase 2 development where we will implement core functionality.

Next: Continue to [Phase 2 - Core Functionality](plan-phase-2.md)