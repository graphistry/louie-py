LouieAI_Bootstrap Plan - Phase 1A (Repository Setup)
THIS PLAN FILE: AI_PROGRESS/LouieAI_Bootstrap/plan-phase-1a.md
Created: 2025-07-25 21:01:56 PST
Current Phase: 1A - Initial Repository & Code Setup
Next Plan: [Phase 1B - Documentation & CI](plan-phase-1b.md)
Previous Phase: [Plan Overview](plan-overview.md)
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
RELOAD PLAN: cat AI_PROGRESS/LouieAI_Bootstrap/plan-phase-1a.md | head -200
FIND YOUR TASK: Locate the current 🔄 IN_PROGRESS step.
EXECUTE: ONLY do what that step says.
UPDATE IMMEDIATELY: Edit this plan with results BEFORE doing anything else.
VERIFY: tail -50 AI_PROGRESS/LouieAI_Bootstrap/plan-phase-1a.md
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
Phase 1A Overview
Phase 1A focuses on creating the core repository structure and initial code:
- Setting up version control and base folder structure (src/louieai, tests, docs, workflows)
- Writing pyproject.toml with proper metadata (project name, version, authors, dependencies, etc.) using PEP 621
- Creating minimal code (LouieClient class with stubbed method and just enough to be importable)
- Adding basic tests to ensure functionality

Phase 1B (plan-phase-1b.md) will handle:
- Documentation files (README, CONTRIBUTING, etc.)
- GitHub Actions workflows
- Final verification and PR creation

Success Criteria for Phase 1A: 
By the end of Phase 1A, the repository should have:
- Core directory structure created
- pyproject.toml configured with all dependencies
- LouieClient class implemented with stub methods
- Basic tests passing
- All code passing lint and type checks

Quick Reference (READ-ONLY)
# Reload plan
cat AI_PROGRESS/LouieAI_Bootstrap/plan-phase-1a.md | head -200

# Local validation (Phase 1A)
ruff . && mypy .
pytest -xsv

# To run specific tools:
ruff check --fix
mypy
pytest -xvs

