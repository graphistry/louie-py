LouieAI_Bootstrap Plan
THIS PLAN FILE: AI_PROGRESS/LouieAI_Bootstrap/plan.md
Created: 2025-07-25 21:01:56 PST
Current Branch if any: (none, repository initialization)
PRs if any: None (initial project setup)
PR Target Branch if any: main (default branch for initial merge)
Base branch if any: main See further info in section ## Context
CRITICAL META-GOALS OF THIS PLAN
THIS PLAN MUST BE:
FULLY SELF-DESCRIBING: All context needed to resume work is IN THIS FILE.
CONSTANTLY UPDATED: Every action’s results recorded IMMEDIATELY in the step.
THE SINGLE SOURCE OF TRUTH: If it’s not in the plan, it didn’t happen.
SAFE TO RESUME: Any AI can pick up work by reading ONLY this file.
REMEMBER: External memory is unreliable. This plan is your ONLY memory.
CRITICAL: NEVER LEAVE THIS PLAN
YOU WILL FAIL IF YOU DON’T FOLLOW THIS PLAN EXACTLY
TO DO DIFFERENT THINGS, YOU MUST FIRST UPDATE THIS PLAN FILE TO ADD STEPS THAT EXPLICITLY DEFINE THOSE CHANGES.
Anti-Drift Protocol - READ THIS EVERY TIME
THIS PLAN IS YOUR ONLY MEMORY. TREAT IT AS SACRED.
The Three Commandments:
RELOAD BEFORE EVERY ACTION: Your memory has been wiped. This plan is all you have.
UPDATE AFTER EVERY ACTION: If you don’t write it down, it never happened.
TRUST ONLY THE PLAN: Not your memory, not your assumptions, ONLY what’s written here.
Critical Rules:
ONE TASK AT A TIME – Never jump ahead.
NO ASSUMPTIONS – The plan is the only truth. If you need new info, update the plan with new steps to investigate, document, replan, act, and validate.
NO OFFROADING – If it’s not in the plan, don’t do it.
Step Execution Protocol – MANDATORY FOR EVERY ACTION
BEFORE EVERY SINGLE ACTION, NO EXCEPTIONS:
RELOAD PLAN: cat AI_PROGRESS/LouieAI_Bootstrap/plan.md | head -200
FIND YOUR TASK: Locate the current 🔄 IN_PROGRESS step.
EXECUTE: ONLY do what that step says.
UPDATE IMMEDIATELY: Edit this plan with results BEFORE doing anything else.
VERIFY: tail -50 AI_PROGRESS/LouieAI_Bootstrap/plan.md
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
Plan Overview
Raw Prompt: Create a step-by-step multi-phase PLAN.md for bootstrapping the louieai open-source Python library repository using the user's provided planning template and goals. The repo should: - Be a minimal but functional public Python OSS package, hosted on GitHub, licensed under Apache 2.0.
- Be installable via pip and uv.
- Use pyproject.toml with PEP 621-style configuration.
- Include pinned dev dependencies and relaxed prod dependencies, using a lockfile only for internal tooling if possible.
- Depend on pygraphistry, httpx, pandas, pyarrow for production only. Other dependencies should be dev-only and minimal.
- Be safely typed (e.g., mypy or pyright), linted (ruff), and CI-checked via GitHub Actions.
- Use a docs system suitable for hosting on readthedocs.org (prefer modern markdown-based tooling like mkdocs).
- Include good OSS practices like README.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, architecture overview, security policy, and starter prompt AI planning files.
- Include usage badges, links to Louie.ai and pygraphistry in README.md.
- Use GitFlow conventions and set up GitHub Actions for testing, linting, type-checking, packaging, and publishing to PyPI.
- Include a base implementation of LouieClient targeting https://den.louie.ai, with auth passthrough via pygraphistry.
- Phase 1 should define a minimal viable setup: complete repo structure, pyproject, CI jobs, typed stub client, doc scaffolding, etc. Later phases will extend functionality, documentation depth, and dev experience polish. For all Claude-executed steps, include clearly labeled meta-instructions for how Claude should research, plan, or code that part. Goal: Set up the initial code repository for the LouieAI Python client library, ensuring it meets all listed requirements and best practices. We will deliver a structured plan that spans multiple phases of development, starting from a minimal viable package through to a fully functional and polished open-source project. Description: The task is to bootstrap a new open-source Python package called louieai. Phase 1 will create the foundational repository structure, packaging config (PEP 621 in pyproject.toml), initial stub implementation of LouieClient class connecting to Louie.ai, CI pipelines, documentation scaffolding (mkdocs for readthedocs), and essential OSS files (license, README, etc.). Subsequent phases will expand the client functionality, improve documentation, and enhance developer experience (type checks, lint, pre-commit hooks, etc.), following GitFlow and publishing the package on PyPI. Context: Louie.ai is an AI-driven investigation platform integrated with Graphistry. This package will serve as a client library to interact with Louie.ai's API (den.louie.ai) from Python, leveraging Graphistry’s authentication (PyGraphistry). The project must be a clean, modern Python codebase with proper packaging and documentation to be publicly released on GitHub under Apache-2.0 license. We have a planning template that dictates how to structure our plan and a set of best practices to include. We must ensure only pygraphistry, httpx, pandas, pyarrow are used as runtime dependencies. All other tools (linters, docs, testing) are dev dependencies. The CI/CD pipeline should automatically test, lint, type-check, and publish the package. We will use GitFlow branching, meaning feature work is done on separate branches and merged via PR into main (or a develop branch) and releases are tagged. Success Criteria: By the end of Phase 1, the repository should be usable as a Python package: one can install it (e.g. pip install . or via uv) and import louieai. The LouieClient class exists with a stub method, and the project passes CI checks (no lint or type errors, tests pass). Documentation builds (though minimal content) on readthedocs. All mandatory files (LICENSE, README with badges and links, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, architecture overview, AI planning template) are present. The package can be published to PyPI via the configured GitHub Actions workflow (though actual publishing may occur after Phase 2 when functionality is fleshed out). In later phases, success means the client can actually communicate with the Louie.ai API using Graphistry auth, documentation is sufficiently detailed for users (including usage examples), and developer tooling (like pre-commit hooks, coverage, etc.) is in place. The repository should meet community standards for an open-source Python project by the final phase. Key Constraints:
Packaging: Must use a single pyproject.toml with PEP 621 metadata (no setup.py or setup.cfg). Build backend either Setuptools or Hatchling, but final config should allow installation via pip and the new uv tool. The package name is louieai and should be published to PyPI under that name.
Dependencies: Only four production dependencies are allowed: pygraphistry, httpx, pandas, pyarrow. These should be specified with relatively broad version ranges (no strict pinning in install requirements). All development tooling (linters, formatters, docs, tests) must not be installed with the library by end users. Instead, use optional dev dependencies (like .[dev]) or separate dev requirements file. If a lockfile is used, it should only lock dev environment (for reproducible CI), not pin the library’s own requirements for users.
Code Quality: The code must include type hints (compatible with mypy) and be linted with ruff. We must configure CI to run these checks on every push/PR. We’ll target Python 3.8+ (ensuring type annotations and language features remain compatible).
Documentation: We will set up MkDocs for documentation with a ReadTheDocs configuration. Documentation content will start minimal (just an index and maybe an architecture page), but structure must be in place for future expansion. Also, embed essential info in the README (badges for CI status, PyPI version, license; description of the project; links to Louie.ai site and PyGraphistry).
OSS Formalities: Include Apache 2.0 LICENSE file; a README.md that gives an overview and usage example; a CONTRIBUTING.md outlining how to contribute (and referencing our AI planning process if relevant); a CODE_OF_CONDUCT.md (adapted from a standard template like Contributor Covenant); a SECURITY.md with instructions for reporting vulnerabilities; an ARCHITECTURE.md giving a high-level overview of the system design and how LouieClient works; and an AI planning template file (as provided) so that future development tasks can follow the same structure.
Git & CI: Use a GitFlow-inspired workflow. The initial development can happen on a branch (e.g., feature/initial-setup) and then merged to main. We’ll set up GitHub Actions workflows: one for CI (run tests, lint, mypy on pushes/PRs) and one for releasing to PyPI (triggered on version tags). Secrets like PyPI API token must be assumed to be added in the repo settings for the workflow. Ensure the CI passes before finishing Phase 1.
LouieClient Implementation: Initially, implement a basic LouieClient that can retrieve an auth token from PyGraphistry (using graphistry.api_token()) and includes a method (e.g., ask() or query()) that sends a request to the Louie API endpoint (we will assume or find an endpoint). The actual functionality can be minimal or stub (e.g., not executing real requests yet) in Phase 1, but should be structured for extension. We must ensure the class has proper type hints and error handling scaffolding. In later phases, we’ll flesh it out to make real HTTP calls to den.louie.ai and handle responses.
Phase Deliverables:
Phase 1: Functional skeleton (passes tests and CI, but minimal features).
Phase 2: Core features implemented and documented (LouieClient fully working with Louie.ai API, documentation expanded, more tests).
Phase 3: Additional polish (pre-commit hooks, code formatting with Black, code coverage, and any remaining improvements), culminating in a first release (version 0.1.0) published to PyPI.
Technical Context
Initial State:
Working Directory: (Assumed to be an empty or newly initialized git repository directory for louieai project)
Current Branch: main (this is the default branch; we will create feature branches as needed)
Target Branch: main (all initial work will merge into main or a dev branch per GitFlow; since this is initial commit, main will be the target for PR)
Related Work:
None (this is a brand new repository, no prior PRs or issues).
Depends on: No external dependencies beyond standard tools and PyPI packages (Graphistry account for testing actual API would be needed eventually, but for now we can stub or simulate calls).
We assume internet access is available to install packages and fetch license text, etc.
Blocks: Once this plan is executed, it will unblock publishing the library and further contributions from the community or team, as the project scaffolding will be in place.
Strategy
Approach: We will follow a phased development approach, starting with the absolute essentials to make the repository functional and compliant with standards. Phase 1 focuses on scaffolding:
Setting up version control and base folder structure (src/louieai, tests, docs, workflows).
Writing pyproject.toml with proper metadata (project name, version, authors, dependencies, etc.) using PEP 621.
Creating minimal code (LouieClient class with stubbed method and just enough to be importable).
Adding all required files like license and contributor docs.
Configuring GitHub Actions for continuous integration (lint/type check/test) and release.
Very basic documentation scaffolding (so readthedocs won't fail).
We will verify at the end of Phase 1 that one can build and install the package locally, run ruff and mypy with no errors, and that the GitHub Actions pipeline would succeed on these checks.
Phase 2 will then flesh out functionality:
Implement the LouieClient.ask() method to actually call the Louie API (using httpx for HTTP requests). If documentation about the API is unavailable, we will infer or create a plausible endpoint and payload structure (e.g., a POST request with a prompt to den.louie.ai).
Ensure that Graphistry authentication is properly integrated (e.g., requiring graphistry.register() to be called by the user, then using the JWT from graphistry.api_token() in the Authorization header).
Add error handling (e.g., raise exceptions if not authenticated or if HTTP requests fail).
Expand the test suite to cover these new features (likely by mocking HTTPX responses and Graphistry token).
Expand documentation: provide an example usage in the README and a usage guide in docs (with instructions on how to set up Graphistry and call LouieClient).
Ensure the README has all badges (CI, PyPI version, license) and correct links.
Phase 3 will focus on developer experience and polish:
Introduce a pre-commit configuration to automate linting/formatting on commits (with ruff and potentially black for code formatting).
Possibly integrate a formatting tool like Black (for strict code style) as an optional dev dependency and in CI.
Add any missing pieces like a CHANGELOG.md (if desired) and issue/PR templates.
Implement code coverage measurement in CI (using pytest --cov and uploading to Codecov or similar), to monitor test coverage.
Make final adjustments to documentation (ensuring no TODOs remain, all sections like architecture are filled out).
Bump version number appropriately and create a release tag to trigger the publish workflow. Verify that the package is uploaded to PyPI and can be installed via pip.
Throughout, maintain GitFlow discipline: use feature branches for new changes, then PR merge into main (or develop). For initial development we might use feature/phase2-features and feature/phase3-polish etc.
Key Decisions:
Build System: Use Setuptools as the build backend with PEP 621 config. (Reasoning: It's widely used and will allow publishing to PyPI easily. We will put metadata in [project] table of pyproject.toml. We'll configure it for a src/ layout via tool.setuptools.packages.find. Hatchling was an option, but sticking to setuptools is straightforward given our needs.)
Dependency Specification: Relaxed version pins for runtime deps (we’ll specify minimal versions or none, e.g., pygraphistry>=0.34 without upper bounds, trusting semantic versioning). Dev dependencies will be pinned exactly to ensure consistent lint/test behavior (e.g., ruff==0.12.0, etc.) and listed under optional-dependencies.dev. We will not create a lockfile in Phase 1; if needed, we might generate a requirements-dev.txt via pip-compile in a later phase, but not initially.
Documentation Tool: Use MkDocs with a simple theme (Material for MkDocs) for documentation, instead of Sphinx. Markdown is easier to maintain and integrates with readthedocs. We'll include a .readthedocs.yml pointing to use mkdocs. (Reasoning: modern, supports MarkDown, easier to get started quickly.)
Testing Framework: Use pytest for testing. (Reasoning: Standard in Python, will integrate well with CI and coverage.)
Type Checking: Use mypy for static type checking. (Reasoning: We choose mypy as it's widely used, even though pyright is an option. Mypy will run in CI to ensure type safety.)
Linting/Formatting: Use Ruff as the primary linter (enforcing flake8/pylint rules at high speed). We will also include Black in a later phase for consistent code formatting (Black wasn’t explicitly mentioned but is a de-facto standard; we'll integrate it in Phase 3 to polish style). (Reasoning: Ruff covers a broad set of lint rules and even some formatting fixes. Black ensures no bikeshedding on style.)
Continuous Integration: Two GitHub Actions workflows: (1) CI for PRs/commits, running on pushes to feature branches and main, covering install, lint, type-check, and test on multiple Python versions (we will likely test on 3.8, 3.9, 3.10, 3.11 to ensure broad compatibility). (2) Release workflow triggered on creating a Git tag (matching a version pattern), which builds the package and uploads to PyPI. (Reasoning: Separation of concerns – CI vs deploy. Also ensures only tagged commits are released.)
Git Branching: We start on a feature branch even for initial work (e.g., feature/initial-scaffold), though since the repo is empty, it could also be done on main and then retrospectively treated as initial commit. We’ll follow standard practice by doing development on feature branches and merging via PR into main. (Reasoning: Maintains history and CI checks via PR, exemplifies good practice from the start.)
LouieClient Design: The client will be a lightweight wrapper around HTTP calls. We will store a base URL (default to https://den.louie.ai) and possibly allow override if needed. Authentication will not be an explicit parameter; instead, we’ll piggyback on Graphistry’s global auth (user must have called graphistry.register() with credentials, which sets an internal token). Our client will fetch graphistry.api_token() internally. (Reasoning: Simplifies user experience – they authenticate once with Graphistry and that carries over to Louie. Also, avoids managing credentials in two places.)
Starter AI Planning: We will incorporate the provided AI planning template into the repo (probably in an AI_PROGRESS/PLAN_TEMPLATE.md file) and mention our process in CONTRIBUTING.md. (Reasoning: Encourages future contributions to use the same structured approach, which is valuable for consistency and onboarding new AI/human contributors.)
Git Strategy
Planned Git Operations:
Branch Creation: Create a new branch feature/initial-scaffold from main for all Phase 1 work.
For each logical grouping of changes, commit with meaningful message (e.g., "chore: initial project structure", "feat: add pyproject.toml and packaging config", "feat: stub LouieClient and tests", "docs: add README and contributor guides", "ci: add GitHub Actions workflows").
Once Phase 1 steps are complete and everything is validated locally (tests pass, etc.), open a Pull Request from feature/initial-scaffold into main. Ensure CI passes on the PR, then merge it (squash or merge commit as appropriate). Tag this as an initial release (maybe v0.0.1 or just no tag yet until Phase 2 completion).
Phase 2: Create a new branch feature/core-functionality from main (or develop if we decide to introduce a develop branch for ongoing dev).
Commit Phase 2 changes in increments (e.g., "feat: implement LouieClient ask method", "test: add tests for LouieClient", "docs: update usage and architecture docs").
Open PR for Phase 2 into main, ensure all checks pass, then merge.
Phase 3: Branch feature/dev-polish from main, implement enhancements (pre-commit, black, etc.), commit and PR similarly.
Once Phase 3 is merged, bump version to 0.1.0 (if not already done) and create a Git tag v0.1.0 on main to trigger the publish workflow. Verify that the package is released to PyPI.
After release, consider creating a develop branch for any further development if following GitFlow strictly, keeping main only for stable releases.
Merge Order: (Since this is a new project, merge order is simply sequential phases into main.)
No parallel PRs expected. If they were: [Phase 1 PR] → [Phase 2 PR] → [Phase 3 PR]. But in practice, we will merge Phase 1 before starting Phase 2, etc.
Quick Reference (READ-ONLY)
# Reload plan
cat AI_PROGRESS/LouieAI_Bootstrap/plan.md | head -200

# Local validation before pushing (Phase 1)
ruff . && mypy .
pytest -xsv

# To run specific tools:
./bin/ruff check --fix    # (if we create bin wrappers for ruff; otherwise just `ruff --fix`)
./bin/mypy                # (or `mypy`)
pytest -xvs               # run tests verbosely
# (shellcheck for any shell scripts if present, but we likely won't have any in this Python project)

# CI monitoring (via GitHub CLI):
gh pr checks <PR-number> --repo <owner>/louieai --watch  # watch PR checks
gh run watch <run-id>                                   # watch a specific workflow run
watch -n 30 'gh pr checks <PR-number> --repo <owner>/louieai'  # continuously update status every 30s

# Debugging CI early exit example:
echo "DEBUG: Early exit" && exit 0  # line to add in workflows for debugging (remove when done)

# Remember to remove debug exits and re-run CI after fixing issues.
LIVE PLAN (THE ONLY SECTION YOU UPDATE)
Reminder, follow ## Step protocol:
Context Preservation (Update ONLY if directed by a step)
<!-- Only update these sections if a step specifically says to -->
Key Decisions Made
<!-- Document WHY things were done certain ways -->
[Packaging Backend Decision]: Chose Setuptools (PEP 621) because it’s standard and easy to configure for both pip and uv, and allows direct control over packaging specifics (like specifying src layout). This avoids introducing another tool like Poetry/Hatch which might impose stricter dependency locking by default.
[Docs Framework Decision]: Went with MkDocs for documentation due to its simplicity and compatibility with readthedocs (and personal preference for Markdown). This keeps documentation lightweight and easy for contributors to edit.
[Auth Integration Decision]: Decided to rely on PyGraphistry’s api_token() for authentication rather than building a separate auth mechanism. This leverages existing infrastructure and reduces complexity for the user (they only authenticate once).
[Phase Split Decision]: Broke the implementation into 3 phases (scaffold, core features, polish) to ensure that each major milestone (functional package, fully working client, developer experience) is achieved in stages and verified, instead of trying to do everything in one go.
Lessons Learned
<!-- Document what failed and why to avoid repeating -->
[Placeholder]: This section will capture any mistakes or necessary adjustments encountered during execution. (e.g., if CI fails due to a misconfigured pyproject, note the fix here for future reference.)
Important Commands
<!-- Document complex commands that worked -->
# Example: Used curl to fetch standard license text directly from Apache:
curl -sSL "https://www.apache.org/licenses/LICENSE-2.0.txt" -o LICENSE

# Example: Install the package in editable mode with dev extras for local testing:
pip install -e .[dev]
Steps
Step 1.0.0: Phase 1 – Initialize repository and structure
Status: 🔄 IN_PROGRESS
Started: [timestamp]
Action: We start Phase 1 by setting up the basic repository structure and necessary initial files. Claude should:
Initialize Git repository: If this directory is not already a git repo, run git init. If it’s already initialized (perhaps via GitHub), ensure we have a clean working tree.
Create core directories: Make the following directories:
src/louieai/ – for the package source code.
src/louieai should contain an empty __init__.py (we will add content now with version).
tests/ – for test files.
docs/ – for documentation markdown files.
.github/workflows/ – for CI pipeline definitions.
AI_PROGRESS/ – for AI planning files (we will put the template here later).
Create a Python package marker: In src/louieai/__init__.py, write a basic initialization. Define the package version here for reference. Since we plan version "0.1.0" initially (per pyproject), set __version__ = "0.1.0" in this file. This ensures the version is accessible via louieai.__version__ at runtime.
Create a .gitignore: We need a .gitignore at the repo root to ignore typical files:
Python artifacts like __pycache__/, .pytest_cache/, *.py[cod], etc.
Virtual environment directories (e.g., .venv/ if any).
Build artifacts (dist/, build/, *.egg-info).
Possibly .env or secrets files.
.mypy_cache/ for mypy, and .ruff_cache/ if any.
We can use a standard Python .gitignore template.
Add Apache-2.0 LICENSE: Acquire the Apache License text and save to LICENSE file. To ensure accuracy, Claude should fetch the official text. For example, using a shell command:
curl -sSL "https://www.apache.org/licenses/LICENSE-2.0.txt" -o LICENSE
This will download the full Apache 2.0 license text. After downloading, open the LICENSE file and verify that it contains the proper license text (starting with "Apache License Version 2.0, January 2004..."). If there is any placeholder (like the appendix instruction to replace [yyyy] [name] in the license notice), consider adding the current year and owner. For now, we might not have a formal copyright name to put; we could fill "2025 [LouieAI Contributors]" at the top if desired, or leave it generic.
Initial commit: Once the above files and directories are created, stage them (git add .) and commit as "chore: initial project structure and license". (We categorize as chore since it's not a feature yet, just setup.)
Success Criteria:
The repository has a src/louieai folder with an __init__.py file containing __version__ = "0.1.0".
Other directories (tests, docs, .github/workflows, AI_PROGRESS) are created (they might be empty for now except AI_PROGRESS which we’ll populate later).
.gitignore exists with appropriate patterns.
LICENSE file exists and contains the full Apache 2.0 text.
git status should show a clean working directory (meaning everything is committed). Running git log should show the initial commit with the expected message.
Result:
[Fill this in with commands, output, decisions, errors, etc.]
Step 1.1.0: Add pyproject.toml with PEP 621 metadata
Status: ⏳ PENDING
Started: [timestamp]
Action: Now, create the packaging configuration using pyproject.toml. Claude should:
Open a new file pyproject.toml at the repository root. Populate it with the project metadata and build system config. We will use setuptools as the build backend and specify project details according to PEP 621.
Use the following content for pyproject.toml (make sure to carefully align indentation and TOML syntax):
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "louieai"
version = "0.1.0"
description = "Python client for Louie.ai (Graphistry's AI investigation platform)"
authors = [
  { name = "Graphistry, Inc.", email = "support@graphistry.com" }
]
readme = "README.md"
license = { text = "Apache-2.0" }
requires-python = ">=3.8"
classifiers = [
  "Development Status :: 3 - Alpha",
  "Intended Audience :: Developers",
  "License :: OSI Approved :: Apache Software License",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.8",
  "Programming Language :: Python :: 3.9",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Topic :: Software Development :: Libraries :: Python Modules",
  "Topic :: Scientific/Engineering :: Information Analysis"
]
keywords = ["Louie.ai", "Graphistry", "AI", "client", "investigation"]
dependencies = [
  "graphistry>=0.34",
  "httpx>=0.28",
  "pandas>=1.0",
  "pyarrow>=8.0"
]
# Note: graphistry on PyPI is named 'graphistry'. We ensure a minimal version that likely includes Louie support.

[project.optional-dependencies]
dev = [
  "ruff==0.12.0",
  "mypy==1.5.0",
  "pytest==7.4.0",
  "black==25.1.0",
  "mkdocs==1.4.3",
  "mkdocs-material==8.5.10",
  "types-requests"  # (if needed for httpx, but httpx is typed; this could be omitted)
]
docs = [
  "mkdocs==1.4.3",
  "mkdocs-material==8.5.10"
]
# We define a separate "docs" extra in case readthedocs needs to install just docs requirements.

[tool.setuptools.packages.find]
where = ["src"]
include = ["louieai*"]
Important details:
In [build-system]: ensure setuptools and wheel are listed so that pip knows how to build the project.
In [project]:
name is louieai (this will be the package name on PyPI).
version should match the __version__ we set. We used "0.1.0".
license here is given as "Apache-2.0" which should be acceptable since PEP 621 allows SPDX expressions or a license text. (We might adjust to use license = { file = "LICENSE" } in the future if PEP 639 is considered, but our approach is fine for now.)
dependencies list includes exactly the 4 production dependencies requested, with relaxed lower bounds. We chose:
graphistry>=0.34 (PyGraphistry latest series),
httpx>=0.28 (latest stable HTTPX),
pandas>=1.0 (works for all 1.x and 2.x presumably),
pyarrow>=8.0 (to cover current versions).
We did not pin upper bounds to keep them relaxed (these libs follow semver decently; if breaking changes occur, we'll address then).
The requires-python is ">=3.8" to reflect compatibility (Graphistry likely needs 3.8+, and 3.7 is probably EOL).
Classifiers cover license, supported Python versions, and an "Alpha" development status since this is initial.
In [project.optional-dependencies]:
We define dev extra to include all tools needed for development (linter, type checker, test runner, formatter, docs generator). These are pinned to specific versions to ensure consistency in dev and CI.
Using ruff==0.12.0 (placeholder for latest Ruff in 2025),
mypy==1.5.0,
pytest==7.4.0,
black==25.1.0 (Black's version scheme is year-based, this corresponds to a 2025 release),
mkdocs and mkdocs-material for docs.
types-requests is included as a precaution if httpx or other libs might need stub packages (httpx uses httpcore and possibly requests' types in some places; we can remove it if unnecessary).
We also define a docs extra that duplicates the docs-related packages. This is optional, but sometimes readthedocs can be configured to install .[docs] to get requirements needed to build docs without pulling in all dev tools.
In [tool.setuptools.packages.find]:
We inform setuptools that our packages are under src. This will cause it to include src/louieai as the package.
include = ["louieai*"] ensures it picks up louieai (and any sub-packages if any in future).
We are not listing packages explicitly under [project] so setuptools' discovery is needed (hence this config).
Save pyproject.toml. Then verify the syntax: use toml highlighting or a quick command like python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))" to ensure no syntax errors (if available in Python 3.11+ since tomllib exists).
Stage and commit this file: git add pyproject.toml and commit with message "feat: add pyproject.toml for packaging (PEP 621)". This marks the addition of our build configuration.
Success Criteria:
The pyproject.toml file is present with all fields correctly set.
Running pip inspect pyproject.toml or similar (or even trying pip install . in a dry run) should succeed indicating the project metadata is valid.
The commit for pyproject is created. git log shows the new commit.
No obvious errors in the pyproject content (we will further test by installing in the next step).
Result:
[Fill this in with commands, output, decisions, errors, etc.]
Step 1.2.0: Install package and dev dependencies for validation
Status: ⏳ PENDING
Started: [timestamp]
Action: Now that pyproject.toml is in place, we should test that the project is installable and the dev tools run. Claude should:
Install in editable mode: Run pip install -e ".[dev]". This uses the editable/development install (-e) so that any changes in code are immediately reflected, and it also installs the [dev] extra, bringing in ruff, mypy, pytest, etc.
Watch the output for any errors in setup. It should install our four prod dependencies and all dev packages. Verify that no errors occurred (if there is an error, examine it: e.g., a typo in pyproject.toml).
If the environment is fresh, pip might first build our package. It will use setuptools to find the louieai package. Since we created src/louieai/__init__.py and configured setuptools to find packages in src, it should build correctly. If for some reason it says "package not found", we need to revisit the tool.setuptools.packages.find config.
Verify installation: After install, open a Python REPL (python -c "import louieai; print(louieai.__version__)" or similar) to ensure:
The package can be imported.
louieai.__version__ returns "0.1.0". This confirms our __init__.py and packaging version are aligned.
Also, check that the graphistry, httpx, etc., are installed (just to ensure dependencies were recognized, though this is secondary).
Run dev tools: Now that dev requirements are installed, run a quick sanity check of lint and type check on the minimal project:
ruff . – This will lint the entire repo. At this moment, we have almost no code except __init__.py. Ruff might still flag something like missing newline at EOF or similar trivial issues. If any lint issues appear, note them. For example, if it complains about unused imports (we have none yet) or missing license headers (ruff can enforce that; but we don't have one in init, might not matter).
mypy src/louieai – Type check the package. Currently, only __init__.py with a version (type of version is str, that’s fine). There should be no type errors.
If any issues come up (like ruff complaining about not having a newline or .gitignore patterns?), fix them:
For instance, ensure __init__.py ends with a newline (open it, add newline if needed).
If ruff warns about something like missing docstring or license header in init, we might configure ruff to ignore that or add a comment. But likely it's fine.
Adjust and commit: If changes were needed (like adding a newline), make them and stage the change. Otherwise, all is well.
Commit environment setup: We may not need a separate commit if nothing changed except environment. But we should record that we tested installation. We can proceed directly to next step. If a fix was made (like adding a newline), commit it as a fix (e.g., "chore: adjust files to pass lint checks").
Success Criteria:
pip install -e .[dev] completes successfully, meaning our pyproject.toml is functional.
The package is importable and reports the correct version.
No lint or type errors on the minimal code.
The development environment now has all tools for subsequent steps (ruff, mypy, pytest, etc.), ready to use.
All changes are committed and git status is clean.
Result:
[Fill this in with commands, output, decisions, errors, etc.]
Step 1.3.0: Implement LouieClient stub (code) and ensure typing
Status: ⏳ PENDING
Started: [timestamp]
Action: We will add the initial code for the Louie.ai client. Claude should:
Create louieai/client.py: In the package directory src/louieai/, create a new module file client.py. This will contain the LouieClient class. Write a minimal implementation with proper type hints:
import httpx
import graphistry
from typing import Optional, Any

class LouieClient:
    """
    A client for interacting with the Louie.ai service.
    Uses Graphistry's authentication token for authorization.
    """
    def __init__(self, server_url: str = "https://den.louie.ai"):
        """
        Initialize the LouieClient.
        
        :param server_url: Base URL for the Louie.ai service (default is the production Louie endpoint).
        """
        self.server_url = server_url
        # Ensure Graphistry is registered (i.e., an API token is available) 
        # We don't fetch the token here to avoid doing it at import; will do when needed.

    def ask(self, prompt: str) -> Any:
        """
        Send a prompt to Louie.ai and get a response.
        
        :param prompt: The prompt or query to send to the Louie.ai service.
        :return: The response from Louie.ai (parsed from JSON), or raises an exception on error.
        """
        # Get the current Graphistry API token for auth
        token: Optional[str] = graphistry.api_token()
        if token is None:
            raise RuntimeError("No Graphistry API token found. Please call graphistry.register() to authenticate.")
        # Prepare the request
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{self.server_url}/api/ask"  # Assuming an endpoint; this may change when actual API is known
        try:
            response = httpx.post(url, json={"prompt": prompt}, headers=headers, timeout=30.0)
            response.raise_for_status()
        except httpx.HTTPError as e:
            # For now, raise an error if request fails
            raise RuntimeError(f"Request to Louie.ai failed: {e}") from e
        # Assuming the API returns JSON
        return response.json()
Key points in this stub:
We import httpx and graphistry. Ensure graphistry is spelled correctly (the PyPI name is graphistry, the import is likely graphistry as well).
LouieClient.__init__ stores the server_url (default to den.louie.ai). We don't attempt any network calls in init.
The ask method:
Retrieves the token via graphistry.api_token(). If None, we throw a clear error asking user to log in.
We then form a request to self.server_url + "/api/ask" (we are guessing this endpoint; if we find docs later, we might update it. This is a placeholder that likely aligns with the idea of asking a question).
Use httpx.post to send the prompt. We set a timeout and immediately call response.raise_for_status(). If there's an HTTP error (status 4xx/5xx or network issue), we catch httpx.HTTPError and raise a RuntimeError with message.
On success, return response.json(). We don't structure it further, leaving it as raw data for now.
All functions are annotated: prompt: str -> Any (we don't know what the response looks like yet; could refine later).
We might in future extend with other methods or allow streaming, etc., but not now.
Note: We should consider that graphistry.api_token() may require Graphistry to be registered with an api=3. But since user has to do that anyway, it's okay.
Also, consider if graphistry isn't imported by user before using our library. The import at top will bring it in as dependency (we have it installed via dependency). If user didn't call register, the error message covers it.
Update __init__.py: To make it easy to access LouieClient, we can import it in the package’s __init__.py. Add the following at the bottom of src/louieai/__init__.py:
from .client import LouieClient

__all__ = ["LouieClient", "__version__"]
This way from louieai import LouieClient is possible. Also define __all__ to explicitly export the client and version.
Add basic usage example (optional): Not in code, but we will document usage in README later. In code we already have docstrings.
Run lint and type-check: After writing the code, run:
ruff src/louieai – to catch any style issues (like maybe line too long in docstring, or unused variable if any).
mypy src/louieai – to catch type issues. Potential things:
graphistry.api_token() – mypy might not know its type. If PyGraphistry has type stubs, great. If not, it might treat as Any. If it's Any, no complaint. If it errors "Module graphistry has no attribute api_token" (if stubs outdated), we might need to add a type ignore or import from a submodule. But Graphistry docs show graphistry.api_token() exists. We can do: token: Optional[str] = graphistry.api_token() which is fine if api_token returns str or None.
httpx.post returns Response which has json() method returning Any – that's fine.
ensure we import typing Optional and Any correctly.
If ruff complains about anything (say docstring style or f-string usage), fix accordingly:
Possibly f"... {token}" could trigger a warning if token can be None, but we guard that.
Might warn if we didn't use Optional properly. It's okay.
If line length issues, break lines (like the error message or the URL string).
If mypy complains about missing type hints on ask return, we left it Any intentionally, could suppress with -> Any which we did.
Or it might warn about ignoring exception type e is too broad. Actually we catch httpx.HTTPError, that's fine.
If any issues, adjust.
Run tests (though none yet): We have no tests for this step yet (we will add in next step). But ensure pytest runs with zero tests rather than error:
Running pytest now should simply report "collected 0 tests" if we haven’t written any. That's okay (exit 5 perhaps because no tests? Actually pytest exit code 5 for no tests can fail CI by default, so perhaps we should write at least one dummy test now to avoid that scenario).
It's wise to proceed to writing at least a minimal test in the next step to avoid empty test suite.
Stage and commit: Add the louieai/client.py and the modified __init__.py to git, and commit with message "feat: add LouieClient stub implementation".
Success Criteria:
The file src/louieai/client.py exists with the LouieClient class as above.
src/louieai/__init__.py now exposes LouieClient.
ruff and mypy show no issues on the code (maybe except a possible warning about httpx usage if any, but likely fine).
Build/Install still works: run pip install -e . again (should be quick since already installed, but ensures no packaging issues with new files).
The commit is recorded.
We have the foundation of functionality that can later be expanded but currently returns data from the (hypothetical) API.
Result:
[Fill this in with commands, output, decisions, errors, etc.]
Step 1.4.0: Add a basic test for LouieClient
Status: ⏳ PENDING
Started: [timestamp]
Action: We write a minimal test to ensure the package and LouieClient work as expected in stub form. Claude should:
Create a test module: Open a new file tests/test_louie_client.py.
Write test content: Add a basic test function. We won’t call the real API (to avoid external dependency), but we can test some logic:
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
In test_client_uses_graphistry_token: we monkeypatch graphistry.api_token to always return "fake-token". Then monkeypatch httpx.post to a lambda that returns DummyResponse with {"result": "ok"}. That means when client.ask() calls httpx.post, it gets our dummy response. We then check that result equals the dummy data. (We assume if headers were wrong, maybe not relevant as DummyResponse doesn’t care. This just tests flow.)
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
Running pytest yields “2 passed” (or similar) with no failures.
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
pip install louieai
(Note: The package may not be on PyPI yet if you're reading early.)
Usage Example
import graphistry
from louieai import LouieClient

# First, authenticate with Graphistry (replace with your credentials or key)
graphistry.register(api=3, username="your_user", password="your_pass")

client = LouieClient()
response = client.ask("What insights can you find about X dataset?")
print(response)
This will send the prompt to LouieAI and return a response (e.g., an answer or a visualization link). See the Architecture page for more details on how LouieAI and Graphistry integrate.
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
For ReadTheDocs to install our dependencies, one method is to use a docs/requirements.txt. Alternatively, since we have extras, we could instruct RTD to use pip install .[docs]. But easiest is to create docs/requirements.txt listing our needed packages:
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
pip install louieai
(Until published, you can install from source via pip or uv:)
pip install git+https://github.com/<owner>/louieai.git
Quick Start
import graphistry
from louieai import LouieClient

# Authenticate to Graphistry (replace with your credentials or API token)
graphistry.register(api=3, username="your_user", password="your_pass")

client = LouieClient()
result = client.ask("Summarize the latest alerts in Splunk and graph the entities.")
print(result)
This will send your prompt to the LouieAI service. The result might be a JSON containing an answer or instructions (for example, a link to a Graphistry visualization). See the documentation for more details and examples.
Links
Louie.ai Homepage – Learn about the LouieAI platform.
PyGraphistry Documentation – Learn how to set up Graphistry, which is required for LouieAI.
Project Documentation – Full documentation on ReadTheDocs.
Contributing
Contributions are welcome! Please see CONTRIBUTING.md for guidelines. We have a structured AI-involved development workflow – check out the AI planning template in AI_PROGRESS/ if you're interested in how we use AI to assist development. This project adheres to a Code of Conduct. By participating, you are expected to uphold this code.
License
Licensed under the Apache 2.0 License. See LICENSE for details.
Replace `<owner>` with the actual GitHub owner/org when known. If unknown, we leave a placeholder or put something like `graphistry` if likely hosted there.
- The example usage and installation refer to pip, and note the dev status.
- We link to docs and mention Graphistry and Louie.
Create CONTRIBUTING.md: Outline how to contribute:
# Contributing to LouieAI Python Library

Thank you for your interest in contributing! We welcome contributions via pull requests.

## Development Setup

- **Prerequisites**: Python 3.8+ and pip. You'll also need an account on Graphistry's platform to test against LouieAI.
- **Fork & Clone** this repository.
- **Install in dev mode**: `pip install -e ".[dev]"` to get all dependencies and tools.
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

## Contributor License Agreement

All contributions are assumed to be licensed under the same Apache 2.0 license that covers this project.

-- Happy coding! --
We mention the AI planning template and how we use it, aligning with the user's request to include "starter prompt AI planning files".
We outline typical steps.
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
        run: pip install -e ".[dev]"
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
We do not run packaging build here explicitly, but pip install -e implicitly builds. We might add a step to attempt pip wheel . or python -m build to ensure packaging is OK. Could do:
    - name: Build Package
      run: python -m build --wheel .
but requires adding pip install build before, unless we already have it via setuptools? Maybe skip for now. The packaging is simple enough.
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
        run: pip install build twine
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
This will fail if PYPI_API_TOKEN is not set. We must instruct maintainers to add it (in Graphistry’s GitHub secrets).
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
Ensure no TODOs or placeholders left that should be replaced. Possibly update README’s <owner> if we know who will own the repo (if Graphistry, maybe use graphistry).
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
Step 2.0.0: Phase 2 – Research Louie.ai API for functionality expansion
Status: ⏳ PENDING
Started: [timestamp]
Action: Before coding Phase 2, gather any available info on Louie.ai’s API to guide implementation. Claude should:
Search official docs or repositories: Look for documentation on Louie.ai's API endpoints and usage. For example:
Check if Louie.ai has developer docs or an API reference. Use keywords like "Louie.ai API" or search Graphistry’s docs for references to Louie’s API beyond marketing pages.
Possibly search in the graphistry/louie.ai-docs repository or any code that might hint at endpoints (maybe not publicly available beyond what we did).
Examine PyGraphistry for clues: The Graphistry ecosystem doc we saw shows Louie is integrated but doesn’t give technical details. We might search the PyGraphistry code for any use of "louie" or "den.louie.ai".
If PyGraphistry’s Python library has any reference to Louie (maybe in an ai module), that could inform how to call it. For instance, sometimes new features might be behind flags or separate modules.
Search in PyPI or Graphistry releases for "Louie".
Gather likely patterns: If direct info is lacking, infer from common patterns:
Perhaps the Louie API might have endpoints like:
/api/ask or /api/prompt for sending a prompt.
Possibly endpoints for retrieving results or starting sessions, etc.
It might return a JSON with fields like answer, or references to Graphistry visualizations or other data.
Graphistry’s mention: “Use Louie.AI's API to integrate genAI experiences” implies a straightforward REST call with input and output.
Also consider authentication: since we have token, we assumed Bearer token in header is correct. Graphistry’s API likely expects a JWT in Authorization header.
Graphistry Hub (hub.graphistry.com) uses token in Authorization or cookie. JWT from api_token() likely is what’s needed.
So our approach in stub is likely correct.
Plan functionality: Based on limited info, decide what to implement:
We will stick with our ask(prompt) method as primary. Possibly add an optional parameter for context or for specifying which "agent" to use (Louie can connect to databases, etc., maybe not needed in client, maybe out-of-scope).
Maybe implement a way to handle different response types: If Louie returns a graph or chart reference, how to surface that? Possibly out-of-scope for now; we might just return raw JSON and let user deal with it.
Ensure error handling robust: If a 400 error with message, maybe catch and include that in exception. Already doing raise_for_status which will raise HTTPError with status, but could parse JSON error message if present. Could consider doing:
try:
    resp.raise_for_status()
except httpx.HTTPStatusError as e:
    # e.response.json() might give error details if any, include those
    msg = f"LouieAI API error {resp.status_code}: {resp.text}"
    raise RuntimeError(msg) from e
But that might be too detailed. We'll keep it simpler unless needed.
Could also implement an async version using httpx.AsyncClient. But that may be beyond Phase 2 scope (could be Phase 3 or later).
Possibly define a method to set a custom token or to use Graphistry personal API key if not using graphistry.register (some might want to provide token directly). But since Graphistry likely always uses register, skip for now.
Update plan: Note any findings:
If no new info found, proceed with assumptions we have.
Conclude that our stub approach was okay and we'll mainly finalize any placeholders (like confirm endpoint path if possible, else use /api/ask).
If any better naming or additional parameters gleaned (for instance, maybe an endpoint needs a conversation/session ID or knowledge base selection?), we might skip those due to lack of info.
No code changes in this step, it's just information gathering. Move to implementing features next.
Success Criteria:
We have confirmed or at least not contradicted our approach. If no official info, our plan stands as is.
Document any assumptions in Key Decisions or code comments if needed (like “# TODO: confirm correct Louie endpoint and response format when official docs are available”).
Result:
[Fill this in with commands, output, decisions, errors, etc.]
Step 2.1.0: Implement enhanced LouieClient functionality
Status: ⏳ PENDING
Started: [timestamp]
Action: Now extend the LouieClient based on Phase 2 goals. Claude should:
Improve error handling: Modify LouieClient.ask in src/louieai/client.py:
Use httpx.HTTPStatusError specifically in except to differentiate status errors from network errors.
If status error, include response content in the exception message for debugging.
Example:
        try:
            response = httpx.post(url, json={"prompt": prompt}, headers=headers, timeout=30.0)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            # Include response text or json in error
            error_text = ""
            try:
                error_text = response.json().get("error", "")
            except Exception:
                error_text = response.text
            raise RuntimeError(f"LouieAI API returned error {response.status_code}: {error_text}") from e
        except httpx.RequestError as e:
            # Network or other request issue
            raise RuntimeError(f"Failed to connect to LouieAI: {e}") from e
This way, if e.g. a 400 happens with error details in JSON (maybe {"error": "..."}), we show it.
httpx.RequestError is base for network errors (like DNS fail, etc.), handle that separately.
Note: We need to import httpx.HTTPStatusError and httpx.RequestError.
After catching, we still return response.json() on success.
Optional: Additional methods: Consider adding a method def set_server_url(self, url: str) or a property to allow changing endpoint, or including an optional api_path param in ask if needed. This might not be necessary.
Another idea: maybe a async_ask if we want asynchronous support using httpx.AsyncClient. But that requires making an async method and perhaps duplicating code.
Possibly skip async in this phase to keep it simple, as it's not explicitly requested.
Ensure idempotence: Using a single httpx call per ask, nothing to change there.
If we had to allow reusing an httpx.Client for performance, we might add self._client = httpx.Client() in init and use that. But that's an optimization not demanded yet. Could consider it if multiple queries needed to reuse connection.
We can leave it stateless for simplicity (each ask creates a new connection via httpx.post which internally may use a pool anyway).
Add docstring example: Maybe update the class or method docstring to include a usage snippet for clarity.
For example, in class docstring, add a short how-to with Graphistry register. But README covers it, might skip.
Update tests for new behavior: Our tests might need tweaking:
Now we catch httpx.HTTPStatusError and turn it into RuntimeError with message containing response. Our test_client_no_token still passes (we raise before making request).
We might add a test for HTTP error handling:
e.g., monkeypatch httpx.post to return DummyResponse with status 400, and ensure RuntimeError is raised with correct message.
But our DummyResponse currently raises Exception, not specifically HTTPStatusError. Actually, in our code now, we specifically catch HTTPStatusError which is thrown by response.raise_for_status().
Our DummyResponse doesn't raise HTTPStatusError, it raises a generic Exception. That means in our code above, an Exception not subclassing HTTPStatusError would not be caught by that except, but by the generic RequestError except? Actually, our except covers only HTTPStatusError and RequestError, not a generic Exception. So in test, our DummyResponse raising Exception will not be caught by HTTPStatusError or RequestError, so it will propagate as generic Exception, failing the test unexpectedly.
To properly test, we can simulate httpx.HTTPStatusError specifically. We might need to import that class and raise an instance. But it's a bit complex to create. Alternatively, monkeypatch response.raise_for_status to raise HTTPStatusError.
Possibly easier: monkeypatch httpx.post to a function that raises httpx.RequestError("...") to simulate network error, and ensure we catch it.
Or adjust DummyResponse to raise an HTTPStatusError. But constructing that might require a request and response object to attach.
Simpler approach: change DummyResponse.raise_for_status to raise httpx.HTTPStatusError("error", request=None, response=self) to simulate. If we import httpx in test, we can do raise httpx.HTTPStatusError(f"{self.status_code} Error", request=None, response=self).
Yes, do that:
def raise_for_status(self):
    if self.status_code >= 400:
        import httpx
        raise httpx.HTTPStatusError(f"Error: status {self.status_code}", request=None, response=self)
This will allow our production code to catch it as HTTPStatusError.
Then a test can monkeypatch httpx.post to return DummyResponse(status_code=500).
And expect RuntimeError with our custom message "LouieAI API returned error 500: ..." containing error text.
Implement new test:
def test_http_error_handling(monkeypatch):
    import httpx
    # Monkeypatch httpx.post to simulate a 500 response with error message
    dummy = DummyResponse(status_code=500, data={"error": "Internal Server Error"})
    monkeypatch.setattr(httpx, "post", lambda url, json, headers, timeout: dummy)
    monkeypatch.setattr(graphistry, "api_token", lambda: "token")
    client = louieai.LouieClient()
    with pytest.raises(RuntimeError) as exc:
        client.ask("test")
    # The error message should contain status code and "Internal Server Error"
    err = str(exc.value)
    assert "500" in err and "Internal Server Error" in err
This will run through our code: graphistry token is present, httpx.post returns DummyResponse with status 500 and error in JSON. raise_for_status will raise HTTPStatusError with DummyResponse attached, caught, then we parse dummy._data and get "Internal Server Error" message, raise RuntimeError.
We check that string.
Run tests: Execute pytest to ensure all tests pass after changes.
Possibly our earlier tests might need small tweaks to how DummyResponse is defined to ensure HTTPStatusError is used as above.
Confirm everything green.
Commit changes: Stage client.py and updated tests. Commit as "feat: improve LouieClient error handling" (and possibly "test: ..." combined if done together or separate commits for code and test).
Success Criteria:
LouieClient now robustly handles HTTP and network errors with informative messages.
All tests, including new ones, pass (so our improved DummyResponse works and our code catches properly).
The changes adhere to requirements: still only using allowed libs, and maintain type hints (HTTPStatusError etc is fine).
Code coverage presumably improved by covering error branch.
Result:
[Fill this in with commands, output, decisions, errors, etc.]
Step 2.2.0: Expand documentation (usage & architecture)
Status: ⏳ PENDING
Started: [timestamp]
Action: Improve the documentation content now that functionality is fleshed out. Claude should:
README updates: If any new info or best practices emerged (not much new, but we can:
Emphasize that multiple types of outcomes can come from Louie (maybe mention if prompt triggers a graph, Louie might return a URL to Graphistry visualization, etc.).
If we have any known limitations or next steps, note them (maybe in an "About" or "Roadmap" section).
Possibly add a badge or note about documentation link explicitly (we have link in usage).
Check if the placeholder <owner> can now be replaced if known (assuming by Phase 2 we know where the repo lives. If Graphistry, put "graphistry", if user personal, put that).
If not known, leave it.
Minor corrections if any issues (like ensure code fences closed properly, etc.).
Add any example output snippet if available? Hard without real calls.
We'll primarily verify consistency.
Docs index.md: Expand maybe the usage example with expected output or a more narrative:
Possibly add a section like "How it works" or "Next Steps" referencing architecture page or Graphistry docs.
We already have usage and example in README which mirrored in docs.
Could add one more example of handling a result:
e.g., if Louie returns a chart link, how to handle it (just speculation).
But without official info, maybe skip specifics.
Ensure index and architecture pages reflect the improved error handling:
Possibly mention that the client will raise exceptions if something goes wrong, which should be caught by the application.
Architecture.md: Expand it with details:
Now we know exactly how we implemented, describe:
That LouieClient.ask issues an HTTP POST to {server}/api/ask sending the prompt and uses Graphistry’s JWT for auth.
Outline what kind of responses might be returned: e.g., text answers, JSON with data, links to Graphistry viz (given Louie is about visualizing, likely it could respond with a graph ID or link).
Clarify what the client does not do: it doesn’t store state, doesn't manage conversation context (Louie might handle context server-side, but our client is stateless).
Note thread safety: since we use no global state except Graphistry’s global token, which is fine, the client is lightweight. Instances can be created as needed.
Indicate potential future improvements (which we actually plan in Phase 3 or beyond): async support, richer result handling, etc.
For example:
## Under the Hood

When you call `LouieClient.ask(prompt)`, the library:
1. Fetches your Graphistry authentication token (JWT) via `graphistry.api_token()`.
2. Makes an HTTP POST request to Louie.ai’s REST API (default `https://den.louie.ai/api/ask`) with your prompt.
3. Includes the auth token in the request headers (`Authorization: Bearer <token>`).
4. On success, returns the response parsed from JSON. This could be a direct answer (text or data) or instructions/results (e.g., a link to a Graphistry visualization or a summarized dataset).
5. On failure (HTTP error or no token), it raises a `RuntimeError` with details.

The client itself does not maintain any session state. Each call is independent (Louie.ai may maintain context on the server side).

## Future Enhancements

- **Streaming Responses**: For large responses or conversational use, streaming output (and an async API) might be added.
- **Result Handling**: In the future, the client could parse known response formats (like recognizing if a response contains a Graphistry visualization link) and provide helper methods.
- **Additional API Endpoints**: As Louie.ai grows (dashboards, agent management, etc.), this library will add corresponding methods.
Changelog or version note: We haven’t created a CHANGELOG.md, but we might start documenting changes:
Possibly create a minimal CHANGELOG.md summarizing v0.1.0 changes. But not requested.
Could hold off until a first release is imminent, which might be at end of Phase 3. So skip for now.
Security.md: Already has content, but since we have a security policy, maybe ensure the contact info is correct.
Possibly update supported versions to mention that at v0.1 we support all features, etc.
Fine as is.
Contributing.md: Check if any updates:
We said we plan pre-commit (phase 3). If by now we didn't implement it yet, it's okay because it's said "to be set up in later phase".
We might mention running tests with multiple Python versions is done in CI but locally it's good to test with at least one.
Otherwise fine.
Stage and commit: After editing docs, commit changes e.g., "docs: update usage and architecture documentation".
Success Criteria:
Documentation is updated to reflect the state of the code and provide clearer guidance.
No broken links or formatting issues in docs.
The commit for doc changes is made.
Optionally, build docs locally to confirm (if significant changes).
The documentation now would be user-friendly for an initial release.
Result:
[Fill this in with commands, output, decisions, errors, etc.]
Step 2.3.0: Dev experience improvements (pre-commit hooks, Black formatting)
Status: ⏳ PENDING
Started: [timestamp]
Action: In Phase 2 we can introduce some dev tooling improvements, though major polish we left for Phase 3. But let's add pre-commit and code formatter now to not delay. Claude should:
Add Black to dev: We already included Black in dev dependencies in pyproject (at Phase 1 optional deps). We should integrate it:
Run black . locally to format the codebase. (Our code is small, but let's ensure consistent style, like double quotes etc. Since we possibly wrote with double quotes already, minimal changes expected.)
If Black reformats anything, ensure tests still pass (they should).
If changed, stage those changes (they would be trivial spacing or quotes).
Configure ruff to avoid conflicts with Black: In pyproject.toml, we might add:
[tool.ruff]
extend-ignore = ["E501"]  # Black handles line length
Because ruff might complain about line length which we let Black handle, and Black will break lines appropriately. Actually Black aims for 88 char by default. If we prefer, we could set Black line-length to 88 and ruff to ignore E501 or to 88 as well.
We can do this or rely on default. If our lines aren't too long (some might exceed 88 slightly?), better set it explicitly to avoid any CI issue.
Could add in pyproject:
[tool.black]
line-length = 88
or let default.
Probably fine without specifying, but adding doesn't hurt.
We'll also ensure ruff config if needed:
We can either do ruff.toml or in pyproject under [tool.ruff]. Let's do pyproject to keep things consolidated.
Example minimal:
[tool.ruff]
line-length = 88
ruff default is 88 too, so fine. If we had to ignore some rules, we add.
Actually, adding ruff config might require adding toml to dev if not included. But since we run via CLI, not needed.
Eh, skip heavy config, trust defaults. We'll just ensure all lint passes after Black.
Add pre-commit: Create .pre-commit-config.yaml:
repos:
  - repo: https://github.com/psf/black
    rev: 25.1.0
    hooks:
      - id: black
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.12.0
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
  - repo: https://github.com/pre-commit/pygrep-hooks
    rev: v1.0.0
    hooks:
      - id: python-check-blanket-noqa
Explanation:
This sets up Black, Ruff, Mypy hooks. Using ruff-pre-commit hook with --fix to auto-fix trivial issues.
Also includes a hook to flag misuse of # noqa (optional, could include other checks).
Now developers can run pre-commit install and then each commit triggers these checks/fixes.
We should mention this in CONTRIBUTING that one should enable pre-commit hooks.
Actually, we already alluded to it. We could update CONTRIBUTING to instruct to run pre-commit install.
Let's quickly add that:
In CONTRIBUTING.md under development setup, add:
- After installing, run `pre-commit install` to set up Git hooks for linting/formatting.
Stage that minor addition.
Test pre-commit config: Run pre-commit run --all-files to see if all hooks pass. Since we've manually run Black, ruff, mypy earlier, should be no issues. If any appear, fix them.
E.g., "python-check-blanket-noqa" might trigger if we had a # noqa without specifying rule. We likely didn't use any noqa, so fine.
Commit changes: Add .pre-commit-config.yaml and updated CONTRIBUTING.md. Commit as "chore: add pre-commit configuration for lint/format".
CI integration: Optionally, we can add a step in CI to run pre-commit on one environment (like Python 3.11) to ensure hooks pass. But since we already run ruff and mypy etc. separately, not necessary. Pre-commit would just repeat those tasks. We can skip to avoid redundancy.
If we wanted, we could have:
    - name: Run Pre-commit (Lint & Format)
      run: pre-commit run --all-files --show-diff-on-failure
But then we need to install pre-commit in CI too, which is an extra dep. And it essentially runs Black (which might reformat code and show diff if something not formatted, which is a fail). But if code is all formatted already, it's fine. It's a matter of preference.
As we have direct ruff/mypy in CI, it covers the same ground. We'll rely on devs to use pre-commit locally rather than run it in CI.
Update optional: Possibly bump requires = ["setuptools>=61.0", "wheel", "pre-commit"] in build-system, but pre-commit isn't needed to build or run, only dev. We already have it indirectly by including it in dev? Actually, we did not include pre-commit in dev extra. Should we? Usually yes, add "pre-commit" to dev dependencies so devs easily install it.
Do that: In pyproject optional dev, add "pre-commit==3.3.0" (latest version). Or just "pre-commit" unpinned, but pin for consistency.
Let's say pre-commit==3.3.0.
Then one can pip install .[dev] gets pre-commit too.
Stage pyproject change and commit perhaps combined with pre-commit config commit.
Check dev install: Now pip install -e ".[dev]" includes pre-commit. Ensure no conflicts, likely fine.
Success Criteria:
Code base is formatted per Black and ruff, no style issues left.
.pre-commit-config.yaml exists, and devs can use it.
CONTRIBUTING.md instructs to use it.
Pre-commit is in dev deps for easy installation.
All tests still pass after formatting changes.
The code changes from formatting are minimal and didn't break anything (our tests ensure that).
The commit for these changes is done.
Result:
[Fill this in with commands, output, decisions, errors, etc.]
Step 2.4.0: Finalize Phase 2 – Prepare for release
Status: ⏳ PENDING
Started: [timestamp]
Action: Conclude Phase 2 by ensuring everything is ready for an initial release (v0.1.0). Claude should:
Bump version if needed: Our version has been "0.1.0" since Phase 1. If we intended initial release to be 0.1.0 after finishing Phase 2, that's fine. If we wanted to call initial skeleton 0.0.1, we would bump now to 0.1.0. But since we started at 0.1.0, we can either keep it or bump to 0.1.1.
Usually first release might be 0.1.0. It's still that, so we can leave it.
If we decided that after adding features it's more like 0.1.0 whereas initial scaffold was 0.0.1, we would have to do bump. But let's assume 0.1.0 is our first intended release, and we set it from start anticipating this.
So no change needed in version.
If we did want to bump, we would update pyproject and version, but let's skip bump to avoid confusion, keep consistency.
Ensure changelog or release notes: If we have no CHANGELOG.md, maybe quickly create one:
It can be as simple as:
# Changelog

## [0.1.0] - 2025-07-25
- Initial release of louieai library with basic `LouieClient.ask` functionality.
But since not requested, optional. Could help users see what's included.
Let's create it for completeness:
Create CHANGELOG.md and put above content. Stage it.
Update in pyproject's [project.urls] if we want to add "Changelog": link to that file in GitHub (maybe not needed, but can).
Add project.urls in pyproject with "Documentation": "https://louieai.readthedocs.io", "Source": "https://github.com/<owner>/louieai", etc. This is nice for PyPI project page.
We omitted [project.urls] earlier. We can add now:
urls = { 
  "Documentation" = "https://louieai.readthedocs.io",
  "Source" = "https://github.com/<owner>/louieai",
  "Issue Tracker" = "https://github.com/<owner>/louieai/issues"
}
Replace <owner> accordingly.
Stage pyproject changes if adding URLs.
Test packaging: We should test that building distribution works with our final state:
Run python -m build . to produce wheel and sdist in dist/.
Inspect that louieai package is included and all necessary files (license, README) are included (we may need to ensure MANIFEST.in or project.include in pyproject for license and such).
Actually, PEP 621’s license.text might not automatically include the LICENSE file in sdist. Possibly yes if using setuptools, usually not, we might need to add:
[project] 
license-files = ["LICENSE"]
or similar. PEP 639 covers license-files (setuptools supports license_file or license_files config historically).
If we want to be safe:
We can add license-files = ["LICENSE"] to pyproject, given setuptools 77+ supports that (our config might be used by PyPI as well).
Or MANIFEST.in file with include LICENSE.
Let's quickly add a MANIFEST.in:
include LICENSE
include README.md
include CHANGELOG.md
(so these files go into sdist).
And maybe include docs? Usually not needed in sdist.
We want license and readme definitely in sdist for compliance.
Create MANIFEST.in with those includes.
Set in pyproject [tool.setuptools] include-package-data = true if we had package data, but we don't.
Add MANIFEST.in to git.
Build again, check output. Ideally, we do this in an environment with build installed. If not possible in plan environment, just assume.
If any packaging issues discovered (like it didn't include something), we adjust.
Ready secrets: Ensure that for releasing on PyPI, the PYPI_API_TOKEN must be added in GitHub secrets. In plan context, we can mention to user to add that secret.
Possibly update SECURITY.md or CONTRIBUTING to mention how maintainers release, but not needed to expose token details.
We'll assume maintainers handle it outside code.
Push Phase 2 changes:
Create branch feature/core-functionality if not already, commit all changes from steps above, push it.
Open PR to main, check CI:
With new tests and slight changes, ensure all jobs pass.
Possibly ruff might now catch that we added a new import or something.
e.g., in client, we import httpx.RequestError and HTTPStatusError but not used by name explicitly (only in except). Actually, we might need to reference them to avoid "imported but unused" if ruff considers except naming usage not as usage (should count as usage though because except httpx.HTTPStatusError uses the symbol).
If ruff complains unused, then prefix import with "_" or access a property. But likely except counts as usage.
Tests might have new imports, check those (like import httpx in test, but we use it to patch, so used).
If any minor ruff issues, fix them.
Ensure new pre-commit config doesn't cause any CI fail. We didn't integrate pre-commit in CI, so no effect.
Everything passes, then merge PR.
Tag release: After merging to main, decide to tag v0.1.0 and let CI Release workflow do its thing.
Use gh release create 0.1.0 --generate-notes or manually create a tag.
Since we might not want to actually push to real PyPI in this simulation, but in a real scenario we'd do it.
If we simulate it: push tag v0.1.0 to origin.
Check GitHub Actions: the publish workflow should trigger. It will attempt to build and upload to PyPI.
If no API token, it will fail. In a real case, ensure token is present.
For now, if we were the maintainer, we'd have added it already after Phase1 or now.
We consider that done or leave it until ready.
Success: The library is now officially released on PyPI (conceptually).
Confirm by trying pip install louieai from TestPyPI if we went that route, etc.
Now users can use it.
Mark Phase 2 complete.
Success Criteria:
All Phase 2 enhancements (functional client, docs improved, dev tools) are integrated and main branch is updated.
The project is in a state ready for initial release:
Version number set to 0.1.0 and tagged.
PyPI release workflow triggered (if credentials present).
If published (in a real scenario), one could pip install and see version 0.1.0 and use it as documented.
We have a CHANGELOG documenting the release.
All CI checks are green at release commit.
Phase 2 goals (functionality extended, documentation extended, dev polish partially done) are met.
Result:
[Fill this in with commands, output, decisions, errors, etc.]
Step 3.0.0: Phase 3 – Code quality and coverage improvements
Status: ⏳ PENDING
Started: [timestamp]
Action: Focus on developer experience and project quality tasks. Claude should:
Add coverage measurement: Integrate pytest-cov to measure coverage and optionally upload to Codecov or similar:
Add pytest-cov to dev dependencies (e.g., pytest-cov==4.1.0).
In CI, adjust test step to pytest -q --cov=louieai --cov-report=xml to produce coverage XML.
Then a new step to upload to Codecov:
Add CODECOV_TOKEN secret in GitHub (if we were to do, but open source can use Codecov without token on public repos).
Use codecov action:
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    token: ${{ secrets.CODECOV_TOKEN }}  # if required
    files: coverage.xml
    flags: unittests
    name: CI-Python
Since not explicitly requested, this is an optional improvement.
We can add it as it is a typical polish.
If no Codecov, at least produce coverage and maybe fail CI if coverage below threshold (some projects do).
Could use --cov-fail-under=80 to enforce e.g. 80% coverage.
We have a small code base, probably coverage is high (we covered error and success paths).
Good practice: set maybe 90% threshold.
That might be fine; currently our tests cover most logic except possibly one branch in error parse.
Let's assume >90% coverage already. If not, can adjust threshold or add a dummy test to cover a branch if needed.
We'll include coverage to see metric but not necessarily enforce if not needed.
Check packaging one more time: Possibly test the installed package in a fresh venv to ensure no missing files:
Eg: pip install dist/louieai-0.1.0-py3-none-any.whl then import louieai works, license included in distribution etc.
But if earlier step packaging had issues, we likely fixed via MANIFEST.in.
Confirm that in the wheel, license is often not included (wheels not required to include license file, but sdist should).
It's fine; sdist has it, that's enough for license compliance.
All good likely.
Issue templates / GitHub settings: We could add .github/ISSUE_TEMPLATE/bug_report.md and feature_request.md to encourage structured issues. Not requested but nice.
Possibly beyond scope. We skip due to time.
Refine any leftover minor tasks:
Possibly ensure our PyPI metadata is complete:
Did we mention graphistry clearly in description? It's fine.
If we want, add long_description_content_type = "text/markdown" in project config if needed. But since we gave readme as readme file, it should pick that up for PyPI long desc.
Confirm no references to "louie.ai" that should be "LouieAI" or spelling, etc.
Spell-check docs.
Clean any trailing whitespace.
Ensure year in license correct (maybe add "2025 Graphistry" at top of license file if needed).
Could do that as courtesy:
Add to LICENSE file top: "Copyright 2025 Graphistry, Inc." above the license text.
Many projects do that.
We can do that to finalize.
Stage license file change if any.
These are minor polishing.
One more run of pre-commit: It should pass. If any new things like trailing whitespace found, fix them.
Commit final changes: e.g., "chore: miscellaneous project polish (coverage, license header)".
Push Phase 3 branch:
branch e.g. feature/dev-polish, push, open PR.
CI runs: now with coverage, might produce a result:
If we set --cov-fail-under, ensure it passes threshold or adjust threshold accordingly if fails (maybe initially see what coverage is).
If coverage is 100% or near, we can set 90% confidently. If it's like 85, set threshold a bit lower or add another test to raise it (maybe not needed if we consider coverage not strictly required to pass).
It's optional to enforce. If not comfortable, skip fail-under and just upload coverage.
Codecov action might require adding codecov to dev dependencies or not (the action uses its own code).
If not working directly, we can skip it or not fail CI on it.
All other checks pass.
Merge PR.
Post-merge tasks:
We might cut a new release if changes warrant (0.1.1 perhaps, but if changes are all internal like tests, docs, maybe not necessary to release).
Possibly skip immediate new PyPI release because no functional change.
If we want to include pre-commit and coverage improvement for users/cloners, not needed on PyPI artifact, it's dev stuff.
We might wait for a next functional update to do 0.1.1 release.
So no new tag now.
Success: The project is now polished. High code quality and completeness for an open-source project.
We can declare Phase 3 done.
Success Criteria:
Pre-commit hooks ensure style; Black and ruff integrated, so contributions remain consistent.
Code coverage is measured in CI (and optionally uploaded to codecov), ensuring we keep/improve it over time.
All documentation and configuration files have been revisited and fine-tuned.
The license file has proper notice.
The repository is effectively ready for community contributions and further development with minimal technical debt.
Result:
[Fill this in with commands, output, decisions, errors, etc.]
Step 3.1.0: Wrap up and future plans
Status: ⏳ PENDING
Started: [timestamp]
Action: Conclude the planning with any notes on future developments beyond Phase 3. Claude should:
Summarize achievements: We have a fully bootstrapped repository. Recap:
Packaging: done (pip/uv installable).
CI: runs tests, lint, type-check on PRs; publish to PyPI on tag.
Docs: on readthedocs with basic content.
Code: LouieClient with core functionality.
OSS files: license, contributing, etc. are in place.
Dev tooling: pre-commit, formatting, etc. done.
Release: v0.1.0 published (assuming).
Identify any known gaps or next steps:
Possibly implement asynchronous support (if Graphistry or users need).
Possibly create more client methods if Louie gets new APIs (like listing saved prompts or connecting to specific data sources).
More robust integration tests if there's a staging Louie API environment (for example, tests that actually hit an API if credentials present, perhaps marked optional).
Community growth: maybe add examples directory or Jupyter notebook demos. Could be beyond initial scope.
Monitoring issues: ensure any bugs reported are addressed, etc.
Document these future ideas in an appropriate place:
Could put them in README as "Roadmap".
Or open GitHub issues to track.
Maybe we add a section in README:
## Roadmap
- [ ] Async support for non-blocking calls.
- [ ] Support for new LouieAI endpoints (as they become available).
- [ ] Enhanced parsing of responses (e.g., auto-launch Graphistry viz if a link is returned).
- [ ] More examples and tutorials.
We can if we want.
But might clutter README. Possibly skip adding it to published docs, but keep notes in plan or internal tracker (like GitHub Issues).
We'll mention it here for completeness, but perhaps not commit in README unless desired.
No code changes here: It's just reflective.
Plan completion: Mark all steps done (once executed). The plan file itself remains as record (maybe commit plan.md to repository's AI_PROGRESS if they do that).
But likely not commit actual plan, it was guiding development.
Possibly we add a reference to the plan in CONTRIBUTING or a wiki.
Already in CONTRIBUTING we mentioned there's an AI plan template and maybe "see AI_PROGRESS for past plans". We could consider adding our now completed plan as AI_PROGRESS/2025-07_bootstrap_plan.md or similar for record.
If that’s something maintainers want (so new contributors can see how initial work was done and learn the process).
Could be beneficial. If yes, we copy this PLAN.md into the repo in AI_PROGRESS folder with a name (like AI_PROGRESS/louieai_bootstrap_plan.md).
But the plan is extremely long (like 1000+ lines including results once filled), maybe too much to include in code repo.
Possibly skip adding executed plan to code.
The template is there for future tasks, which is enough.
Final commit: Not needed if we didn't change code in this step. If we did minor README roadmap addition, commit that as "docs: add roadmap section".
Close out: The project is ready and the plan is fully executed.
Success Criteria:
Phase 3 enhancements are merged, and the repository status is as desired.
We have identified future ideas, which ensures the project has direction beyond this initial scope.
All steps in the plan are completed or noted for follow-up (no ❌ or ⏭️ left).
The plan file is updated with results for each step (in an ideal execution scenario).
Result:
[Fill this in with commands, output, decisions, errors, etc.]
