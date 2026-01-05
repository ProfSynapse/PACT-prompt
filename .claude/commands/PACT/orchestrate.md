---
description: Delegate a task to PACT specialist agents
argument-hint: [e.g., implement feature X]
---
Orchestrate specialist PACT agents through the PACT workflow to address: $ARGUMENTS

## Before Starting

### Task Complexity Check

Before running full PACT orchestration, evaluate task complexity:

**Simple or borderline task (ask user):**
- Single file or component mentioned
- Bug fix in one domain
- Clear single-domain keywords (React, Express, PostgreSQL, Jest, etc.)
- Small feature with unclear scope
- Refactor that might be contained
- → Use `AskUserQuestion` tool:
  - Question: "This looks like it could be handled by a single specialist. Would you like to run comPACT instead?"
  - Options: "Yes, use comPACT" / "No, proceed with full orchestration"
- If comPACT → redirect to `/PACT:comPACT`
- If orchestrate → proceed with full PACT phases below

**Complex task (proceed with orchestrate):**
- Multiple domains mentioned
- "New feature" or greenfield language
- Architectural decisions required
- → Proceed with full PACT phases

---

1. **Create feature branch** if not already on one
2. **Check for plan** in `docs/plans/` matching this task
3. **Check for progress** in `docs/progress/` matching this task

### Progress File Handling

If a progress file exists, incremental orchestration was started previously:

| Progress State | Action |
|----------------|--------|
| All sub-features ✅ Completed | Work already done—confirm with user before re-running |
| Some sub-features 🔄 In Progress or ⏳ Pending | Ask: "Resume from sub-feature X?" or "Start fresh?" |
| No progress file | Proceed normally |

When resuming:
- Read "Established Context" section for patterns/decisions from prior sub-features
- Skip to the first incomplete sub-feature
- Context from completed sub-features informs phase-skipping

### Plan Status Handling

| Status | Action |
|--------|--------|
| PENDING APPROVAL | `/PACT:orchestrate` = implicit approval → update to IN_PROGRESS |
| APPROVED | Update to IN_PROGRESS |
| BLOCKED | Ask user to resolve or proceed without plan |
| IN_PROGRESS | Confirm: continue or restart? |
| SUPERSEDED/IMPLEMENTED | Confirm with user before proceeding |
| No plan found | Proceed—phases will do full discovery |

### Large Feature Handling

For features with multiple implementation phases (identified in plan or by scope):

**Option 1: Single orchestration** (default)
- Run all phases once
- Single PR with all changes
- Best for: cohesive features, moderate scope

**Option 2: Incremental orchestration** (for large features)
- Break into sub-features based on plan's "Implementation Sequence" or logical boundaries
- Each sub-feature gets its own orchestration cycle:
  1. Orchestrate sub-feature 1 → test → commit
  2. Orchestrate sub-feature 2 → test → commit
  3. ...continue...
  4. Final `/PACT:peer-review` covers all commits
- Context carries forward: later sub-features can skip PREPARE/ARCHITECT if earlier ones established patterns
- Best for: large features, multiple independent components, risk mitigation

**How to break up work**:
1. **Present proposed breakdown** before starting: list sub-features with brief scope
2. Each sub-feature should be:
   - A meaningful, testable unit (not arbitrary chunks)
   - Mappable to 1-3 logical commits
   - Completable without depending on unfinished sub-features
3. Suggested breakdown patterns:
   - By layer: database → backend → frontend
   - By component: auth module → user profile → dashboard
   - By user flow: registration → login → password reset
4. Get user confirmation on breakdown before proceeding

**When to suggest incremental orchestration**:
- Plan identifies 3+ distinct implementation phases
- Feature touches 3+ separate domains
- Estimated scope is "High" or "Very High"
- User explicitly requests phased delivery

Ask the user: "This is a large feature. Would you prefer single orchestration or incremental (sub-feature by sub-feature)?"

**Tracking incremental progress**:

When incremental orchestration is chosen, create a progress file at `docs/progress/{feature-slug}-progress.md`:

```markdown
# Progress: {Feature Name}

> Tracking incremental orchestration for: {task description}
> Plan: `docs/plans/{slug}-plan.md` (if exists, otherwise "None")
> Started: {YYYY-MM-DD}

## Sub-feature Breakdown

| # | Sub-feature | Status | Commits | Context Established |
|---|-------------|--------|---------|---------------------|
| 1 | Database schema | ✅ Completed | `abc123` | User table, session table, indexes |
| 2 | Backend auth API | 🔄 In Progress | — | — |
| 3 | Frontend login UI | ⏳ Pending | — | — |

**Current**: Sub-feature 2 of 3
**Last updated**: {YYYY-MM-DD}

## Established Context

Patterns and decisions from completed sub-features that inform remaining work:
- User table uses UUID primary keys (established in sub-feature 1)
- Auth follows JWT pattern with refresh tokens (established in sub-feature 2)
```

**After each sub-feature completes**:
1. Update status: ⏳ Pending → 🔄 In Progress → ✅ Completed
2. Record commit hash(es)
3. Add key context to "Established Context" section
4. This context informs phase-skipping for subsequent sub-features

**Cross-session continuity**: The progress file tells the next session exactly where to resume and what context has been established.

---

## Context Assessment

Before executing phases, assess which are needed based on existing context:

