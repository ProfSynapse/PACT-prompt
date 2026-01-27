---
description: Recursive nested PACT cycle for complex sub-tasks
argument-hint: [backend|frontend|database|prepare|test|architect] <sub-task description>
---
Run a recursive PACT cycle for this sub-task: $ARGUMENTS

This command initiates a **nested P→A→C→T cycle** for a sub-task that is too complex for simple delegation but should remain part of the current feature work.

---

## Task Management

### Nested Task Structure

When rePACT starts, create nested phase tasks with `rePACT:` prefix:

```
rePACT: PREPARE    (nested)
rePACT: ARCHITECT  (nested)
rePACT: CODE       (nested)
rePACT: TEST       (nested)
```

The parent phase (from the outer orchestration) is `blockedBy` the nested `rePACT: TEST` task. This ensures the parent waits for the full nested cycle to complete.

### Nested Task Metadata

```javascript
{
  taskType: "phase",
  pactWorkflow: "rePACT",
  phase: "prepare" | "architect" | "code" | "test",
  nestingLevel: 1 | 2,
  parentPhaseId: "3",        // ID of the parent phase task that spawned this rePACT
  parentWorkflow: "orchestrate",
  domain: "backend" | "frontend" | "database" | null,  // null if multi-domain
  handoff: { ... }
}
```

### Parent-Child Linkage

1. **At rePACT start**: Record `parentPhaseId` from the outer phase that invoked rePACT
2. **Create 4 nested tasks**: `rePACT: PREPARE` → `rePACT: ARCHITECT` → `rePACT: CODE` → `rePACT: TEST`
3. **Set dependencies**:
   - Sequential within nested cycle: ARCH blockedBy PREP, CODE blockedBy ARCH, TEST blockedBy CODE
   - Parent blocked: Parent phase `blockedBy` nested `rePACT: TEST`
4. **On completion**: Nested TEST completes → parent phase auto-unblocks

### Example Task Structure

```
Parent: CODE (id: 3, status: in_progress)
  └── blockedBy: "7" (rePACT: TEST)

Nested tasks:
  rePACT: PREPARE   (id: 4, parentPhaseId: "3")
  rePACT: ARCHITECT (id: 5, parentPhaseId: "3", blockedBy: "4")
  rePACT: CODE      (id: 6, parentPhaseId: "3", blockedBy: "5")
  rePACT: TEST      (id: 7, parentPhaseId: "3", blockedBy: "6")
```

---

## When to Use rePACT

Use `/PACT:rePACT` when:
- A sub-task needs full P→A→C→T treatment (prepare, architect, code, test)
- The sub-task should stay on the current branch (no new branch/PR)
- You're already within a `/PACT:orchestrate` workflow

**Don't use rePACT when:**
- Sub-task is simple → use `/PACT:comPACT` instead
- Sub-task is a top-level feature → use `/PACT:orchestrate` instead
- You're not in an active orchestration → use `/PACT:orchestrate` instead

---

## Usage Modes

### Single-Domain Nested Cycle

When the sub-task fits within one specialist's domain:

```
/PACT:rePACT backend "implement OAuth2 token refresh mechanism"
```

This runs:
1. **Mini-Prepare**: Backend-focused research (token refresh best practices)
2. **Mini-Architect**: Backend component design (token storage, refresh flow)
3. **Mini-Code**: Backend implementation
4. **Mini-Test**: Smoke tests for the sub-component

### Multi-Domain Nested Cycle

When the sub-task spans multiple specialist domains:

```
/PACT:rePACT "implement payment processing sub-system"
```

This runs a mini-orchestration:
1. **Assess scope**: Determine which specialists are needed
2. **Mini-Prepare**: Research across relevant domains
3. **Mini-Architect**: Design the sub-system
4. **Mini-Code**: Invoke relevant coders (may be parallel)
5. **Mini-Test**: Smoke tests for the sub-system

---

## Specialist Selection

| Shorthand | Specialist | Use For |
|-----------|------------|---------|
| `backend` | pact-backend-coder | Server-side sub-components |
| `frontend` | pact-frontend-coder | UI sub-components |
| `database` | pact-database-engineer | Data layer sub-components |
| `prepare` | pact-preparer | Research-only nested cycles |
| `test` | pact-test-engineer | Test infrastructure sub-tasks |
| `architect` | pact-architect | Design-only nested cycles |

**If no specialist specified**: Assess the sub-task and determine which specialists are needed (multi-domain mode).

---

## Constraints

### Nesting Depth

**Maximum nesting: 2 levels**

```
/PACT:orchestrate (level 0)
  └── /PACT:rePACT (level 1)
        └── /PACT:rePACT (level 2) ← maximum
              └── /PACT:rePACT ← NOT ALLOWED
```

