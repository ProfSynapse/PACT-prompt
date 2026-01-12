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

Algedonic signals are emergency escalations that bypass normal triage. Any agent can emit them when they recognize viability threats. You **MUST** surface them to the user immediately.

### HALT Signal Response

When you receive a HALT signal (SECURITY, DATA, or ETHICS category):

1. **Stop ALL agents immediately** — no exceptions
2. **Present signal to user** with full context:
   ```
   ⚠️ ALGEDONIC HALT: {Category}

   Issue: {from signal}
   Evidence: {from signal}
   Impact: {from signal}

   All work has stopped. Please acknowledge before we can proceed.
   Options: [Acknowledged, investigate] / [Override, continue anyway (requires justification)]
   ```
3. **Do NOT resume** until user explicitly acknowledges
4. **Log** the halt in session notes

### ALERT Signal Response

When you receive an ALERT signal (QUALITY, SCOPE, or META-BLOCK category):

1. **Pause current phase** — don't stop everything, but pause active work
2. **Present signal to user** with options:
   ```
   ⚠️ ALGEDONIC ALERT: {Category}

   Issue: {from signal}
   Evidence: {from signal}

   Options: [Investigate further] / [Continue with caution] / [Stop work]
   ```
3. **Await user decision** before proceeding
4. **Log** the alert and user's decision

### Algedonic vs imPACT

| Signal Type | Protocol | When |
|-------------|----------|------|
| Operational blocker | `/PACT:imPACT` | "How do we proceed?" |
| Viability threat | Algedonic | "Should we proceed at all?" |

If you're unsure whether something is an operational blocker or viability threat, err on the side of algedonic (safer).

See `protocols/algedonic.md` for full protocol and trigger conditions.

---

## Before Starting

### Task Variety Assessment

Before running orchestration, assess task variety using the protocol in `pact-protocols.md > Variety Management`.

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
| **TEST** | Integration/E2E tests needed, complex component interactions, security/performance verification | Unit tests from coders sufficient, no integration boundaries crossed, isolated change |

**Conflict resolution**: When both "Run if" and "Skip if" criteria apply, **run the phase** (safer default). Example: A plan exists but requirements have changed—run PREPARE to validate.

**Plan-aware fast path**: When an approved plan exists in `docs/plans/`, PREPARE and ARCHITECT are typically skippable—the plan already synthesized specialist perspectives. Skip unless scope has changed or plan appears stale (typically >2 weeks; ask user to confirm if uncertain).

**State your assessment before proceeding.** For each skipped phase, state:
1. Which skip criterion was met
2. The context source (plan path, doc path, or pattern name)

Example:

> "Approved plan found at `docs/plans/user-auth-jwt-plan.md`. Skipping PREPARE (plan has Preparation Phase section). Skipping ARCHITECT (plan has Architecture Phase section). Running CODE. Running TEST (plan specifies integration tests needed)."

Or without a plan:

> "No plan found. Running PREPARE (external API needs research). Skipping ARCHITECT (following established repository pattern in `src/repositories/`). Running CODE. Skipping TEST (isolated change, unit tests sufficient)."

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

Each specialist should end with a structured handoff (2-4 sentences):

```
**Handoff**:
1. Produced: [files created/modified, key artifacts]
2. Key context for next phase: [decisions made, patterns established, constraints discovered]
3. Open questions (if any): [uncertainties for next phase to resolve or confirm]
4. Decisions made (if phases skipped): [moderate decisions with rationale—for orchestrator validation]
```

**Examples**:

> **Handoff**: 1. Produced: `docs/preparation/rate-limiting-research.md` covering token bucket vs sliding window algorithms. 2. Key context: Recommended Redis-based token bucket; existing `redis-client.ts` can be reused. 3. Open questions: Should rate limits be per-user or per-API-key?

> **Handoff**: 1. Produced: `src/middleware/rateLimiter.ts`, `src/config/rateLimits.ts`, unit tests passing. 2. Key context: Used token bucket with Redis; added `X-RateLimit-*` headers per RFC 6585. 3. Open questions: None—ready for integration testing. 4. Decisions made: Chose `X-RateLimit-Remaining` header format (moderate—affects API consumers); rationale: follows RFC 6585 standard.

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

#### Execution Strategy Analysis

Before invoking coders, analyze dependencies and justify your execution strategy.

**How to analyze:**
- Review the plan's implementation details and file paths mentioned
- If no plan exists, analyze the task description and examine relevant files directly
- Check if tasks reference or modify the same files/modules
- Examine import relationships between components

**Analysis steps:**
1. **Map file-level dependencies**: Which tasks touch the same files?
2. **Map import dependencies**: Does one task's output feed another's input?
3. **Identify parallelizable groups**: Independent tasks with no shared files

**Required**: State your execution strategy with specific reasoning:
- "Parallel because [specific files/components are independent]"
- "Sequential because [specific dependency or shared file]"
- "Mixed: [A, B] in parallel, then C (depends on A's output)"

> **"I'm not sure"** and **"the plan lists them in order"** are **not valid justifications**. Complete your analysis until you can make a definitive choice.

