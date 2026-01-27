# Task Metadata Schema Reference

> **Purpose**: Complete schema documentation for PACT task metadata. Use as reference when creating or interpreting task structures.
>
> **Context**: PACT integrates with Claude Code's native Task system (v2.1.16+). Tasks use structured metadata to preserve PACT methodology context.

---

## Task Types Overview

| Type | Owner | Purpose | Example Names |
|------|-------|---------|---------------|
| **Phase** | Orchestrator | Track PACT phase progress | `PREPARE`, `CODE`, `TEST` |
| **Specialist** | Specialist agent | Track individual work items | `Backend: Implement auth` |
| **Workflow** | Orchestrator | Track lightweight workflows | `comPACT`, `Peer Review` |

---

## Phase Task Schema

Phase tasks represent the four PACT phases (Prepare, Architect, Code, Test) or plan-mode phases.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `taskType` | string | Yes | Always `"phase"` |
| `pactWorkflow` | string | Yes | `"orchestrate"` or `"plan-mode"` |
| `phase` | string | Yes | `"prepare"` \| `"architect"` \| `"code"` \| `"test"` |
| `variety` | object | No | Variety assessment (see below) |
| `featureBranch` | string | No | Git branch name (e.g., `"feature/user-auth"`) |
| `planRef` | string | No | Path to plan document (e.g., `"docs/plans/user-auth-plan.md"`) |
| `subtaskIds` | string[] | No | IDs of specialist subtasks belonging to this phase |
| `skipped` | boolean | No | `true` if phase was skipped |
| `skipReason` | string | No | Reason for skipping (when `skipped: true`) |
| `handoff` | object | No | Phase completion handoff (see below) |

### Variety Object

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `novelty` | number | 1-4 | How new is this work? |
| `scope` | number | 1-4 | How many concerns involved? |
| `uncertainty` | number | 1-4 | How clear are requirements? |
| `risk` | number | 1-4 | What's the impact if wrong? |
| `total` | number | 4-16 | Sum of dimensions |

### Phase Handoff Object

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | Brief description of what was accomplished |
| `produced` | string[] | Files or artifacts created/modified |
| `keyDecisions` | string[] | Important decisions made during the phase |
| `unresolvedItems` | array | Items needing attention (see below) |
| `nextPhaseContext` | string | Context the next phase needs to know |

### Unresolved Item Object

| Field | Type | Description |
|-------|------|-------------|
| `priority` | string | `"HIGH"` \| `"MEDIUM"` \| `"LOW"` |
| `description` | string | What needs attention |

### Example

```javascript
{
  taskType: "phase",
  pactWorkflow: "orchestrate",
  phase: "code",
  variety: {
    novelty: 2,
    scope: 3,
    uncertainty: 2,
    risk: 3,
    total: 10
  },
  featureBranch: "feature/user-auth",
  planRef: "docs/plans/user-auth-plan.md",
  subtaskIds: ["4", "5", "6"],
  handoff: {
    summary: "Implemented authentication service with JWT tokens",
    produced: [
      "src/auth/token-manager.ts",
      "src/auth/middleware.ts"
    ],
    keyDecisions: [
      "Used JWT with 15min expiry for access tokens",
      "Refresh tokens stored in httpOnly cookies"
    ],
    unresolvedItems: [
      { priority: "MEDIUM", description: "Token refresh race condition needs testing" }
    ],
    nextPhaseContext: "Focus testing on concurrent token refresh scenarios"
  }
}
```

---

## Specialist Subtask Schema

Specialist subtasks represent work delegated to individual specialist agents (coders, architect, preparer, test engineer).

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `taskType` | string | Yes | Always `"specialist"` |
| `phaseTaskId` | string | Yes | ID of parent phase task |
| `domain` | string | Yes | `"backend"` \| `"frontend"` \| `"database"` \| `"architecture"` \| `"preparation"` \| `"test"` |
| `specialist` | string | Yes | Agent type (e.g., `"pact-backend-coder"`) |
| `agentId` | string | No | Claude Code agent instance ID |
| `handoff` | object | No | Specialist completion handoff (see below) |

### Specialist Handoff Object

| Field | Type | Description |
|-------|------|-------------|
| `produced` | string[] | Files created or modified |
| `decisions` | string[] | Key implementation decisions with rationale |
| `uncertainties` | array | Areas of uncertainty (see below) |
| `openQuestions` | string[] | Unresolved questions for orchestrator |

### Uncertainty Object

| Field | Type | Description |
|-------|------|-------------|
| `priority` | string | `"HIGH"` \| `"MEDIUM"` \| `"LOW"` |
| `description` | string | What's uncertain and why it matters |

### Example

