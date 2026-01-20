---
description: Delegate a task to PACT specialist agents
argument-hint: [e.g., implement feature X]
---
Orchestrate specialist PACT agents through the PACT workflow to address: $ARGUMENTS

---

## S3/S4 Mode Awareness

This command primarily operates in **S3 mode** (operational control)—executing the plan and coordinating agents. However, mode transitions are important:

| Phase | Primary Mode | Mode Checks |
|-------|--------------|-------------|
| **Before Starting** | S4 | Understand task, assess complexity, check for plans |
| **Context Assessment** | S4 | Should phases be skipped? What's the right approach? |
| **Phase Execution** | S3 | Coordinate agents, track progress, clear blockers |
| **On Blocker** | S4 | Assess before responding—is this operational or strategic? |
| **Between Phases** | S4 | Still on track? Adaptation needed? |
| **After Completion** | S4 | Retrospective—what worked, what didn't? |

When transitioning to S4 mode, pause and ask: "Are we still building the right thing, or should we adapt?"

---

## Responding to Algedonic Signals

Algedonic signals are emergency escalations that bypass normal triage. You **MUST** surface them to the user immediately.

| Signal | Response |
|--------|----------|
| **HALT** (Security, Data, Ethics) | Stop ALL agents, present to user, await acknowledgment |
| **ALERT** (Quality, Scope, Meta-block) | Pause current work, present options, await decision |

**Algedonic vs imPACT**: Operational blocker → `/PACT:imPACT` ("How do we proceed?"). Viability threat → Algedonic ("Should we proceed at all?"). If unsure, err toward algedonic (safer).

See [algedonic.md](../protocols/algedonic.md) for signal format and full protocol.

---

## Before Starting

### Task Variety Assessment

Before running orchestration, assess task variety using the protocol in [pact-variety.md](../protocols/pact-variety.md).

**Quick Assessment Table**:

| If task appears... | Variety Level | Action |
|-------------------|---------------|--------|
| Single file, one domain, routine | Low (4-6) | Offer comPACT: "This could be handled by a single specialist. Use comPACT?" |
| Multiple files, one domain, familiar | Low-Medium | Proceed with orchestrate, consider skipping PREPARE |
| Multiple domains, some ambiguity | Medium (7-10) | Standard orchestrate with all phases |
| Greenfield, architectural decisions, unknowns | High (11-14) | Recommend plan-mode first |
| Novel technology, unclear requirements, critical stakes | Extreme (15-16) | Recommend research spike before planning |

**Variety Dimensions** (score 1-4 each, sum for total):
- **Novelty**: Routine (1) → Unprecedented (4)
- **Scope**: Single concern (1) → Cross-cutting (4)
- **Uncertainty**: Clear (1) → Unknown (4)
- **Risk**: Low impact (1) → Critical (4)

**When uncertain**: Default to standard orchestrate. Variety can be reassessed at phase transitions.

**User override**: User can always specify their preferred workflow regardless of assessment.

---

1. **Create feature branch** if not already on one
2. **Check for plan** in `docs/plans/` matching this task

### Plan Status Handling

| Status | Action |
|--------|--------|
| PENDING APPROVAL | `/PACT:orchestrate` = implicit approval → update to IN_PROGRESS |
| APPROVED | Update to IN_PROGRESS |
| BLOCKED | Ask user to resolve or proceed without plan |
| IN_PROGRESS | Confirm: continue or restart? |
| SUPERSEDED/IMPLEMENTED | Confirm with user before proceeding |
| No plan found | Proceed—phases will do full discovery |

---

## Context Assessment

Before executing phases, assess which are needed based on existing context:

