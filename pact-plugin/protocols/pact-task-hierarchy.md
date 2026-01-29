## Task Hierarchy

This document explains how PACT uses Claude Code's Task system to track work at multiple levels.

### Hierarchy Levels

```
Feature Task (created by orchestrator)
├── Phase Tasks (PREPARE, ARCHITECT, CODE, TEST)
│   ├── Agent Task 1 (specialist work)
│   ├── Agent Task 2 (parallel specialist)
│   └── Agent Task 3 (parallel specialist)
└── Review Task (peer-review phase)
```

### Task Ownership

| Level | Created By | Owned By | Lifecycle |
|-------|------------|----------|-----------|
| Feature | Orchestrator | Orchestrator | Spans entire workflow |
| Phase | Orchestrator | Orchestrator | Active during phase |
| Agent | Orchestrator | Specialist | Completed when specialist returns |

### Task States

Tasks progress through: `pending` → `in_progress` → `completed`

- **pending**: Created but not started
- **in_progress**: Active work underway
- **completed**: Work finished (success or documented failure)

### Blocking Relationships

Use `addBlockedBy` to express dependencies:

```
CODE phase Task
├── blockedBy: [ARCHITECT Task ID]
└── Agent Tasks within CODE
    └── blockedBy: [CODE phase Task ID]
```

### Metadata Conventions

Agent Tasks include metadata for context:

```json
{
  "phase": "CODE",
  "domain": "backend",
  "feature": "user-auth",
  "handoff": {
    "produced": ["src/auth.ts"],
    "uncertainty": ["token refresh edge cases"]
  }
}
```

### Integration with PACT Signals

- **Algedonic signals**: Emit via Task metadata or direct escalation
- **Variety signals**: Note in Task metadata when complexity differs from estimate
- **Handoff**: Store structured handoff in Task metadata on completion

### Example Flow

1. Orchestrator creates Feature Task: "Implement user authentication" (parent container)
2. Orchestrator creates PREPARE phase Task under the Feature Task
3. Orchestrator dispatches pact-preparer with agent Task (blocked by PREPARE phase Task)
4. Preparer completes, updates Task to completed with handoff metadata
5. Orchestrator marks PREPARE complete, creates ARCHITECT phase Task
6. Orchestrator creates CODE phase Task (blocked by ARCHITECT phase Task)
7. Pattern continues through remaining phases

