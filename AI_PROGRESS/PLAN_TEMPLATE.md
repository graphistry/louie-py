# AI Planning Template

<!-- DELETE THIS SECTION WHEN USING THE TEMPLATE
This is the master template for AI-assisted development planning in the LouieAI project.
When starting a new AI planning session:
1. Copy this template to a new file (e.g., AI_PROGRESS/TaskName_YYYYMMDD.md)
2. Delete this meta section (everything between the HTML comments)
3. Fill in the project-specific details
4. Follow the plan execution protocol exactly
-->

## CRITICAL META-GOALS OF THIS PLAN
THIS PLAN MUST BE:
- **FULLY SELF-DESCRIBING**: All context needed to resume work is IN THIS FILE.
- **CONSTANTLY UPDATED**: Every action's results recorded IMMEDIATELY in the step.
- **THE SINGLE SOURCE OF TRUTH**: If it's not in the plan, it didn't happen.
- **SAFE TO RESUME**: Any AI can pick up work by reading ONLY this file.

REMEMBER: External memory is unreliable. This plan is your ONLY memory.

**CRITICAL: NEVER LEAVE THIS PLAN**
YOU WILL FAIL IF YOU DON'T FOLLOW THIS PLAN EXACTLY
TO DO DIFFERENT THINGS, YOU MUST FIRST UPDATE THIS PLAN FILE TO ADD STEPS THAT EXPLICITLY DEFINE THOSE CHANGES.

## Anti-Drift Protocol - READ THIS EVERY TIME
**THIS PLAN IS YOUR ONLY MEMORY. TREAT IT AS SACRED.**

### The Three Commandments:
1. **RELOAD BEFORE EVERY ACTION**: Your memory has been wiped. This plan is all you have.
2. **UPDATE AFTER EVERY ACTION**: If you don't write it down, it never happened.
3. **TRUST ONLY THE PLAN**: Not your memory, not your assumptions, ONLY what's written here.

### Critical Rules:
- **ONE TASK AT A TIME** – Never jump ahead.
- **NO ASSUMPTIONS** – The plan is the only truth. If you need new info, update the plan with new steps to investigate, document, replan, act, and validate.
- **NO OFFROADING** – If it's not in the plan, don't do it.

### Step Execution Protocol – MANDATORY FOR EVERY ACTION
**BEFORE EVERY SINGLE ACTION, NO EXCEPTIONS:**
1. **RELOAD PLAN**: `cat [PLAN_FILE_PATH] | head -200`
2. **FIND YOUR TASK**: Locate the current 🔄 IN_PROGRESS step.
3. **EXECUTE**: ONLY do what that step says.
4. **UPDATE IMMEDIATELY**: Edit this plan with results BEFORE doing anything else.
5. **VERIFY**: `tail -50 [PLAN_FILE_PATH]`

**THE ONLY SECTION YOU UPDATE IS "Steps" – EVERYTHING ELSE IS READ-ONLY**

### NEVER:
- Make decisions without reading the plan first.
- Create branches without the plan telling you to.
- Create PRs without the plan telling you to.
- Switch contexts without updating the plan.
- Do ANYTHING without the plan.

### If Confused:
1. STOP.
2. Reload this plan.
3. Find the last ✅ completed step.
4. Continue from there.

## Context (READ-ONLY)
### Project Overview
[Fill in project description, goals, and current state]

### Prerequisites
[List what must be in place before starting]

### Success Criteria
[Define what "done" looks like for this task]

### Quick Reference Commands
```bash
# Reload plan
cat [PLAN_FILE_PATH] | head -200

# Local validation
ruff . && mypy .
pytest -xsv

# Git status
git status
```

## LIVE PLAN (THE ONLY SECTION YOU UPDATE)

### Context Preservation (Update ONLY if directed by a step)
<!-- Only update these sections if a step specifically says to -->

#### Key Decisions Made
<!-- Document WHY things were done certain ways -->
[Placeholder]: This section will capture key architectural and implementation decisions.

#### Lessons Learned
<!-- Document what failed and why to avoid repeating -->
[Placeholder]: This section will capture any mistakes or necessary adjustments encountered during execution.

#### Important Commands
<!-- Document complex commands that worked -->
[Placeholder]: This section will capture useful commands discovered during execution.

### Steps
#### Step X.X.X: [Step Name]
Status: ⏳ PENDING
Started: [timestamp]
Action: [Detailed description of what needs to be done]

Success Criteria:
- [Specific, measurable criteria for completion]
- [Another criteria]

Result:
[Fill this in with commands, output, decisions, errors, etc.]

---

## Task Complete
After completing all steps, the task is complete. The deliverables should be:
- [List expected deliverables]
- [Another deliverable]

Next: [Link to next task or plan file]