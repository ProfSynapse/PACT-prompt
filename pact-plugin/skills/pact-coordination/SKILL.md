---
name: pact-coordination
description: |
  S2/S3/S3* Control layer: Parallel execution, conflict prevention, progress tracking, audit.
  Use when: Coordinating parallel work, tracking progress, resolving conflicts, continuous review.
  Triggers on: parallel execution, conflict prevention, resource allocation, agent coordination,
  audit, continuous review, progress tracking, S2, S3, convention drift.
---

# PACT Coordination

S2/S3/S3* control layer protocols for parallel execution, conflict prevention,
progress tracking, and continuous audit during CODE phase.

---

## S2: Parallel Execution Coordination

### Pre-Parallel Checkpoint

Before invoking parallel agents, emit:

```
**S2 Pre-Parallel Check**:
- Shared files: [none / list with mitigation]
- Shared interfaces: [none / contract defined by X]
- Conventions: [pre-defined / first agent establishes]
- Anticipated conflicts: [none / sequencing X before Y]
```

### Conflict Prevention Rules

| Conflict Type | Prevention/Resolution |
|---------------|----------------------|
| Same file | Sequence agents OR assign section boundaries |
| Interface disagreement | Architect arbitrates; document decision |
| Naming/convention | First agent's choice = standard for batch |
| Resource contention | Orchestrator allocates; others wait |

### Convention Authority

- **Truly parallel**: Orchestrator pre-defines conventions in all prompts
- **Staggered**: First agent establishes; orchestrator extracts and propagates
- **Decision logs**: Subsequent agents MUST read first agent's decision log

### Convention Drift Check

Before editing any file:
1. Check what conventions are already established in the file/module
2. Follow established conventions (even if you'd do it differently)
3. If conventions seem wrong, escalate to orchestrator - don't silently change

### Anti-Oscillation Protocol

**Detect**: Agents undo each other's work or claim same interface
**Pause**: Stop both agents immediately
**Diagnose**: Technical disagreement or requirements ambiguity?
**Resolve**:
- Technical → Architect arbitrates
- Requirements → User clarifies
**Document**: Record resolution, then resume

---

## S3: Resource Allocation and Progress

### Agent Assignment

| Domain | Owner | Shared With (Read) |
|--------|-------|-------------------|
| Schema, DDL, migrations | Database Engineer | Backend |
| ORM, repositories | Backend Engineer | Database |
| API contracts | Architect defines | All coders |
| UI components | Frontend Engineer | Backend (API consumers) |

### Backend ↔ Database Boundary

**Sequence**: Database delivers schema → Backend implements ORM

| Database Owns | Backend Owns |
|---------------|--------------|
| Schema design, DDL | ORM models |
| Migrations | Repository/DAL layer |
| Complex SQL queries | App queries via ORM |
| Indexes | Connection pooling |

**Collaboration**: Backend needs complex query → ask Database.
Database needs access patterns → ask Backend.

### Cross-Agent Discovery Handoff

When you discover something affecting another domain:

```
⚠️ CROSS-AGENT: {what was discovered}
Affects: {which domain/agent}
Impact: {what they need to know/do}
```

Report to orchestrator immediately - do not attempt cross-domain fixes.

---

## S3*: Continuous Audit

### When to Invoke Parallel Audit

| Condition | Risk | Action |
|-----------|------|--------|
| Auth, payments, PII | High | Invoke test engineer in parallel |
| Multi-component integration | High | Early integration review |
| Novel patterns | Medium-High | Testability assessment |
| Routine code | Low | Sequential TEST sufficient |

**Default**: Sequential TEST phase. Parallel audit is opt-in.

### Audit Signals

| Signal | Meaning | Action |
|--------|---------|--------|
| 🟢 **GREEN** | Testable, no concerns | Continue normally |
| 🟡 **YELLOW** | Testability concerns | Note for TEST, continue |
| 🔴 **RED** | Critical issue | Interrupt CODE, triage now |

### Signal Format

```
[🟢/🟡/🔴] AUDIT: {one-line summary}

**Observation**: {what you found}
**Concern**: {why it matters}
**Recommendation**: {suggested action}
```

### 🔴 RED Signal Response Flow

1. Orchestrator receives signal
2. Pause affected coder(s)
3. Triage via `/PACT:imPACT`
4. Resolve, then resume CODE

**Note**: RED signals remain operational (S3). Security/ethics issues use
algedonic signals (S5 bypass) instead.

### Parallel Audit Rules (S2 for Audit)

- Test engineer is **READ-ONLY** on source files
- Test engineer may create test scaffolding in separate test files
- Coders have priority on source files
- Conflicts escalate to orchestrator

---

## S3* Audit Handoff Format

When handing off audit findings to TEST phase:

```
## Audit Handoff: {feature}

### Concerns Identified
1. **[PRIORITY]** {concern} - {location}
2. ...

### Areas Needing Extra Coverage
- {area}: {reason}

### Test Strategy Impact
- {how concerns should influence test approach}

### Recommended Focus
- {specific test scenarios to prioritize}
```

**Test engineer MUST acknowledge receipt** before TEST phase proceeds.

---

## Quick Reference Checklist

### Before Parallel Invocation
- [ ] Identified shared files and assigned boundaries
- [ ] Defined interface contracts
- [ ] Established or pre-defined conventions
- [ ] Set resolution authority for disputes

### During Parallel Execution
- [ ] Monitoring for anti-oscillation signals
- [ ] Propagating conventions from first agent
- [ ] Checking for 🔴 audit signals

### On Cross-Domain Discovery
- [ ] Emitted CROSS-AGENT signal
- [ ] Reported to orchestrator
- [ ] Did NOT attempt cross-domain fix

### Convention Drift Prevention
- [ ] Checked existing conventions before editing
- [ ] Following established patterns
- [ ] Escalated if conventions seem wrong