```javascript
{
  taskType: "specialist",
  phaseTaskId: "3",
  domain: "backend",
  specialist: "pact-backend-coder",
  agentId: "agent-abc123",
  handoff: {
    produced: [
      "src/auth/token-manager.ts",
      "src/auth/token-manager.test.ts"
    ],
    decisions: [
      "Used symmetric signing for JWTs (faster, simpler for single-service)",
      "Token storage uses in-memory cache with Redis fallback"
    ],
    uncertainties: [
      { priority: "HIGH", description: "Race condition possible during concurrent token refresh" },
      { priority: "MEDIUM", description: "Clock skew >5s may cause validation failures" }
    ],
    openQuestions: [
      "Should refresh tokens use rotation?"
    ]
  }
}
```

---

## Workflow Task Schema

Workflow tasks represent lightweight workflows like comPACT or peer review that don't use the full PACT phase structure.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `taskType` | string | Yes | Always `"workflow"` |
| `pactWorkflow` | string | Yes | `"comPACT"` \| `"peer-review"` |
| `domain` | string | No | Primary domain (for comPACT) |
| `subtaskIds` | string[] | No | IDs of specialist/reviewer subtasks |
| `handoff` | object | No | Workflow completion handoff |

### Workflow Handoff Object (comPACT)

Same structure as Specialist Handoff.

### Workflow Handoff Object (Peer Review)

| Field | Type | Description |
|-------|------|-------------|
| `verdict` | string | `"APPROVED"` \| `"CHANGES_REQUESTED"` \| `"NEEDS_DISCUSSION"` |
| `findings` | array | Review findings (see below) |
| `summary` | string | Overall review summary |

### Finding Object

| Field | Type | Description |
|-------|------|-------------|
| `reviewer` | string | Which reviewer found this |
| `severity` | string | `"CRITICAL"` \| `"MAJOR"` \| `"MINOR"` \| `"SUGGESTION"` |
| `category` | string | `"security"` \| `"performance"` \| `"design"` \| `"testing"` \| `"style"` |
| `description` | string | What was found |
| `location` | string | File and line (if applicable) |

### Example (comPACT)

```javascript
{
  taskType: "workflow",
  pactWorkflow: "comPACT",
  domain: "backend",
  subtaskIds: ["7", "8"],
  handoff: {
    produced: ["src/api/validation.ts"],
    decisions: ["Used Zod for schema validation"],
    uncertainties: [],
    openQuestions: []
  }
}
```

### Example (Peer Review)

```javascript
{
  taskType: "workflow",
  pactWorkflow: "peer-review",
  subtaskIds: ["10", "11", "12"],
  handoff: {
    verdict: "CHANGES_REQUESTED",
    summary: "Good implementation overall; two security items need addressing",
    findings: [
      {
        reviewer: "pact-architect",
        severity: "MAJOR",
        category: "security",
        description: "JWT secret loaded from env but not validated at startup",
        location: "src/auth/config.ts:15"
      },
      {
        reviewer: "pact-test-engineer",
        severity: "MINOR",
        category: "testing",
        description: "Missing test for token expiry edge case",
        location: "src/auth/token-manager.test.ts"
      }
    ]
  }
}
```

---

## Nested Task Schema (rePACT)

Nested PACT cycles use the same Phase Task schema with additional fields for parent linkage.

### Additional Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `parentPhaseId` | string | Yes | ID of parent phase task that spawned this nested cycle |
| `nestingLevel` | number | Yes | Depth of nesting (1 or 2; max is 2) |

### Naming Convention

Nested phase tasks use `rePACT:` prefix: `rePACT: PREPARE`, `rePACT: CODE`, etc.

### Example

```javascript
{
  taskType: "phase",
  pactWorkflow: "orchestrate",
  phase: "code",
  parentPhaseId: "3",
  nestingLevel: 1,
  // ... other phase task fields
}
```

---

## Algedonic Annotation Schema

Algedonic signals annotate existing tasks rather than creating new ones. These fields are added to any task's metadata when an algedonic signal is emitted.

### Active Halt Fields

Added when a HALT signal is active (work stopped, awaiting user acknowledgment).

| Field | Type | Description |
|-------|------|-------------|
| `algedonicHalt.timestamp` | string | ISO timestamp when signal was emitted |
| `algedonicHalt.category` | string | `"SECURITY"` \| `"DATA"` \| `"ETHICS"` |
| `algedonicHalt.issue` | string | One-line description of the issue |
| `algedonicHalt.evidence` | string | What triggered the signal |
| `algedonicHalt.impact` | string | Why this threatens viability |
| `algedonicHalt.recommendedAction` | string | Suggested response |
| `algedonicHalt.awaitingAcknowledgment` | boolean | `true` until user responds |

### Active Alert Fields