| Phase | Run if... | Skip if... |
|-------|-----------|------------|
| **PREPARE** | Requirements unclear, external APIs to research, dependencies unmapped | Approved plan exists with Preparation Phase section, OR requirements explicit in task, OR existing `docs/preparation/` covers scope |
| **ARCHITECT** | New component or module, interface contracts undefined, architectural decisions required | Approved plan exists with Architecture Phase section, OR following established patterns, OR `docs/architecture/` covers design |
| **CODE** | Always run | Never skip |
| **TEST** | Integration/E2E tests needed, complex component interactions, security/performance verification | Trivial change (no new logic requiring tests) AND no integration boundaries crossed AND isolated change with no meaningful test scenarios |

**Conflict resolution**: When both "Run if" and "Skip if" criteria apply, **run the phase** (safer default). Example: A plan exists but requirements have changed—run PREPARE to validate.

**Plan-aware fast path**: When an approved plan exists in `docs/plans/`, PREPARE and ARCHITECT are typically skippable—the plan already synthesized specialist perspectives. Skip unless scope has changed or plan appears stale (typically >2 weeks; ask user to confirm if uncertain).

**State your assessment before proceeding.** For each skipped phase, state:
1. Which skip criterion was met
2. The context source (plan path, doc path, or pattern name)

Example:

> "Approved plan found at `docs/plans/user-auth-jwt-plan.md`. Skipping PREPARE (plan has Preparation Phase section). Skipping ARCHITECT (plan has Architecture Phase section). Running CODE. Running TEST (plan specifies integration tests needed)."

Or without a plan:

> "No plan found. Skipping PREPARE (requirements explicit in task). Skipping ARCHITECT (following established pattern in `src/utils/`). Running CODE. Skipping TEST (trivial change, no new logic to test)."

The user can override your assessment if they want more or less ceremony.

---

## Handling Decisions When Phases Were Skipped

When a phase is skipped but a coder encounters a decision that would have been handled by that phase:

| Decision Scope | Examples | Action |
|----------------|----------|--------|
| **Minor** | Naming conventions, local file structure, error message wording | Coder decides, documents in commit message |
| **Moderate** | Interface shape within your module, error handling pattern, internal component boundaries | Coder decides and implements, but flags decision with rationale in handoff; orchestrator validates before next phase |
| **Major** | New module needed, cross-module contract, architectural pattern affecting multiple components | Blocker → `/PACT:imPACT` → may need to run skipped phase |

**Boundary heuristic**: If a decision affects files outside the current specialist's scope, treat it as Major.

**Coder instruction when phases were skipped**:

> "PREPARE and/or ARCHITECT were skipped based on existing context. Minor decisions (naming, local structure) are yours to make. For moderate decisions (interface shape, error patterns), decide and implement but flag the decision with your rationale in the handoff so it can be validated. Major decisions affecting other components are blockers—don't implement, escalate."

This prevents excessive ping-pong for small decisions while catching real issues.

---

## Handoff Format

Each specialist should end with a structured handoff:

```
1. **Produced**: Files created/modified
2. **Key context**: Decisions made, patterns used, assumptions
3. **Areas of uncertainty**: Where bugs might hide, tricky parts, things to watch
4. **Open questions**: Anything unresolved
```

**Example**: `1. Produced: src/middleware/rateLimiter.ts. 2. Key context: Used token bucket with Redis. 3. Areas of uncertainty: Edge case with concurrent resets. 4. Open questions: None.`

---

### Phase 1: PREPARE → `pact-preparer`

**Skip criteria met?** → Proceed to Phase 2.

**Plan sections to pass** (if plan exists):
- "Preparation Phase"
- "Open Questions > Require Further Research"

**Invoke `pact-preparer` with**:
- Task description
- Plan sections above (if any)
- "Reference the approved plan at `docs/plans/{slug}-plan.md` for full context."

**Before next phase**:
- [ ] Outputs exist in `docs/preparation/`
- [ ] Specialist handoff received (see Handoff Format below)
- [ ] If blocker reported → `/PACT:imPACT`
- [ ] **S4 Checkpoint** (see [pact-s4-checkpoints.md](../protocols/pact-s4-checkpoints.md)): Environment stable? Model aligned? Plan viable?

