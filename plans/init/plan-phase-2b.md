LouieAI_Bootstrap Plan - Phase 2B (Documentation & Dev Tools)
THIS PLAN FILE: AI_PROGRESS/LouieAI_Bootstrap/plan-phase-2b.md
Created: 2025-07-26 16:00:00 PST
Current Phase: 2B - Documentation & Developer Experience
Previous Phase: [Phase 2A - Core Implementation](plan-phase-2a.md)
Next Phase: [Phase 3 - Polish & Release](plan-phase-3.md)
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
RELOAD PLAN: cat AI_PROGRESS/LouieAI_Bootstrap/plan-phase-2b.md | head -200
FIND YOUR TASK: Locate the current 🔄 IN_PROGRESS step.
EXECUTE: ONLY do what that step says.
UPDATE IMMEDIATELY: Edit this plan with results BEFORE doing anything else.
VERIFY: tail -50 AI_PROGRESS/LouieAI_Bootstrap/plan-phase-2b.md
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
Phase 2B Overview
Phase 2B focuses on documentation and developer experience:
- Expand documentation (usage & architecture)
- Add developer experience improvements (pre-commit hooks, Black formatting)
- Finalize Phase 2 and prepare for release
- Ensure all documentation reflects enhanced functionality

Prerequisites from Phase 2A:
- Enhanced LouieClient with robust error handling
- Comprehensive test coverage
- Research documented on API patterns
- All code passing lint and type checks

Success Criteria for Phase 2B: 
By the end of Phase 2B, the repository should have:
- Updated documentation reflecting all functionality
- Developer tools configured (pre-commit, Black)
- Release preparation completed
- All packaging and build processes verified

Quick Reference (READ-ONLY)
# Reload plan
cat AI_PROGRESS/LouieAI_Bootstrap/plan-phase-2b.md | head -200

# Local validation
ruff . && mypy .
pytest -xsv

# CI monitoring (via GitHub CLI):
gh pr checks <PR-number> --repo <owner>/louieai --watch
gh run watch <run-id>

# Build package
python -m build .

LIVE PLAN (THE ONLY SECTION YOU UPDATE)
Context Preservation (Update ONLY if directed by a step)
<!-- Only update these sections if a step specifically says to -->
Key Decisions Made
<!-- Document WHY things were done certain ways -->
[Dev Tools Decision]: Added Black formatter and pre-commit hooks in Phase 2B to improve developer experience early.

Lessons Learned
<!-- Document what failed and why to avoid repeating -->
[Placeholder]: This section will capture any mistakes or necessary adjustments encountered during execution.

Important Commands
<!-- Document complex commands that worked -->
# Format code with Black
black .

# Run pre-commit on all files
pre-commit run --all-files

# Build distribution files
python -m build .

