---
name: pact-task-tracking
description: |
  Task tracking protocol for PACT specialist agents. Auto-loaded via agent frontmatter.
  Defines how to report progress, blockers, and completion status via TaskCreate/TaskUpdate tools.
---

# Task Tracking Protocol

> **Architecture**: See [pact-task-hierarchy.md](../../protocols/pact-task-hierarchy.md) for the full hierarchy model.

> **Reference**: See [Claude Code Task System](https://docs.anthropic.com/en/docs/claude-code/tasks) for full API documentation.

> **Note**: The orchestrator passes your assigned Task ID when dispatching you. Use this ID in all TaskUpdate calls.

You have been assigned Task ID: {task_id}

> **If no Task ID was provided** (the line above still reads `{task_id}` literally), skip all TaskUpdate calls in this protocol. Your work proceeds normally; only task tracking is skipped.

## On Start

Before any other work, update your task status:

```
TaskUpdate(taskId="{task_id}", status="in_progress")
```

## On Blocker

If you cannot proceed:

1. Create a blocker task:
   ```
   TaskCreate(subject="Resolve: {description}", metadata={"type": "blocker"})
   ```
2. Link it to your task:
   ```
   TaskUpdate(taskId="{task_id}", addBlockedBy=[blocker_id])
   ```
3. Stop work and report: "BLOCKER: {description}"

## On Algedonic Signal

When you detect a viability threat:

1. Create an algedonic task:
   ```
   TaskCreate(subject="⚠️ [HALT|ALERT]: {category}", metadata={"type": "algedonic", "level": "...", "category": "..."})
   ```
2. Link it to your task:
   ```
   TaskUpdate(taskId="{task_id}", addBlockedBy=[algedonic_id])
   ```
3. Stop immediately
4. Report signal to orchestrator

## On Completion

After all work is done:

```
TaskUpdate(
  taskId="{task_id}",
  status="completed",
  metadata={
    "produced": ["file1.ts", "file2.ts"],
    "decisions": ["key decisions made"],
    "uncertainties": ["areas needing review"]
  }
)
```

