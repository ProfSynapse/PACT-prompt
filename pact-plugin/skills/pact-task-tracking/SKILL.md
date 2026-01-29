---
name: pact-task-tracking
description: |
  Task tracking protocol for PACT specialist agents. Auto-loaded via agent frontmatter.
  Defines how to report progress, blockers, and completion status via TaskCreate/TaskUpdate tools.
---

# Task Tracking Protocol

> **Architecture**: See [pact-task-hierarchy.md](../../protocols/pact-task-hierarchy.md) for the full hierarchy model.

> **Reference**: See [Claude Code Task System](https://docs.anthropic.com/en/docs/claude-code/tasks) for full API documentation.

## Your Task ID

The orchestrator includes a line in your prompt:
```
Your assigned Task ID is: <number>
```
Find that line and extract the number. That is **YOUR_TASK_ID** -- use it in every `TaskUpdate` call below.

> **If no such line exists in your prompt**, skip all `TaskUpdate` calls in this protocol. Your work proceeds normally; only Task tracking is skipped.

## On Start

Before any other work, update your Task status:

```
TaskUpdate(taskId=YOUR_TASK_ID, status="in_progress")
```

## On Blocker

If you cannot proceed:

1. Create a blocker Task:
   ```
   TaskCreate(subject="Resolve: {description}", metadata={"type": "blocker"})
   ```
2. Link it to your Task:
   ```
   TaskUpdate(taskId=YOUR_TASK_ID, addBlockedBy=[blocker_id])
   ```
3. Stop work and report: "BLOCKER: {description}"

## On Algedonic Signal

When you detect a viability threat:

1. Create an algedonic Task:
   ```
   TaskCreate(subject="⚠️ [HALT|ALERT]: {category}", metadata={"type": "algedonic", "level": "...", "category": "..."})
   ```
2. Link it to your Task:
   ```
   TaskUpdate(taskId=YOUR_TASK_ID, addBlockedBy=[algedonic_id])
   ```
3. Stop immediately
4. Report signal to orchestrator

## On Completion

After all work is done:

```
TaskUpdate(
  taskId=YOUR_TASK_ID,
  status="completed",
  metadata={
    "produced": ["file1.ts", "file2.ts"],
    "decisions": ["key decisions made"],
    "uncertainties": ["areas needing review"]
  }
)
```