---

### Post-PREPARE Re-assessment

If PREPARE ran and ARCHITECT was marked "Skip," compare PREPARE's recommended approach to the skip rationale:

- **Approach matches rationale** → Skip holds
- **Novel approach** (new components, interfaces, expanded scope) → Override, run ARCHITECT

**Example**:
> Skip rationale: "following established pattern in `src/utils/`"
> PREPARE recommends "add helper to existing utils" → Skip holds
> PREPARE recommends "new ValidationService class" → Override, run ARCHITECT

---

### Phase 2: ARCHITECT → `pact-architect`

**Skip criteria met (after re-assessment)?** → Proceed to Phase 3.

**Plan sections to pass** (if plan exists):
- "Architecture Phase"
- "Key Decisions"
- "Interface Contracts"

**Invoke `pact-architect` with**:
- Task description
- PREPARE phase outputs
- Plan sections above (if any)
- "Reference the approved plan at `docs/plans/{slug}-plan.md` for full context."

**Before next phase**:
- [ ] Outputs exist in `docs/architecture/`
- [ ] Specialist handoff received (see Handoff Format above)
- [ ] If blocker reported → `/PACT:imPACT`
- [ ] **S4 Checkpoint**: Environment stable? Model aligned? Plan viable?

---

### Phase 3: CODE → `pact-*-coder(s)`

**Always runs.** This is the core work.

> **S5 Policy Checkpoint (Pre-CODE)**: Before invoking coders, verify:
> 1. "Does the architecture align with project principles?"
> 2. "Am I delegating ALL code changes to specialists?" (orchestrator writes no application code)
> 3. "Are there any S5 non-negotiables at risk?"
>
> **Delegation reminder**: Even if you identified the exact implementation during earlier phases, you must delegate the actual coding. Knowing what to build ≠ permission to build it yourself.

**Plan sections to pass** (if plan exists):
- "Code Phase"
- "Implementation Sequence"
- "Commit Sequence"

**Select coder(s)** based on scope:
- `pact-backend-coder` — server-side logic, APIs
- `pact-frontend-coder` — UI, client-side
- `pact-database-engineer` — schema, queries, migrations

#### Parallel-First Philosophy

**Default stance**: Parallel unless proven dependent.

The orchestrator should **expect** to use parallel execution. Sequential is the exception requiring explicit justification. This philosophy reflects the reality that most CODE phase work involves independent domains (backend, frontend, database) or independent components within a domain.

**Required decision output** (no exceptions):
- "**Parallel**: [groupings]" — the expected outcome
- "**Sequential because [specific reason]**: [ordering]" — requires explicit justification
- "**Mixed**: [parallel groupings], then [sequential dependencies]" — when genuinely mixed

**Deviation from parallel requires articulated reasoning.** "I'm not sure" defaults to parallel with S2 coordination, not sequential.

**Analysis should complete quickly.** Use the Quick Dependency Checklist (QDCL) below. If QDCL analysis takes more than 2 minutes, you're likely over-analyzing independent tasks—default to parallel with S2 coordination.

---

#### Execution Strategy Analysis

Before invoking coders, complete the **Quick Dependency Checklist (QDCL)** to determine your execution strategy.

> **REQUIRED**: You must complete the QDCL and emit the checklist output before invoking coders. This is not optional.

**Quick Dependency Checklist (QDCL)**:

For each pair of work units, check:
```
[ ] Same file modified? → Sequential (or define strict boundaries)
[ ] A's output is B's input? → Sequential (A first)
[ ] Shared interface undefined? → Define interface first, then parallel
[ ] None of above? → Parallel
```

**Emit your QDCL result** (example): `Backend ↔ Frontend: Parallel | Backend ↔ DB: Sequential (schema first)`

**If QDCL shows no dependencies**: Parallel is your answer. Don't second-guess.

#### S2 Pre-Parallel Coordination

Before parallel invocation, check: shared files? shared interfaces? conventions established?

