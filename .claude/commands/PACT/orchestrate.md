---
description: Delegate a task to PACT specialist agents
argument-hint: [e.g., implement feature X]
---
Orchestrate specialist PACT agents through the PACT workflow to address: $ARGUMENTS

## Before Starting

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

## Phase Execution

⚠️ **MANDATORY: Execute ALL four phases in sequence. Never skip phases, even with a plan.**

Plans are roadmaps from planning-only consultation. Each phase produces its own detailed, implementation-ready artifacts. A plan accelerates phases; it does not replace them.

---

### Phase 1: PREPARE → `pact-preparer`

**Plan sections to pass** (if plan exists):
- "Preparation Phase"
- "Open Questions > Require Further Research"

**Invoke `pact-preparer` with**:
- Task description
- Plan sections above (if any)
- "Reference the approved plan at `docs/plans/{slug}-plan.md` for full context."

**Before next phase**:
- [ ] Outputs exist in `docs/preparation/`
- [ ] Specialist handoff received
- [ ] If blocker reported → `/PACT:imPACT`

---

### Phase 2: ARCHITECT → `pact-architect`

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
- [ ] Specialist handoff received
- [ ] If blocker reported → `/PACT:imPACT`

---

### Phase 3: CODE → `pact-*-coder(s)`

**Plan sections to pass** (if plan exists):
- "Code Phase"
- "Implementation Sequence"
- "Commit Sequence"

**Select coder(s)** based on scope:
- `pact-backend-coder` — server-side logic, APIs
- `pact-frontend-coder` — UI, client-side
- `pact-database-engineer` — schema, queries, migrations

Invoke multiple coders in parallel for non-conflicting work.

**Invoke coder(s) with**:
- Task description
- ARCHITECT phase outputs
- Plan sections above (if any)
- "Reference the approved plan at `docs/plans/{slug}-plan.md` for full context."

**Before next phase**:
- [ ] Implementation complete
- [ ] Unit tests passing
- [ ] Specialist handoff(s) received
- [ ] If blocker reported → `/PACT:imPACT`

---

### Phase 4: TEST → `pact-test-engineer`

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
- [ ] Specialist handoff received
- [ ] If blocker reported → `/PACT:imPACT`

---

## After All Phases Complete

1. **Update plan status** (if plan exists): IN_PROGRESS → IMPLEMENTED
2. **Run `/PACT:peer-review`** to commit, create PR, and get multi-agent review
