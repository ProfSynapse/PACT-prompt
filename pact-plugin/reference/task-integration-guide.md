# Task Integration Guide

> **Purpose**: How PACT methodology integrates with Claude Code's native Task system. Reference for orchestrators and developers understanding the hybrid model.
>
> **Audience**: PACT orchestrators, plugin developers, users wanting to understand task flow.

---

## Overview

PACT uses Claude Code's Task system as a **work tracking layer** while preserving PACT's **methodology layer**:

| Layer | What It Provides | Owned By |
|-------|------------------|----------|
| **Task System** | Status tracking, dependencies, blocking relationships | Claude Code |
| **PACT Methodology** | VSM structure, phases, coordination protocols, handoffs | PACT framework |

This separation means:
- Tasks track *what* is happening (status, blockers, completion)
- PACT protocols define *how* work flows (phases, delegation, quality gates)

---

## The Hybrid Task Model

### Core Concept

**Phase tasks** (owned by orchestrator) contain **specialist subtasks** (owned by specialists).

```
┌─────────────────────────────────────────────────────────────┐
│  /PACT:orchestrate "Implement user authentication"          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PREPARE ──► ARCHITECT ──► CODE ──► TEST                   │
│  (phase)     (phase)       (phase)   (phase)                │
│                              │                              │
│                              ▼                              │
│                    ┌─────────────────┐                      │
│                    │ CODE blockedBy: │                      │
│                    │ - Backend: ...  │ (subtask)            │
│                    │ - Frontend: ... │ (subtask)            │
│                    │ - Database: ... │ (subtask)            │
│                    └─────────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Why This Model?

1. **Visibility**: Tasks surface work status without reading agent threads
2. **Dependencies**: `blockedBy` relationships encode phase sequencing
3. **Parallelism**: Subtasks within a phase can run concurrently
4. **Handoffs**: Structured metadata captures context for next phase

---

## Workflow Integration

### /PACT:orchestrate

Full PACT cycle with all four phases.

**Task Structure**:
```
At start:
  Create: PREPARE, ARCHITECT, CODE, TEST (4 phase tasks)
  Set: ARCHITECT blockedBy PREPARE
       CODE blockedBy ARCHITECT
       TEST blockedBy CODE

Per phase:
  1. Mark phase in_progress
  2. Create specialist subtasks
  3. Phase blockedBy its subtasks
  4. Specialists work (parallel)
  5. Subtasks complete → phase auto-unblocks
  6. Orchestrator marks phase completed
```

**Skipped Phases**:
When a phase is skipped (e.g., skip PREPARE for routine tasks):
- Create the phase task anyway
- Immediately mark `completed`
- Set `metadata: { skipped: true, skipReason: "..." }`

This preserves the audit trail while allowing flexibility.

### /PACT:comPACT

Single-domain delegation with light ceremony.

**Task Structure**:
```
Create: 1 workflow task (comPACT)
Create: Specialist subtasks for work items
Set: Workflow blockedBy all subtasks
All subtasks parallel (no inter-dependencies)
```

**Example**: "Fix 3 backend bugs"
```
comPACT (workflow)
├── Backend: Fix bug #1 (subtask) ──┐
├── Backend: Fix bug #2 (subtask) ──┼── all parallel
└── Backend: Fix bug #3 (subtask) ──┘
```

### /PACT:peer-review

Multi-agent code review before PR.

**Task Structure**:
```
Create: 1 workflow task (Peer Review)
Create: Reviewer subtasks:
  - Review: Architecture
  - Review: Test coverage
  - Review: {Domain} (based on PR focus)
All reviewers parallel
Handoff includes verdict + findings
```

**Verdict Values**:
- `APPROVED` - Ready to merge
- `CHANGES_REQUESTED` - Issues must be addressed
- `NEEDS_DISCUSSION` - Requires user input on trade-offs

### /PACT:plan-mode

Planning consultation before implementation.

**Task Structure**:
```
Create: 4 phase tasks (Plan: Analyze → Consult → Synthesize → Present)
During Consult:
  Create planner subtasks: Plan: Backend perspective, etc.
All planners parallel
Output: planRef to docs/plans/
```

**Key Difference**: No implementation occurs. Specialists operate in "planning-only mode" (analysis, recommendations, not code).

### /PACT:rePACT

Nested PACT cycle for complex sub-tasks.

**Task Structure**:
```
Create: Nested phase tasks with rePACT: prefix
  rePACT: PREPARE → rePACT: ARCHITECT → rePACT: CODE → rePACT: TEST
