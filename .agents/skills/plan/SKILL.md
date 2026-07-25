---
name: plan
description: Create and maintain an opt-in, file-based task plan for explicitly planned, multi-session, handoff, or multi-PR work. Use when durable execution state matters; prefer native planning for ordinary single-session work.
---

# Durable, Lightweight Task Plans

Create `plans/<task>/plan.md` only when the user asks for a written plan, work
will span sessions, a handoff is expected, or coordination across PRs requires
persistent state. For ordinary work, use native planning instead.

`plans/` is local working memory and remains uncommitted unless the user asks
otherwise. Never write credentials, tokens, passwords, or customer data to a
tracked path.

## Plan contract

A plan must be sufficient for a new agent to resume safely. Record the goal,
constraints, branch/PR context, decisions, active work, evidence, and next
step. Treat external state (remote branches, deployments, credentials, test
results) as stale until revalidated.

Use hierarchical step IDs:

- `1` — a phase or outcome.
- `1.1` — an independently verifiable task within that phase.
- `1.1.1` — a small action when the parent task needs decomposition.

Keep at most one `IN_PROGRESS` leaf per workstream. Do not renumber completed
IDs; add new work as the next sibling or child. A parent is `DONE` only when
all required children are `DONE` or explicitly `SKIPPED`.

Use these statuses: `TODO`, `IN_PROGRESS`, `DONE`, `FAILED`, `SKIPPED`, and
`BLOCKED`. Every `FAILED`, `SKIPPED`, or `BLOCKED` item states why and names
the next safe action or required owner.

## Update cadence

Read the plan once at session start, before a handoff, and when confused or
returning after an interruption. Update it at meaningful boundaries: a task
completion, material decision, validation result, failure, scope change,
handoff, or session end. Do **not** reread or rewrite it before and after every
command; record concise evidence rather than routine intermediate output.

When a completed task produces a fact a future task needs, add it there as:
`**from_step 1.2**: <fact> (revalidate with <command or source> )`.

## Create a plan

1. Copy the template below to `plans/<task>/plan.md`.
2. Fill the context before starting; include the raw request, scope, success
   criteria, branch/base/PR, and security constraints.
3. Create phases and tasks with hierarchical IDs. Start one leaf as
   `IN_PROGRESS`.
4. For execution/fix loops, use `ai/prompts/PLAN.OBSERVE-FIX.md` to add a
   fresh expected/actual matrix and regression check to the affected task.

## Template

```markdown
# <Task> Plan

**Plan file:** `plans/<task>/plan.md`
**Created:** <date/time/timezone>
**Branch:** `<branch>` from `<base>@<sha>`
**PRs:** <number, URL, role; or none>
**Target branch:** `<target>`

## Context (stable)

### Overview

**Raw request:** <verbatim request>
**Goal:** <outcome>
**Scope:** <included and excluded work>
**Success criteria:** <observable completion conditions>
**Constraints:** <security, compatibility, time, deployment, or ownership>

### Technical state

- Working directory: `<pwd>`
- Branch/base: `<branch>` / `<base>@<sha>`
- Relevant paths, services, and dependencies: <facts>

### Strategy and decisions

- **Approach:** <high-level route>
- **Decision:** <choice — rationale>

## Quick reference

```bash
# Reorient after a break
sed -n '1,240p' plans/<task>/plan.md
git status --short --branch

# Project validation
<focused test/lint/type commands>
```

## Live plan

### 1. <Phase / outcome>

**Status:** IN_PROGRESS

#### 1.1 <Verifiable task>

**Status:** IN_PROGRESS
**Action:** <what to do>
**Success criteria:** <how to tell it is done>
**Evidence:** <commands, links, concise observed result>
**Result:** <completed outcome, failure, or decision>
**Next:** <next ID, owner, or unblock condition>

##### 1.1.1 <Optional atomic action>

**Status:** TODO
**Action:** <small action>
**Success criteria:** <observable result>

#### 1.2 <Next task>

**Status:** TODO
**Action:** <what to do>
**Success criteria:** <how to verify>

## Progress log

### <date/time> — <boundary>

- `1.1` <status>: <concise outcome and evidence>
- Decision: <decision — reason>
- Next: `<ID>` <next work>

## Resume notes

- Revalidate: <stale external facts and how>
- Current blocker / handoff: <if any>
```

## Execution rules

- Work only on the active leaf. If discovery changes scope, add a numbered task
  before doing the new work and state why.
- Mark a task `DONE` only with evidence against its success criteria. Record
  failed validation before retrying so the next attempt has context.
- Keep decisions and durable facts in their task or the stable context; do not
  rely on chat history alone.
- For a blocked task, stop only the blocked path; continue independent tasks
  when safe. Identify the exact question, authority, or external change needed.

## Resume and compaction

On resume, read the plan, check working-tree/branch state, revalidate stale
facts, and continue the first eligible `TODO` task. Every roughly 30 completed
leaf tasks, move historical detail to `plans/<task>/history/` and retain a
dated summary, decisions, validation evidence, ID references, and unresolved
work in the live plan.
