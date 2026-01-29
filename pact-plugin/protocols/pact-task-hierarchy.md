## Task Hierarchy

The Task system provides workflow visibility via Claude Code's native Task tools (TaskCreate, TaskUpdate, TaskGet, TaskList). The orchestrator owns ALL Task operations; agents communicate via structured text.

> **Critical Platform Constraint**: Sub-agents spawned via Claude Code's Task tool do NOT have access to TaskCreate, TaskUpdate, TaskGet, or TaskList. Only the parent orchestrator process has these tools.

### Hierarchy Structure

```
[Feature Task] "Implement user authentication"
├── [Phase Task] "PREPARE: auth feature"        (blockedBy: none)
│   └── [Agent Task] "pact-preparer: research auth patterns"
├── [Phase Task] "ARCHITECT: auth feature"      (blockedBy: PREPARE)
│   └── [Agent Task] "pact-architect: design auth service"
├── [Phase Task] "CODE: auth feature"           (blockedBy: ARCHITECT)
│   ├── [Agent Task] "pact-backend-coder: auth endpoint"
│   └── [Agent Task] "pact-frontend-coder: login form"
└── [Phase Task] "TEST: auth feature"           (blockedBy: CODE, all CODE agents)
    └── [Agent Task] "pact-test-engineer: auth tests"
```

### Creation Rules

| Task Type | Created When | Created By |
|-----------|--------------|------------|
| Feature Task | Workflow start | Orchestrator |
| Phase Tasks | Workflow start (upfront) | Orchestrator |
| Agent Tasks | Phase begins (dynamic) | Orchestrator |
| Blocker Tasks | Agent reports blocker via text | Orchestrator |
| Algedonic Tasks | Agent reports signal via text | Orchestrator |

### Dependency Model

- **Unify on `blockedBy`**: All dependencies expressed via `blockedBy`
- **Phase-to-phase**: Strict chain (PREPARE → ARCHITECT → CODE → TEST)
- **Agent-to-phase**: Agent tasks block the next phase
- **Skipped phases**: Created and immediately marked `completed` with note

### Naming Convention

- Feature: `"{verb} {feature}"`
- Phase: `"{PHASE}: {feature-slug}"`
- Agent: `"{agent-type}: {work-description}"`
- Blocker: `"Resolve: {description}"`
- Algedonic: `"⚠️ [HALT|ALERT]: {category}"`

### VSM-Task Mapping

| VSM System | Task System Role |
|------------|------------------|
| **S1 (Operations)** | Agents report status via structured text; do NOT call Task tools |
| **S2 (Coordination)** | Orchestrator uses TaskList for conflict detection, parallel agent visibility |
| **S3 (Orchestrator)** | Creates hierarchy, sets dependencies, translates agent reports into Task state |
| **S4 (Intelligence)** | Creates new Tasks on adaptation, deletes obsolete Tasks |
| **S5 (Policy)** | TaskList provides audit trail, user visibility via `/tasks` |

### Orchestrator Dispatch Lifecycle

| Event | Orchestrator Action |
|-------|---------------------|
| Before dispatching agent | `TaskCreate(subject="...")` → gets `task_id` |
| Immediately after dispatch | `TaskUpdate(taskId=task_id, status="in_progress")` |
| Agent completes (handoff received) | `TaskUpdate(taskId=task_id, status="completed", metadata={...})` |
| Agent reports blocker | `TaskCreate(subject="Resolve: {desc}")` then `TaskUpdate(taskId=task_id, addBlockedBy=[blocker_id])` |
| Agent emits algedonic signal | `TaskCreate(subject="⚠️ [HALT|ALERT]: {cat}")` then amplify scope |

### Tool Selection Guide

| Need | Tool | Example |
|------|------|---------|
| Create a new task | `TaskCreate` | Create agent task when phase begins |
| Update status, dependencies, metadata | `TaskUpdate` | Mark task completed, add blockedBy |
| See all tasks and their states | `TaskList` | Monitor progress, detect signals, audit |
| Get full details of one task | `TaskGet` | Read handoff metadata, blocker context |

### Agent Reporting (Text-Based)

Agents do NOT call Task tools. They report via structured text:

| Agent Event | Agent Action |
|-------------|-------------|
| Start | Begin working (orchestrator already marked task in_progress) |
| Blocker | Stop immediately, report: `BLOCKER: {description}` |
| Viability threat | Stop immediately, report: `⚠️ ALGEDONIC [HALT|ALERT]: {category} — {description}` |
| Completion | End response with structured HANDOFF |

The orchestrator translates agent text into Task tool calls.

---