**If analysis is genuinely inconclusive**: Consult the architect's outputs in `docs/architecture/`, invoke pact-architect for clarification, or escalate to user. Do not default to either strategy without articulated reasoning.

#### Parallel vs Sequential Examples

Use these to inform your analysis (not as complete decision criteria):

**Parallel-safe** (when analysis confirms independence):
- Backend API + Frontend UI for same feature (no shared files)
- Multiple independent components in same domain (no shared files)
- Backend + Frontend when API contract is already defined

**Sequential-required** (when analysis finds dependencies):
- Database schema → Backend (backend needs schema to build models/queries)
- Backend API → Frontend (frontend needs API contract to consume)
- Shared utility/service → consumers of that utility
- Any work where one task's output is another's input
- Any tasks that modify the same file

**Mixed** (partial parallelization):
- When some tasks are independent but others depend on their output
- Group independent tasks for parallel execution, then sequence dependent groups
- Example: "A and B in parallel, then C (depends on both outputs)"

#### S2 Pre-Parallel Coordination Check

Once you've decided on parallel execution, apply S2 Coordination:

1. **Identify potential conflicts**:
   - Shared files (merge conflict risk)
   - Shared interfaces (API contract disagreements)
   - Shared state (database schemas, config)

2. **If conflicts exist**:
   - Sequence those agents instead, OR
   - Assign clear file/component boundaries to each agent

3. **Establish resolution authority**:
   - Technical disagreements → Architect arbitrates
   - Style/convention → First agent's choice becomes standard

**Include in parallel agent prompts**: "You are working in parallel with [other agent(s)]. Your scope is [specific files/components]. Do not modify files outside your scope. If you need changes outside your scope, report as a blocker."

See `pact-protocols.md > S2 Coordination Layer` for full protocol.

#### Optional: S3* Parallel Audit During CODE

For high-risk work, invoke test engineer in parallel with coders to catch issues early.

**Trigger conditions** (invoke parallel audit when ANY apply):
- Security-sensitive code (auth, payments, PII handling)
- Complex multi-component integration
- Novel patterns or first-time approaches
- User explicitly requests monitoring ("watch this closely")

**Invoke test engineer in audit mode with**:
```
AUDIT MODE: Review {scope} for testability and early risks.
Emit signals (🟢/🟡/🔴) as you observe. Do not block coders.
You are READ-ONLY on source files.
```

**Handling audit signals**:

| Signal | Meaning | Response |
|--------|---------|----------|
| 🟢 GREEN | No concerns | Continue normally |
| 🟡 YELLOW | Concerns noted | Log for TEST phase, continue |
| 🔴 RED | Critical issue | Pause affected coder(s), run `/PACT:imPACT` with signal |

**If 🔴 RED signal received**:
1. Immediately pause the affected coder(s)
2. Run `/PACT:imPACT` with the RED signal details as input
3. imPACT triages: fix now, redo phase, or escalate
4. Resume CODE only after resolution

See `pact-protocols.md > S3* Continuous Audit` for full protocol.

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
- [ ] Decision log(s) created at `docs/decision-logs/{feature}-{domain}.md`
- [ ] Specialist handoff(s) received (see Handoff Format above)
- [ ] If blocker reported → `/PACT:imPACT`

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
- Sub-task is large enough to warrant its own decision log

**Example:**
During CODE phase for "user authentication," you realize "OAuth2 token refresh" is complex enough to need its own design:
```
/PACT:rePACT backend "implement OAuth2 token refresh mechanism"
```

This runs a nested P→A→C→T cycle, staying on the current branch, producing a `-nested` decision log.

**For multi-domain sub-tasks:**
```
/PACT:rePACT "implement audit logging sub-system"
```

This runs a mini-orchestration for the sub-task, invoking relevant specialists across domains.

---

### Phase 4: TEST → `pact-test-engineer`

**Skip criteria met?** → Proceed to "After All Phases Complete."

**Plan sections to pass** (if plan exists):
- "Test Phase"
- "Test Scenarios"
- "Coverage Targets"

**Invoke `pact-test-engineer` with**:
- Task description
- Decision log(s) from CODE phase: "Read the implementation decision log(s) at `docs/decision-logs/{feature}-*.md` for context on what was built, key decisions, assumptions, and areas of uncertainty."
- Plan sections above (if any)
- "Reference the approved plan at `docs/plans/{slug}-plan.md` for full context."
- "You own ALL substantive testing: unit tests, integration, E2E, edge cases. The decision log provides context—you decide what and how to test."

**Before completing**:
- [ ] Outputs exist in `docs/testing/`
- [ ] All tests passing
- [ ] Test decision log created at `docs/decision-logs/{feature}-test.md`
- [ ] Specialist handoff received (see Handoff Format above)
- [ ] If blocker reported → `/PACT:imPACT`

---

## After All Phases Complete

> **S5 Policy Checkpoint (Pre-Merge)**: Before creating PR, verify: "Do all tests pass? Is system integrity maintained? Have S5 non-negotiables been respected throughout?"

1. **Update plan status** (if plan exists): IN_PROGRESS → IMPLEMENTED
2. **Run `/PACT:peer-review`** to commit, create PR, and get multi-agent review
3. **S4 Retrospective**: Briefly note—what worked well? What should we adapt for next time?