LIVE PLAN (THE ONLY SECTION YOU UPDATE)
Context Preservation (Update ONLY if directed by a step)
<!-- Only update these sections if a step specifically says to -->
Key Decisions Made
<!-- Document WHY things were done certain ways -->
[Packaging Backend Decision]: Chose Setuptools (PEP 621) because it's standard and easy to configure for both pip and uv, and allows direct control over packaging specifics (like specifying src layout). This avoids introducing another tool like Poetry/Hatch which might impose stricter dependency locking by default.
[Auth Integration Decision]: Decided to rely on PyGraphistry's api_token() for authentication rather than building a separate auth mechanism. This leverages existing infrastructure and reduces complexity for the user (they only authenticate once).
[Code Quality Decision]: Enforce strict code quality with NO tolerance for:
  - Type ignore comments (# type: ignore)
  - Noqa comments (# noqa)
  - Type casts or Any workarounds
  - File-specific lint/type check exceptions
  All code must pass strict ruff and mypy checks. Dependencies without type information must be handled properly in mypy config, not with ignore comments.
[Type Export Decision]: Include py.typed marker file to ensure our type hints are available to library consumers. This enables downstream users to benefit from our strict typing when they use mypy or other type checkers.

Lessons Learned
<!-- Document what failed and why to avoid repeating -->
[Placeholder]: This section will capture any mistakes or necessary adjustments encountered during execution.

Important Commands
<!-- Document complex commands that worked -->
# Example: Used curl to fetch standard license text directly from Apache:
curl -sSL "https://www.apache.org/licenses/LICENSE-2.0.txt" -o LICENSE

# Example: Install the package in editable mode with dev extras for local testing:
uv pip install -e .[dev]

Steps
Step 1.0.0: Phase 1A – Initialize repository and structure
Status: 🔄 IN_PROGRESS
Started: [timestamp]
Action: We start Phase 1A by setting up the basic repository structure and necessary initial files. Claude should:
Initialize Git repository: If this directory is not already a git repo, run git init. If it's already initialized (perhaps via GitHub), ensure we have a clean working tree.
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
Create NOTICE file: Create a NOTICE file acknowledging third-party dependencies:
LouieAI Python Client
Copyright 2025 Graphistry, Inc.

This product includes software developed by Graphistry, Inc.
(https://www.graphistry.com/).

Third-party dependencies:
- PyGraphistry (Apache-2.0)
- httpx (BSD-3-Clause)
- pandas (BSD-3-Clause)
- pyarrow (Apache-2.0)
This NOTICE file satisfies Apache-2.0 requirements and acknowledges our dependencies.
Initial commit: Once the above files and directories are created, stage them (git add .) and commit as "chore: initial project structure and license". (We categorize as chore since it's not a feature yet, just setup.)
Success Criteria:
The repository has a src/louieai folder with an __init__.py file containing __version__ = "0.1.0".
Other directories (tests, docs, .github/workflows, AI_PROGRESS) are created (they might be empty for now except AI_PROGRESS which we'll populate later).
.gitignore exists with appropriate patterns.
LICENSE file exists and contains the full Apache 2.0 text.
NOTICE file exists acknowledging third-party dependencies.
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
IMPORTANT: Configure strict ruff and mypy rules in pyproject.toml:
  - No type: ignore comments allowed
  - No noqa comments allowed  
  - No file-specific ignores
  - Strict mypy mode with all checks enabled
  - Handle untyped dependencies properly in config, not code
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
Install in editable mode: Run uv pip install -e ".[dev]". This uses the editable/development install (-e) so that any changes in code are immediately reflected, and it also installs the [dev] extra, bringing in ruff, mypy, pytest, etc.
Watch the output for any errors in setup. It should install our four prod dependencies and all dev packages. Verify that no errors occurred (if there is an error, examine it: e.g., a typo in pyproject.toml).
If the environment is fresh, pip might first build our package. It will use setuptools to find the louieai package. Since we created src/louieai/__init__.py and configured setuptools to find packages in src, it should build correctly. If for some reason it says "package not found", we need to revisit the tool.setuptools.packages.find config.
Verify installation: After install, open a Python REPL (python -c "import louieai; print(louieai.__version__)" or similar) to ensure:
The package can be imported.
louieai.__version__ returns "0.1.0". This confirms our __init__.py and packaging version are aligned.
Also, check that the graphistry, httpx, etc., are installed (just to ensure dependencies were recognized, though this is secondary).
Run dev tools: Now that dev requirements are installed, run a quick sanity check of lint and type check on the minimal project:
ruff . – This will lint the entire repo. At this moment, we have almost no code except __init__.py. Ruff might still flag something like missing newline at EOF or similar trivial issues. If any lint issues appear, note them. For example, if it complains about unused imports (we have none yet) or missing license headers (ruff can enforce that; but we don't have one in init, might not matter).
mypy src/louieai – Type check the package. Currently, only __init__.py with a version (type of version is str, that's fine). There should be no type errors.
If any issues come up (like ruff complaining about not having a newline or .gitignore patterns?), fix them:
For instance, ensure __init__.py ends with a newline (open it, add newline if needed).
If ruff warns about something like missing docstring or license header in init, we might configure ruff to ignore that or add a comment. But likely it's fine.
Adjust and commit: If changes were needed (like adding a newline), make them and stage the change. Otherwise, all is well.
Commit environment setup: We may not need a separate commit if nothing changed except environment. But we should record that we tested installation. We can proceed directly to next step. If a fix was made (like adding a newline), commit it as a fix (e.g., "chore: adjust files to pass lint checks").
Success Criteria:
uv pip install -e .[dev] completes successfully, meaning our pyproject.toml is functional.
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
Update __init__.py: To make it easy to access LouieClient, we can import it in the package's __init__.py. Add the following at the bottom of src/louieai/__init__.py:
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
Running pytest now should simply report "collected 0 tests" if we haven't written any. That's okay (exit 5 perhaps because no tests? Actually pytest exit code 5 for no tests can fail CI by default, so perhaps we should write at least one dummy test now to avoid that scenario).
It's wise to proceed to writing at least a minimal test in the next step to avoid empty test suite.
Stage and commit: Add the louieai/client.py and the modified __init__.py to git, and commit with message "feat: add LouieClient stub implementation".
Success Criteria:
The file src/louieai/client.py exists with the LouieClient class as above.
src/louieai/__init__.py now exposes LouieClient.
ruff and mypy show no issues on the code (maybe except a possible warning about httpx usage if any, but likely fine).
Build/Install still works: run uv pip install -e . again (should be quick since already installed, but ensures no packaging issues with new files).
The commit is recorded.
We have the foundation of functionality that can later be expanded but currently returns data from the (hypothetical) API.
Result:
[Fill this in with commands, output, decisions, errors, etc.]

Phase 1A Complete
After completing Step 1.3.0, Phase 1A is complete. The repository now has:
- Basic structure and directories
- pyproject.toml with all dependencies configured
- LouieClient class with stub implementation
- Package installable and passing basic lint/type checks

Next: Continue to [Phase 1B](plan-phase-1b.md) for documentation, tests, CI workflows, and final PR creation.