| Phase | Run if... | Skip if... |
|-------|-----------|------------|
| **PREPARE** | Requirements unclear, external APIs to research, dependencies unmapped | Approved plan exists with Preparation Phase section, OR requirements explicit in task, OR existing `docs/preparation/` covers scope |
| **ARCHITECT** | New component or module, interface contracts undefined, architectural decisions required | Approved plan exists with Architecture Phase section, OR following established patterns, OR `docs/architecture/` covers design |
| **CODE** | Always run | Never skip |
| **TEST** | Integration/E2E tests needed, complex component interactions, security/performance verification | Unit tests from coders sufficient, no integration boundaries crossed, isolated change |

**Plan-aware fast path**: When an approved plan exists in `docs/plans/`, PREPARE and ARCHITECT are typically skippable—the plan already synthesized specialist perspectives. Skip unless scope has changed or plan is stale (>2 weeks old).

**State your assessment before proceeding.** Example:

> "Approved plan found at `docs/plans/user-auth-jwt-plan.md`. Skipping PREPARE and ARCHITECT (plan covers both). Running CODE. Running TEST (plan specifies integration tests needed)."

Or without a plan:

> "No plan found. Running PREPARE (external API needs research). Skipping ARCHITECT (following existing patterns). Running CODE. Skipping TEST (unit tests sufficient)."

The user can override your assessment if they want more or less ceremony.

---

## Handling Decisions When Phases Were Skipped

When a phase is skipped but a coder encounters a decision that would have been handled by that phase:

| Decision Scope | Examples | Action |
|----------------|----------|--------|
| **Minor** | Naming conventions, local file structure, error message wording | Coder decides, documents in commit message |
| **Moderate** | Interface shape, error handling pattern, component boundaries | Coder proposes in handoff; orchestrator confirms or escalates |
| **Major** | New component needed, cross-boundary contract, architectural pattern choice | Blocker → `/PACT:imPACT` → may need to run skipped phase |

**Coder instruction when phases were skipped**:

> "PREPARE and/or ARCHITECT were skipped based on existing context. If you encounter a decision that feels architectural or requires research beyond your immediate scope, note it in your handoff rather than blocking. Minor decisions (naming, local structure) are yours to make. Major decisions that affect other components should be flagged."

This prevents excessive ping-pong for small decisions while catching real issues.

---

## Handoff Format

Each specialist should end with a structured handoff (2-4 sentences):

```
**Handoff**:
1. Produced: [files created/modified, key artifacts]
2. Key context for next phase: [decisions made, patterns established, constraints discovered]
3. Open questions (if any): [uncertainties for next phase to resolve or confirm]
```

**Examples**:

> **Handoff**: 1. Produced: `docs/preparation/rate-limiting-research.md` covering token bucket vs sliding window algorithms. 2. Key context: Recommended Redis-based token bucket; existing `redis-client.ts` can be reused. 3. Open questions: Should rate limits be per-user or per-API-key?

> **Handoff**: 1. Produced: `src/middleware/rateLimiter.ts`, `src/config/rateLimits.ts`, unit tests passing. 2. Key context: Used token bucket with Redis; added `X-RateLimit-*` headers per RFC 6585. 3. Open questions: None—ready for integration testing.

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

### Phase 2: ARCHITECT → `pact-architect`

**Skip criteria met?** → Proceed to Phase 3.

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

**Plan sections to pass** (if plan exists):
- "Code Phase"
- "Implementation Sequence"
- "Commit Sequence"

**Select coder(s)** based on scope:
- `pact-backend-coder` — server-side logic, APIs
- `pact-frontend-coder` — UI, client-side
- `pact-database-engineer` — schema, queries, migrations

#### Parallel vs Sequential Invocation

**Parallel-safe** (invoke together):
- Backend API + Frontend UI for same feature (independent implementation)
- Multiple independent components in same domain
- Backend + Frontend when API contract is already defined

**Sequential required** (wait for handoff):
- Database schema → Backend (backend needs schema to build models/queries)
- Backend API → Frontend (frontend needs API contract to consume)
- Shared utility/service → consumers of that utility
- Any work where one coder's output is another's input

**When in doubt**: Sequential is safer. Parallel saves time but risks rework if assumptions diverge.

**Invoke coder(s) with**:
- Task description
- ARCHITECT phase outputs (or plan's Architecture Phase if ARCHITECT was skipped)
- Plan sections above (if any)
- "Reference the approved plan at `docs/plans/{slug}-plan.md` for full context."
- If PREPARE/ARCHITECT were skipped, include: "PREPARE and/or ARCHITECT were skipped based on existing context. Minor decisions (naming, local structure) are yours to make. Moderate decisions (interface shape, error patterns) should be proposed in your handoff. Major decisions affecting other components are blockers."

**Before next phase**:
- [ ] Implementation complete
- [ ] Unit tests passing
- [ ] Specialist handoff(s) received (see Handoff Format above)
- [ ] If blocker reported → `/PACT:imPACT`

---

### Phase 4: TEST → `pact-test-engineer`

**Skip criteria met?** → Proceed to "After All Phases Complete."

**Plan sections to pass** (if plan exists):
- "Test Phase"
- "Test Scenarios"
- "Coverage Targets"

**Invoke `pact-test-engineer` with**:
- Task description
- Implementation details from CODE phase
- Plan sections above (if any)
- "Reference the approved plan at `docs/plans/{slug}-plan.md` for full context."

**Before completing**:
- [ ] Outputs exist in `docs/testing/`
- [ ] All tests passing
- [ ] Specialist handoff received (see Handoff Format above)
- [ ] If blocker reported → `/PACT:imPACT`

---

## After All Phases Complete

1. **Update plan status** (if plan exists): IN_PROGRESS → IMPLEMENTED
2. **Run `/PACT:peer-review`** to commit, create PR, and get multi-agent review
