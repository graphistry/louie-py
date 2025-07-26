LouieAI_Bootstrap Plan - Phase 2A (Core Implementation)
THIS PLAN FILE: AI_PROGRESS/LouieAI_Bootstrap/plan-phase-2a.md
Created: 2025-07-26 16:00:00 PST
Current Phase: 2A - Core Implementation & Enhanced Functionality
Previous Phase: [Phase 1B - Tests, Documentation & CI Setup](plan-phase-1b.md)
Next Phase: [Phase 2B - Documentation & Dev Tools](plan-phase-2b.md)
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
RELOAD PLAN: cat AI_PROGRESS/LouieAI_Bootstrap/plan-phase-2a.md | head -200
FIND YOUR TASK: Locate the current 🔄 IN_PROGRESS step.
EXECUTE: ONLY do what that step says.
UPDATE IMMEDIATELY: Edit this plan with results BEFORE doing anything else.
VERIFY: tail -50 AI_PROGRESS/LouieAI_Bootstrap/plan-phase-2a.md
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
Phase 2A Overview
Phase 2A focuses on implementing core functionality:
- Research Louie.ai API patterns and endpoints
- Implement enhanced LouieClient functionality with robust error handling
- Expand test suite to cover new functionality
- Ensure authentication integration works properly

Phase 2B (plan-phase-2b.md) will handle:
- Documentation expansion and improvements
- Developer experience improvements (pre-commit hooks, Black formatting)
- Release preparation and packaging

Success Criteria for Phase 2A: 
By the end of Phase 2A, the repository should have:
- LouieClient with robust error handling and proper API integration
- Comprehensive test coverage for all functionality
- Research documented on Louie.ai API patterns
- All code passing lint and type checks

Quick Reference (READ-ONLY)
# Reload plan
cat AI_PROGRESS/LouieAI_Bootstrap/plan-phase-2a.md | head -200

# Local validation
ruff . && mypy .
pytest -xsv

# CI monitoring (via GitHub CLI):
gh pr checks <PR-number> --repo <owner>/louieai --watch
gh run watch <run-id>

LIVE PLAN (THE ONLY SECTION YOU UPDATE)
Context Preservation (Update ONLY if directed by a step)
<!-- Only update these sections if a step specifically says to -->
Key Decisions Made
<!-- Document WHY things were done certain ways -->
[API Endpoint Decision]: Used /api/ask as the endpoint path based on common patterns, as no official documentation was available.
[Error Handling Decision]: Implemented comprehensive error handling that distinguishes between HTTP status errors and network errors, providing informative messages.

Lessons Learned
<!-- Document what failed and why to avoid repeating -->
[Placeholder]: This section will capture any mistakes or necessary adjustments encountered during execution.

Important Commands
<!-- Document complex commands that worked -->
# Test specific functionality
pytest tests/test_louie_client.py -v

Steps
Step 2.0.0: Phase 2A – Research Louie.ai API for functionality expansion
Status: ⏳ PENDING
Started: [timestamp]
Action: Before coding Phase 2A, gather any available info on Louie.ai's API to guide implementation. Claude should:
Search official docs or repositories: Look for documentation on Louie.ai's API endpoints and usage. For example:
Check if Louie.ai has developer docs or an API reference. Use keywords like "Louie.ai API" or search Graphistry's docs for references to Louie's API beyond marketing pages.
Possibly search in the graphistry/louie.ai-docs repository or any code that might hint at endpoints (maybe not publicly available beyond what we did).
Examine PyGraphistry for clues: The Graphistry ecosystem doc we saw shows Louie is integrated but doesn't give technical details. We might search the PyGraphistry code for any use of "louie" or "den.louie.ai".
If PyGraphistry's Python library has any reference to Louie (maybe in an ai module), that could inform how to call it. For instance, sometimes new features might be behind flags or separate modules.
Search in PyPI or Graphistry releases for "Louie".
Gather likely patterns: If direct info is lacking, infer from common patterns:
Perhaps the Louie API might have endpoints like:
/api/ask or /api/prompt for sending a prompt.
Possibly endpoints for retrieving results or starting sessions, etc.
It might return a JSON with fields like answer, or references to Graphistry visualizations or other data.
Graphistry's mention: "Use Louie.AI's API to integrate genAI experiences" implies a straightforward REST call with input and output.
Also consider authentication: since we have token, we assumed Bearer token in header is correct. Graphistry's API likely expects a JWT in Authorization header.
Graphistry Hub (hub.graphistry.com) uses token in Authorization or cookie. JWT from api_token() likely is what's needed.
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
Could also implement an async version using httpx.AsyncClient. But that may be beyond Phase 2A scope (could be Phase 2B or later).
Possibly define a method to set a custom token or to use Graphistry personal API key if not using graphistry.register (some might want to provide token directly). But since Graphistry likely always uses register, skip for now.
Update plan: Note any findings:
If no new info found, proceed with assumptions we have.
Conclude that our stub approach was okay and we'll mainly finalize any placeholders (like confirm endpoint path if possible, else use /api/ask).
If any better naming or additional parameters gleaned (for instance, maybe an endpoint needs a conversation/session ID or knowledge base selection?), we might skip those due to lack of info.
No code changes in this step, it's just information gathering. Move to implementing features next.
Success Criteria:
We have confirmed or at least not contradicted our approach. If no official info, our plan stands as is.
Document any assumptions in Key Decisions or code comments if needed (like "# TODO: confirm correct Louie endpoint and response format when official docs are available").
Result:
[Fill this in with commands, output, decisions, errors, etc.]

Step 2.1.0: Implement enhanced LouieClient functionality
Status: ⏳ PENDING
Started: [timestamp]
Action: Now extend the LouieClient based on Phase 2A goals. Claude should:
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

Phase 2A Complete
After completing Step 2.1.0, Phase 2A is complete. The repository now has:
- Research completed on Louie.ai API patterns
- Enhanced LouieClient with robust error handling
- Comprehensive test coverage for error scenarios
- All code passing strict lint and type checks

Next: Continue to [Phase 2B - Documentation & Dev Tools](plan-phase-2b.md) for documentation improvements and developer tooling.