Link: parentPhaseId points to spawning phase
Block: Parent phase blockedBy nested TEST task
```

**Nesting Limit**: Maximum 2 levels to prevent infinite recursion.

### /PACT:imPACT

Triage when blocked. Modifies existing tasks rather than creating new ones.

**Task Modifications**:
- No new workflow task created
- Tracks `imPACTHistory` in current phase task's metadata
- May create additional subtasks (if "proceed with help")
- May reset phase status (if "redo")

---

## Task Lifecycle

### Status Transitions

| Status | Meaning | Triggered By |
|--------|---------|--------------|
| `pending` | Not yet started | Task creation |
| `in_progress` | Work underway | Orchestrator starts phase |
| `blocked` | Waiting on dependencies | `blockedBy` relationship active |
| `completed` | Work finished | Orchestrator marks done after handoff |

### Who Updates Status?

**Orchestrator owns all status transitions.**

Specialists:
- Do NOT update task status
- Return structured handoffs
- Report blockers to orchestrator

Orchestrator:
- Creates tasks
- Marks `in_progress` when starting
- Marks `completed` after receiving handoff
- Handles `blockedBy` relationships

This maintains clean separation: specialists focus on work, orchestrator manages coordination.

---

## Handoff Patterns

### Phase Handoffs

When a phase completes, the orchestrator captures:

```javascript
handoff: {
  summary: "Brief description of accomplishments",
  produced: ["list", "of", "files"],
  keyDecisions: ["decisions", "with", "rationale"],
  unresolvedItems: [
    { priority: "HIGH", description: "Needs attention" }
  ],
  nextPhaseContext: "What the next phase needs to know"
}
```

### Specialist Handoffs

When a specialist completes, they return:

```javascript
handoff: {
  produced: ["files", "created"],
  decisions: ["implementation", "decisions"],
  uncertainties: [
    { priority: "HIGH", description: "Potential issue" }
  ],
  openQuestions: ["Unresolved items"]
}
```

### Context Flow

```
PREPARE handoff → ARCHITECT receives nextPhaseContext
ARCHITECT handoff → CODE receives nextPhaseContext
CODE handoff → TEST receives nextPhaseContext (especially uncertainties)
```

**Uncertainty Priority Levels**:
- **HIGH**: "This could break in production" — TEST must cover
- **MEDIUM**: "Not 100% confident" — TEST should cover
- **LOW**: "Edge case I thought of" — TEST discretion

---

## Best Practices

### 1. Reference, Don't Duplicate

Use references to maintain context without bloating task metadata:

| Instead of | Use |
|------------|-----|
| Copying plan content into metadata | `planRef: "docs/plans/..."` |
| Duplicating phase context | `phaseTaskId` to look up parent |
| Embedding file contents | `produced: ["file/paths"]` |

### 2. Structured Handoffs Over Free Text

Handoffs should be machine-parseable:

```javascript
// Good
uncertainties: [
  { priority: "HIGH", description: "Race condition in token refresh" }
]

// Avoid
notes: "There might be a race condition, not sure how serious..."
```

### 3. Let Dependencies Do the Work

Use `blockedBy` relationships instead of manual coordination:

```javascript
// Good: Automatic unblocking
CODE.blockedBy = [subtask1, subtask2, subtask3]
// When all complete → CODE auto-unblocks

// Avoid: Manual polling
// "Check if backend finished before starting frontend..."
```

### 4. Preserve Audit Trail

Even for skipped work, create the task:

```javascript
// Phase skipped but recorded
{
  taskType: "phase",
  phase: "prepare",
  status: "completed",
  skipped: true,
  skipReason: "Routine task, requirements clear from description"
}
```

### 5. Algedonic Signals Annotate, Don't Create

When an algedonic signal fires:
- Annotate the current task with `algedonicHalt` or `algedonicAlert`
- Don't create a new "Algedonic" task
- This keeps signals attached to their context

---

## Relationship to PACT Concepts

### VSM Mapping

| VSM System | Task System Role |
|------------|------------------|
| **S1 (Operations)** | Specialist subtasks — the actual work |
| **S2 (Coordination)** | `blockedBy` relationships, parallel subtask management |
| **S3 (Control)** | Phase tasks — orchestrator's operational view |
| **S4 (Intelligence)** | Variety metadata, S4 checkpoints in handoffs |
| **S5 (Policy)** | Algedonic annotations bypass normal flow |

### Phase Boundaries

Tasks make phase boundaries explicit:

```
PREPARE completed → S4 checkpoint → ARCHITECT in_progress
```

The task status transition is the trigger for S4 checkpoint evaluation.

### Parallel Coordination (S2)

Task system supports S2 coordination:

1. **Pre-parallel check**: Before creating parallel subtasks, verify no file conflicts
2. **Subtask independence**: Parallel subtasks have no `blockedBy` between them
3. **Convention propagation**: First subtask's decisions noted in metadata for others

---

## Troubleshooting

### Task Stuck in Blocked State

**Check**: Are all `blockedBy` tasks completed?

**Common causes**:
- Subtask completed but status not updated
- Circular dependency (shouldn't happen with PACT structure)
- Subtask failed and wasn't handled

### Missing Handoff Data

**Check**: Did specialist return structured handoff?

**Common causes**:
- Agent thread ended unexpectedly
- Handoff not captured in task metadata

**Recovery**: Orchestrator can reconstruct from agent output or re-run subtask.

### Algedonic Signal Not Surfacing

**Check**: Is `awaitingAcknowledgment` or `awaitingDecision` set to `true`?

**Protocol**: Algedonic signals must surface immediately. If task shows signal but user wasn't notified, this is a bug in orchestrator behavior.

---

## Migration Notes

### From Pre-Task PACT

If using PACT before Task integration:
- Handoff structure remains the same
- Phase sequencing now explicit in task dependencies
- Agent coordination unchanged (orchestrator still manages)

### Task System Requirements

- Claude Code v2.1.16+ required
- Task primitives: create, update status, set blockedBy, add metadata
- Orchestrator handles all task operations (specialists don't need task access)