Steps
Step 2.2.0: Expand documentation (usage & architecture)
Status: ⏳ PENDING
Started: [timestamp]
Action: Improve the documentation content now that functionality is fleshed out. Claude should:
README updates: If any new info or best practices emerged (not much new, but we can:
Emphasize that multiple types of outcomes can come from Louie (maybe mention if prompt triggers a graph, Louie might return a URL to Graphistry visualization, etc.).
If we have any known limitations or next steps, note them (maybe in an "About" or "Roadmap" section).
IMPORTANT: Mention the TODO comment about endpoint confirmation - documentation should note that the /api/ask endpoint is based on common REST patterns and subject to confirmation when official API docs become available.
Possibly add a badge or note about documentation link explicitly (we have link in usage).
Check if the placeholder <owner> can now be replaced if known (assuming by Phase 2B we know where the repo lives. If Graphistry, put "graphistry", if user personal, put that).
If not known, leave it.
Minor corrections if any issues (like ensure code fences closed properly, etc.).
Add any example output snippet if available? Hard without real calls.
IMPORTANT: Include error handling examples in documentation showing users how to catch and handle RuntimeError exceptions.
We'll primarily verify consistency and ensure error handling is well documented.
Docs index.md: Expand maybe the usage example with expected output or a more narrative:
Possibly add a section like "How it works" or "Next Steps" referencing architecture page or Graphistry docs.
We already have usage and example in README which mirrored in docs.
Could add one more example of handling a result:
e.g., if Louie returns a chart link, how to handle it (just speculation).
But without official info, maybe skip specifics.
Ensure index and architecture pages reflect the improved error handling:
IMPORTANT: Phase 2A implemented enhanced error handling with specific HTTPStatusError and RequestError handling. Documentation must reflect:
- LouieClient.ask() now provides detailed error messages with status codes
- JSON error extraction from API responses ("error" or "message" fields)  
- Separate handling for network errors vs HTTP errors
- All errors raise RuntimeError with descriptive messages for debugging
Architecture.md: Expand it with details:
Now we know exactly how we implemented, describe:
That LouieClient.ask issues an HTTP POST to {server}/api/ask sending the prompt and uses Graphistry's JWT for auth.
Outline what kind of responses might be returned: e.g., text answers, JSON with data, links to Graphistry viz (given Louie is about visualizing, likely it could respond with a graph ID or link).
Clarify what the client does not do: it doesn't store state, doesn't manage conversation context (Louie might handle context server-side, but our client is stateless).
Note thread safety: since we use no global state except Graphistry's global token, which is fine, the client is lightweight. Instances can be created as needed.
Indicate potential future improvements (which we actually plan in Phase 3 or beyond): async support, richer result handling, etc.
For example:
## Under the Hood

When you call `LouieClient.ask(prompt)`, the library:
1. Fetches your Graphistry authentication token (JWT) via `graphistry.api_token()`.
2. Makes an HTTP POST request to Louie.ai's REST API (default `https://den.louie.ai/api/ask`) with your prompt.
3. Includes the auth token in the request headers (`Authorization: Bearer <token>`).
4. On success, returns the response parsed from JSON. This could be a direct answer (text or data) or instructions/results (e.g., a link to a Graphistry visualization or a summarized dataset).
5. On failure, raises detailed `RuntimeError` exceptions:
   - For HTTP errors (4xx/5xx): Extracts JSON error messages from API response
   - For network errors: Provides network-specific error details  
   - For missing authentication: Clear message about calling graphistry.register()

The client itself does not maintain any session state. Each call is independent (Louie.ai may maintain context on the server side).

## Future Enhancements

- **Streaming Responses**: For large responses or conversational use, streaming output (and an async API) might be added.
- **Result Handling**: In the future, the client could parse known response formats (like recognizing if a response contains a Graphistry visualization link) and provide helper methods.
- **Additional API Endpoints**: As Louie.ai grows (dashboards, agent management, etc.), this library will add corresponding methods.
Changelog or version note: We haven't created a CHANGELOG.md, but we might start documenting changes:
Possibly create a minimal CHANGELOG.md summarizing v0.1.0 changes. But not requested.
Could hold off until a first release is imminent, which might be at end of Phase 3. So skip for now.
Security.md: Already has content, but since we have a security policy, maybe ensure the contact info is correct.
Possibly update supported versions to mention that at v0.1 we support all features, etc.
Fine as is.
Contributing.md: Check if any updates:
We said we plan pre-commit (phase 2B). If by now we didn't implement it yet, it's okay because it's said "to be set up in later phase".
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
Action: In Phase 2B we can introduce some dev tooling improvements, though major polish we left for Phase 3. But let's add pre-commit and code formatter now to not delay. Claude should:
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
Then one can uv pip install .[dev] gets pre-commit too.
Stage pyproject change and commit perhaps combined with pre-commit config commit.
Check dev install: Now uv pip install -e ".[dev]" includes pre-commit. Ensure no conflicts, likely fine.
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

## [0.1.0] - 2025-07-26
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
Actually, PEP 621's license.text might not automatically include the LICENSE file in sdist. Possibly yes if using setuptools, usually not, we might need to add:
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
Confirm by trying uv pip install louieai from TestPyPI if we went that route, etc.
Now users can use it.
Mark Phase 2 complete.
Success Criteria:
All Phase 2 enhancements (functional client, docs improved, dev tools) are integrated and main branch is updated.
The project is in a state ready for initial release:
Version number set to 0.1.0 and tagged.
PyPI release workflow triggered (if credentials present).
If published (in a real scenario), one could uv pip install and see version 0.1.0 and use it as documented.
We have a CHANGELOG documenting the release.
All CI checks are green at release commit.
Phase 2 goals (functionality extended, documentation extended, dev polish partially done) are met.
Result:
[Fill this in with commands, output, decisions, errors, etc.]

Phase 2B Complete
After completing Step 2.4.0, Phase 2B is complete. The repository now has:
- Updated documentation reflecting all functionality
- Developer tools configured (pre-commit, Black)
- Release preparation completed
- All packaging and build processes verified

Phase 2 overall (both 2A and 2B combined) is now complete, and the next step would be Phase 3 - Polish & Release.

Next: Continue to [Phase 3 - Polish & Release](plan-phase-3.md) for final polish and release preparation.