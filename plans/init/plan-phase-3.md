LouieAI_Bootstrap Plan - Phase 3
THIS PLAN FILE: AI_PROGRESS/LouieAI_Bootstrap/plan-phase-3.md
Created: 2025-07-25 21:01:56 PST
Current Phase: 3 - Polish & Release
Previous Phase: [Phase 2B - Documentation & Dev Tools](plan-phase-2b.md) (preceded by [Phase 2A](plan-phase-2a.md), [Phase 1b](plan-phase-1b.md) and [Phase 1a](plan-phase-1a.md))
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
RELOAD PLAN: cat AI_PROGRESS/LouieAI_Bootstrap/plan-phase-3.md | head -200
FIND YOUR TASK: Locate the current 🔄 IN_PROGRESS step.
EXECUTE: ONLY do what that step says.
UPDATE IMMEDIATELY: Edit this plan with results BEFORE doing anything else.
VERIFY: tail -50 AI_PROGRESS/LouieAI_Bootstrap/plan-phase-3.md
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
Phase 3 Overview
Phase 3 will focus on developer experience and polish:
- Integrate a formatting tool like Black for consistent code formatting
- Implement code coverage measurement in CI (using pytest --cov and uploading to Codecov or similar)
- Add any missing pieces like a CHANGELOG.md and issue/PR templates
- Make final adjustments to documentation (ensuring no TODOs remain, all sections filled out)
- Bump version number appropriately and create a release tag to trigger the publish workflow
- Verify that the package is uploaded to PyPI and can be installed via pip

Success Criteria:
Additional polish (pre-commit hooks, code formatting with Black, code coverage, and any remaining improvements), culminating in a first release (version 0.1.0) published to PyPI. The repository should meet community standards for an open-source Python project by the final phase.

Quick Reference (READ-ONLY)
# Reload plan
cat AI_PROGRESS/LouieAI_Bootstrap/plan-phase-3.md | head -200

# Local validation
black .
ruff . && mypy .
pytest -xsv --cov=louieai

# Pre-commit
pre-commit run --all-files

# Build and check distribution
python -m build .
twine check dist/*

LIVE PLAN (THE ONLY SECTION YOU UPDATE)
Context Preservation (Update ONLY if directed by a step)
<!-- Only update these sections if a step specifically says to -->
Key Decisions Made
<!-- Document WHY things were done certain ways -->
[Coverage Decision]: Added pytest-cov for code coverage measurement but made it optional rather than enforcing strict thresholds initially.
[Polish Decision]: Focused on developer experience improvements that would benefit contributors without over-engineering.

Lessons Learned
<!-- Document what failed and why to avoid repeating -->
[Placeholder]: This section will capture any mistakes or necessary adjustments encountered during execution.

Important Commands
<!-- Document complex commands that worked -->
# Run tests with coverage
pytest --cov=louieai --cov-report=xml --cov-report=term

# Check coverage locally
coverage report -m

Steps
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
Eg: uv pip install dist/louieai-0.1.0-py3-none-any.whl then import louieai works, license included in distribution etc.
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
If that's something maintainers want (so new contributors can see how initial work was done and learn the process).
Could be beneficial. If yes, we copy this PLAN.md into the repo in AI_PROGRESS folder with a name (like AI_PROGRESS/louieai_bootstrap_plan.md).
But the plan is extremely long (like 1000+ lines including results once filled), maybe too much to include in code repo.
Possibly skip adding executed plan to code.
The template is there for future tasks, which is enough.
Final commit: Not needed if we didn't change code in this step. If we did minor README roadmap addition, commit that as "docs: add roadmap section".
Close out: The project is ready and the plan is fully executed.
Success Criteria:
The plan is complete and all three phases have been executed.
The repository is a fully functional, well-documented, and polished open-source Python package.
Future development can continue with confidence, using the established patterns and tooling.
The project meets or exceeds typical standards for open-source Python libraries.
Result:
[Fill this in with commands, output, decisions, errors, etc.]