If you hit the nesting limit:
- Simplify the sub-task
- Use `/PACT:comPACT` for remaining work
- Or escalate to user for guidance

---

## Output Conciseness

**Default: Concise output.** User sees nested cycle start/completion, not mini-phase details.

| Internal (don't show) | External (show) |
|----------------------|-----------------|
| Mini-phase transitions | `rePACT: backend "OAuth2 token refresh"` |
| Nesting depth calculations | `rePACT complete. Continuing parent.` |
| Phase skip reasoning | (implicit — just proceed) |

**User can always ask** for nested cycle details (e.g., "What phases ran?" or "Show me the mini-architect output").

| Verbose (avoid) | Concise (prefer) |
|-----------------|------------------|
| "Starting mini-PREPARE phase for the nested cycle..." | (just do it) |
| "The nested cycle has completed successfully..." | `rePACT complete. Continuing parent.` |

---

### Branch Behavior

- **No new branch**: rePACT stays on the current feature branch
- **No PR**: Results integrate into the parent task's eventual PR
- All commits remain part of the current feature work

---

## Workflow

### Phase 0: Assess

Before starting, verify:
1. **Nesting depth**: Are we within the 2-level limit?
2. **Scope appropriateness**: Is this truly a sub-task of the parent?
3. **Domain determination**: Single-domain or multi-domain?

### Phase 1: Mini-Prepare (if needed)

For the sub-task, gather focused context:
- Research specific to the sub-component
- May be skipped if parent Prepare phase covered this
- Output: Notes integrated into parent preparation or separate `-nested` doc

### Phase 2: Mini-Architect (if needed)

Design the sub-component:
- Component design within the larger architecture
- Interface contracts with parent components
- May be skipped for simple sub-tasks
- Output: Design notes in `-nested` architecture doc or inline

### Phase 3: Mini-Code

Implement the sub-component:
- Invoke relevant specialist(s)
- For multi-domain: may invoke multiple specialists
- Apply S2 coordination if parallel work
- Output: Code + handoff summary

### Phase 4: Mini-Test

Verify the sub-component:
- Smoke tests for the sub-component
- Verify integration with parent components
- Output: Test results in handoff

### Phase 5: Integration

Complete the nested cycle:
1. **Verify**: Sub-component works within parent context
2. **Handoff**: Return control to parent orchestration with summary

---

## Context Inheritance

Nested cycles inherit from parent:
- Current feature branch
- Parent task context and requirements
- Architectural decisions from parent
- Coding conventions established in parent

Nested cycles produce:
- Code committed to current branch
- Handoff summary for parent orchestration

---

## Relationship to Specialist Autonomy

Specialists can invoke nested cycles autonomously (see Autonomy Charter).
`/PACT:rePACT` is for **orchestrator-initiated** nested cycles.

| Initiator | Mechanism |
|-----------|-----------|
| Specialist discovers complexity | Uses Autonomy Charter (declares, executes, reports) |
| Orchestrator identifies complex sub-task | Uses `/PACT:rePACT` command |

Both follow the same protocol; the difference is who initiates.

---

## Examples

### Example 1: Single-Domain Backend Sub-Task

```
/PACT:rePACT backend "implement rate limiting middleware"
```

Orchestrator runs mini-cycle:
- Mini-Prepare: Research rate limiting patterns
- Mini-Architect: Design middleware structure
- Mini-Code: Invoke backend coder
- Mini-Test: Smoke test rate limiting

### Example 2: Multi-Domain Sub-System

```
/PACT:rePACT "implement audit logging sub-system"
```

Orchestrator assesses scope:
- Needs: backend (logging service), database (audit tables), frontend (audit viewer)
- Runs mini-orchestration with all three domains
- Coordinates via S2 protocols

### Example 3: Skipping Phases

```
/PACT:rePACT frontend "implement form validation component"
```

If parent already has:
- Validation requirements (skip mini-prepare)
- Component design (skip mini-architect)

Then just run mini-code and mini-test.

---

## Error Handling

**If nesting limit exceeded:**
```
⚠️ NESTING LIMIT: Cannot invoke rePACT at level 3.
Options:
1. Simplify sub-task and use comPACT
2. Complete current level before starting new nested cycle
3. Escalate to user for guidance
```

**If sub-task is actually top-level:**
```
⚠️ SCOPE MISMATCH: This appears to be a top-level feature, not a sub-task.
Consider using /PACT:orchestrate instead.
```

---

## After Completion

When nested cycle completes:
1. **Summarize** what was done in the nested cycle
2. **Report** any decisions that affect the parent task
3. **Continue** with parent orchestration

**Handoff format**: Use the standard 4-item structure (Produced, Key context, Areas of uncertainty, Open questions). See orchestrate.md § Handoff Format.

The parent orchestration resumes with the sub-task complete.
