## Parallel Execution Protocol

**Philosophy**: Parallel unless proven dependent. Sequential execution requires explicit justification.

Parallelization is a primary variety amplification strategy (see [pact-variety.md](pact-variety.md)). This protocol provides the decision framework and patterns for maximizing parallel work while avoiding conflicts.

---

## Quick Dependency Checklist (QDCL)

Before executing work units, run this checklist. Target: under 1 minute for most tasks.

For each work unit pair (A, B):

| Check | If True | Action |
|-------|---------|--------|
| Same file modified? | A and B both write to same file | Sequential (or define strict section boundaries) |
| A's output is B's input? | B needs A's result to start | Sequential (A first) |
| Shared interface undefined? | Both depend on undefined contract | Define interface first, then parallel |
| None of above? | No dependencies detected | **Parallel** |

**Output format**: After running QDCL, declare the execution strategy:

> **Execution Strategy**: [Parallel / Sequential / Mixed]
> - {Unit A, Unit B}: Parallel — no shared dependencies
> - {Unit C}: Sequential after A — consumes A's output
> - Rationale for sequential (if any): {specific reason}

---

## Work Unit Decomposition

Use this template to specify work units before parallelization analysis.

```markdown
## Work Unit: {name}

**Scope**: {files/components this unit owns}
**Produces**: {outputs other units may depend on}
**Consumes**: {inputs from other units}
**Specialist**: {pact-*-coder}

**Boundaries**:
- May modify: {file list}
- May read: {file list}
- Must not modify: {file list}
```

**Example**:

```markdown
## Work Unit: User API Endpoints

**Scope**: User CRUD operations
**Produces**: REST endpoints at /api/users/*
**Consumes**: User schema from Database unit
**Specialist**: pact-backend-coder

**Boundaries**:
- May modify: src/api/users/*, src/services/user.ts
- May read: src/types/user.ts, src/db/schema.ts
- Must not modify: src/db/*, src/api/auth/*
```

---

## Parallelization Patterns

### Pattern 1: Independent Components (Same Domain)

Multiple specialists of the same type working on non-overlapping files.

| Scenario | Analysis | Strategy |
|----------|----------|----------|
| "Fix 3 bugs in different files" | No shared files | 3 agents parallel |
| "Add validation to 5 endpoints" | Each endpoint in separate file | 5 agents parallel |
| "Implement 3 new React components" | Independent component files | 3 agents parallel |

**Worked Example**: "Fix bugs in user-service.ts, order-service.ts, payment-service.ts"
- QDCL: All different files, no shared deps → All parallel
- Invoke 3 backend-coders; first agent's error handling becomes standard

### Pattern 2: Cross-Domain Parallel

Different specialist types working on their respective domains when contracts are defined.

| Scenario | Prerequisite | Strategy |
|----------|--------------|----------|
| Backend + Frontend feature | API contract defined | Both parallel |
| Backend + Database | Schema defined first | DB first, then Backend |
| Frontend + Tests | Component exists | Tests parallel with Frontend if mocking |

**Worked Example**: "Implement user profile (backend API + frontend UI)"
- Prerequisite: API contract defined (GET/PUT /api/users/:id)
- QDCL: Different domains, contract defined → Parallel
- Invoke backend-coder + frontend-coder; frontend mocks until backend completes

### Pattern 3: Mixed Strategy

Some units parallel, then sequential dependent work.

| Phase | Units | Reasoning |
|-------|-------|-----------|
| Parallel Phase 1 | A, B, C | All independent |
| Sequential Phase 2 | D (after A), E (after B) | D consumes A, E consumes B |
| Parallel Phase 3 | D, E | Once available, D and E are independent |

**Worked Example**: "Add audit logging to user/order services, then dashboard"
- Units: A (user logging), B (order logging), C (dashboard)
- QDCL: A ↔ B parallel (different files); C sequential (needs A,B output)
- Phase 1: A + B parallel; Phase 2: C after Phase 1 completes

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Sequential by default** | Missed parallelization opportunity; slower execution | Run QDCL; require justification for sequential |
| **Ignoring shared files** | Merge conflicts; wasted work | QDCL catches this; sequence or assign boundaries |
| **Over-parallelization** | Coordination overhead exceeds benefit; convention drift | Limit parallel agents; use S2 coordination |
| **Analysis paralysis** | QDCL takes longer than the work itself | Time-box to 1 minute; default to parallel if unclear |
| **Undefined interfaces** | Agents make incompatible assumptions | Define contracts before parallel work |
| **Forgetting convention propagation** | Inconsistent code style across parallel work | S2 coordination; first agent establishes standard |

### Detecting Anti-Patterns

**Sequential by default** — Watch for:
- "I'll just run them one at a time to be safe"
- No explicit QDCL analysis performed
- Sequential execution without stated reason

**Analysis paralysis** — Watch for:
- QDCL taking more than 2 minutes
- Repeated re-analysis of the same dependencies
- Uncertainty leading to inaction

**Recovery**: If in doubt, default to parallel with S2 coordination active. Conflicts are recoverable; lost time is not.

---

## Integration with Other Protocols

| Protocol | Integration Point |
|----------|-------------------|
| **S2 Coordination** | Pre-parallel check, convention propagation, conflict resolution |
| **Variety Management** | Parallelization is a primary amplification strategy |
| **comPACT** | Same-domain parallelization patterns apply |
| **orchestrate** | Cross-domain parallelization with QDCL |

### S2 Pre-Parallel Check (Required)

Before parallel invocation, emit the S2 checkpoint (see [pact-s2-coordination.md](pact-s2-coordination.md)):

> **S2 Pre-Parallel Check**:
> - Shared files: [none / list with mitigation]
> - Shared interfaces: [none / contract defined by X]
> - Conventions: [pre-defined / first agent establishes]
> - Anticipated conflicts: [none / sequencing X before Y]

---

## Quick Reference

**Decision Tree**:
```
Start with task decomposition
         ↓
   Run QDCL (<1 min)
         ↓
   ┌─────┴─────┐
   ↓           ↓
Parallel    Sequential
   ↓           ↓
S2 Check    Execute in order
   ↓
Invoke agents
```

**Default Stance**: Parallel unless QDCL identifies dependency.

**Justification Required**: Sequential execution must state: "Sequential because [specific QDCL finding]"

---