- **Shared files**: Sequence those agents OR assign clear boundaries
- **Conventions**: First agent's choice becomes standard; propagate to others
- **Resolution authority**: Technical disagreements → Architect arbitrates; Style/convention → First agent's choice

**Include in parallel prompts**: "You are working in parallel. Your scope is [files]. Do not modify files outside your scope."

#### Optional: S3* Parallel Audit

**Trigger conditions** (invoke when ANY apply): Security-sensitive code, complex multi-component integration, novel patterns, or user requests monitoring.

Invoke test engineer in audit mode alongside coders. Signal meanings: 🟢 no concerns (continue), 🟡 concerns noted (log for TEST phase), 🔴 critical issue (pause coders, run `/PACT:imPACT`). See [pact-s3-audit.md](../protocols/pact-s3-audit.md).

**Invoke coder(s) with**:
- Task description
- ARCHITECT phase outputs (or plan's Architecture Phase if ARCHITECT was skipped)
- Plan sections above (if any)
- "Reference the approved plan at `docs/plans/{slug}-plan.md` for full context."
- If PREPARE/ARCHITECT were skipped, include: "PREPARE and/or ARCHITECT were skipped based on existing context. Minor decisions (naming, local structure) are yours to make. For moderate decisions (interface shape, error patterns), decide and implement but flag the decision with your rationale in the handoff so it can be validated. Major decisions affecting other components are blockers—don't implement, escalate."
- "Testing: Run the full test suite before completing. If your changes break existing tests, fix them."

**Before next phase**:
- [ ] Implementation complete
- [ ] All tests passing (full test suite; fix any tests your changes break)
- [ ] Specialist handoff(s) received (see Handoff Format above)
- [ ] If blocker reported → `/PACT:imPACT`
- [ ] **S4 Checkpoint**: Environment stable? Model aligned? Plan viable?

#### Handling Complex Sub-Tasks During CODE

If a sub-task emerges that is too complex for a single specialist invocation:

| Sub-Task Complexity | Indicators | Use |
|---------------------|------------|-----|
| **Simple** | Code-only, clear requirements | Direct specialist invocation |
| **Focused** | Single domain, no research needed | `/PACT:comPACT` |
| **Complex** | Needs own P→A→C→T cycle | `/PACT:rePACT` |

**When to use `/PACT:rePACT`:**
- Sub-task needs its own research/preparation phase
- Sub-task requires architectural decisions before coding
- Sub-task spans multiple concerns within a domain

---

### Phase 4: TEST → `pact-test-engineer`

**Skip criteria met?** → Proceed to "After All Phases Complete."

**Plan sections to pass** (if plan exists):
- "Test Phase"
- "Test Scenarios"
- "Coverage Targets"

**Invoke `pact-test-engineer` with**:
- Task description
- CODE phase handoff(s): Pass the handoff summaries from coders for context on what was built
- Plan sections above (if any)
- "Reference the approved plan at `docs/plans/{slug}-plan.md` for full context."
- "You own ALL substantive testing: unit tests, integration, E2E, edge cases."

**Before completing**:
- [ ] All tests passing
- [ ] Specialist handoff received (see Handoff Format above)
- [ ] If blocker reported → `/PACT:imPACT`

---

## After All Phases Complete

> **S5 Policy Checkpoint (Pre-Merge)**: Before creating PR, verify: "Do all tests pass? Is system integrity maintained? Have S5 non-negotiables been respected throughout?"

1. **Update plan status** (if plan exists): IN_PROGRESS → IMPLEMENTED
2. **Run `/PACT:peer-review`** to commit, create PR, and get multi-agent review
3. **S4 Retrospective**: Briefly note—what worked well? What should we adapt for next time?
4. **High-variety audit trail** (variety 10+ only): Delegate to `pact-memory-agent` to save key orchestration decisions, S3/S4 tensions resolved, and lessons learned. This preserves the audit trail that formal decision logs previously provided.
