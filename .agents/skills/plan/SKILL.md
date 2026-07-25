---
name: plan
description: Opt-in file-based planning for multi-session, handoff, or explicitly planned work. Prefer native planning for ordinary single-session tasks.
disable-model-invocation: true
---

# Lightweight File-Based Plans

## When to use

Create `plans/<task>/plan.md` only when the user requests a written plan, work
will span sessions, or another person/agent needs a durable handoff. Do not
create a plan merely because a task has several steps.

`plans/` is local working memory and should remain uncommitted unless the user
explicitly asks otherwise. Never put credentials in a tracked file.

## Working agreement

- Make the plan self-contained enough for a later reader to resume.
- Keep stable context near the top and a short live checklist below it.
- Update it at meaningful boundaries: after a completed milestone, an important
  decision, a failed validation, a handoff, or before ending a session.
- Do **not** reread or rewrite it before every command. Use the live task and
  current repository state for normal, short feedback loops.
- Record facts future work actually needs, including commands and validation
  results; omit routine intermediate output.

## Template

```markdown
# <Task> Plan

**Created:** <date/time/timezone>
**Branch:** `<branch>`
**PR:** <URL or none>

## Goal

<Desired outcome and constraints.>

## Context

- <Only durable facts needed to resume.>

## Decisions

- <Decision — reason.>

## Live checklist

- [ ] <Atomic, verifiable next task>
- [ ] <Next task>

## Progress log

### <date/time> — <milestone>

- Completed: <result>
- Evidence: `<command>` — <concise result>
- Next: <next task or blocker>
```

## Resume protocol

1. Read the plan once, then confirm branch and working-tree state.
2. Revalidate any fact that may have become stale (remote state, deployment,
   branch head, credentials, or test results).
3. Continue the first unchecked item, updating the plan only at the next
   meaningful boundary.

## Compaction

When the progress log becomes hard to scan, replace old entries with a short
dated summary or move them to `plans/<task>/history/`. Preserve decisions,
validation evidence, and unresolved work.
