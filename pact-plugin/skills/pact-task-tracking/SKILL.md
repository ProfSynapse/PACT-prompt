---
name: pact-task-tracking
description: |
  Task tracking protocol for PACT specialist agents. Auto-loaded via agent frontmatter.
  Defines how to report progress, blockers, and completion status via text-based reporting.
---

# Task Tracking Protocol

> **Architecture**: See [pact-task-hierarchy.md](../../protocols/pact-task-hierarchy.md) for the full hierarchy model.

## Important: Agents Do Not Have Task Tools

Agents do **NOT** have access to Task tools (TaskCreate, TaskUpdate, TaskGet, TaskList). All Task operations are performed by the orchestrator. Agents communicate status through structured text in their responses, and the orchestrator translates these into Task operations.

## On Start

Begin working immediately. The orchestrator tracks your task status — no status reporting is needed from you.

## Progress Reporting

Report progress naturally in your responses. The orchestrator monitors your output and updates task status accordingly.

## On Blocker

If you cannot proceed:

1. **Stop work immediately**
2. Report: `BLOCKER: {description of what is blocking you}`
3. Provide a partial HANDOFF (see format below) with whatever work you completed

Do not attempt to work around the blocker. The orchestrator will triage and resolve it.

## On Algedonic Signal

When you detect a viability threat (security, data integrity, ethics):

1. **Stop work immediately**
2. Report using this format:
   ```
   ⚠️ ALGEDONIC [HALT|ALERT]: {Category}

   Issue: {One-line description}
   Evidence: {Specific details — file, line, what you observed}
   Impact: {Why this threatens viability}
   Recommended Action: {What you suggest}
   ```
3. Provide a partial HANDOFF with whatever work you completed

See the algedonic protocol for trigger categories and severity guidance.

## On Completion — HANDOFF (Required)

End every response with a structured HANDOFF. This is mandatory — the orchestrator uses it to coordinate subsequent work.

```
HANDOFF:
1. Produced: Files created/modified
2. Key decisions: Decisions with rationale, assumptions that could be wrong
3. Areas of uncertainty (PRIORITIZED):
   - [HIGH] {description} — Why risky, suggested test focus
   - [MEDIUM] {description}
   - [LOW] {description}
4. Integration points: Other components touched
5. Open questions: Unresolved items
```

All five items are required. Not all priority levels need to be present in Areas of uncertainty. If you have no uncertainties, explicitly state "No areas of uncertainty flagged."

## Before Completing

Before returning your final output to the orchestrator:

1. **Save Memory**: Invoke the `pact-memory` skill and save a memory documenting:
   - Context: What you were working on and why
   - Goal: What you were trying to achieve
   - Lessons learned: What worked, what didn't, gotchas discovered
   - Decisions: Key choices made with rationale
   - Entities: Components, files, services involved

This ensures your work context persists across sessions and is searchable by future agents.