Added when an ALERT signal is active (work paused, awaiting user decision).

| Field | Type | Description |
|-------|------|-------------|
| `algedonicAlert.timestamp` | string | ISO timestamp when signal was emitted |
| `algedonicAlert.category` | string | `"QUALITY"` \| `"SCOPE"` \| `"META-BLOCK"` |
| `algedonicAlert.issue` | string | One-line description |
| `algedonicAlert.evidence` | string | What triggered the signal |
| `algedonicAlert.awaitingDecision` | boolean | `true` until user responds |

### History Fields

Tracks resolved algedonic signals for audit trail.

| Field | Type | Description |
|-------|------|-------------|
| `algedonicHistory` | array | List of resolved signals |
| `algedonicHistory[].type` | string | `"HALT"` \| `"ALERT"` |
| `algedonicHistory[].category` | string | Signal category |
| `algedonicHistory[].triggeredAt` | string | ISO timestamp |
| `algedonicHistory[].resolvedAt` | string | ISO timestamp |
| `algedonicHistory[].resolution` | string | How it was resolved |

### Example

```javascript
{
  taskType: "phase",
  phase: "code",
  // ... other fields ...

  // Active HALT (work stopped)
  algedonicHalt: {
    timestamp: "2026-01-27T14:30:00Z",
    category: "SECURITY",
    issue: "AWS credentials hardcoded in source file",
    evidence: "Found in src/config/aws.ts:15",
    impact: "Credentials exposed if committed",
    recommendedAction: "Remove credentials, use environment variables",
    awaitingAcknowledgment: true
  },

  // Previous signals (resolved)
  algedonicHistory: [
    {
      type: "ALERT",
      category: "QUALITY",
      triggeredAt: "2026-01-27T10:15:00Z",
      resolvedAt: "2026-01-27T10:45:00Z",
      resolution: "User chose to continue; added TODO for follow-up"
    }
  ]
}
```

---

## imPACT History Schema

When `/PACT:imPACT` modifies existing tasks, it tracks the history in metadata.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `imPACTHistory` | array | List of imPACT interventions |
| `imPACTHistory[].timestamp` | string | When imPACT was invoked |
| `imPACTHistory[].trigger` | string | What caused the blocker |
| `imPACTHistory[].outcome` | string | `"redo-solo"` \| `"redo-with-help"` \| `"proceed-with-help"` |
| `imPACTHistory[].action` | string | What was done to resolve |

### Example

```javascript
{
  taskType: "phase",
  phase: "code",
  // ... other fields ...

  imPACTHistory: [
    {
      timestamp: "2026-01-27T11:00:00Z",
      trigger: "Type errors after adding new dependency",
      outcome: "redo-with-help",
      action: "Re-ran ARCHITECT phase with pact-architect to resolve type conflicts"
    }
  ]
}
```

---

## Plan-Mode Task Schema

Plan-mode uses phase tasks with plan-specific naming.

### Phase Names

| Phase | Task Name | Purpose |
|-------|-----------|---------|
| Analyze | `Plan: Analyze` | Assess scope, select specialists |
| Consult | `Plan: Consult` | Gather specialist perspectives |
| Synthesize | `Plan: Synthesize` | Resolve conflicts, sequence work |
| Present | `Plan: Present` | Save plan, await approval |

### Planner Subtask Naming

During the Consult phase, planner subtasks use: `Plan: {Domain} perspective`

Examples:
- `Plan: Backend perspective`
- `Plan: Architecture perspective`
- `Plan: Database perspective`

### Example

```javascript
// Phase task
{
  taskType: "phase",
  pactWorkflow: "plan-mode",
  phase: "consult",
  subtaskIds: ["2", "3", "4"]
}

// Planner subtask
{
  taskType: "specialist",
  phaseTaskId: "1",
  domain: "backend",
  specialist: "pact-backend-coder",
  // Operates in "planning-only mode" - analysis, not implementation
}
```

---

## Quick Reference: Naming Conventions

| Task Type | Format | Examples |
|-----------|--------|----------|
| Phase task | `PHASE` | `PREPARE`, `ARCHITECT`, `CODE`, `TEST` |
| Specialist subtask | `Domain: Work` | `Backend: Implement auth`, `Frontend: Add login form` |
| Workflow task | `Title Case` | `comPACT`, `Peer Review` |
| Plan-mode phases | `Plan: Phase` | `Plan: Analyze`, `Plan: Consult` |
| Plan-mode subtasks | `Plan: Domain perspective` | `Plan: Backend perspective` |
| Nested (rePACT) | `rePACT: PHASE` | `rePACT: PREPARE`, `rePACT: CODE` |
| Review subtasks | `Review: Focus` | `Review: Architecture`, `Review: Test coverage` |
