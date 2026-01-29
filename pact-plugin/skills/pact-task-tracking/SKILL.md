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

Begin working on your assigned task immediately. No status update call is needed — the orchestrator tracks your task status.

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
   ALGEDONIC [HALT|ALERT]: {Category}

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
1. Produced: {files created or modified, with paths}
2. Key context: {decisions made, patterns used, assumptions}
3. Areas of uncertainty: {where bugs might hide, tricky parts}
4. Open questions: {anything unresolved that needs attention}
```

All four items are required, even if some are "None."
