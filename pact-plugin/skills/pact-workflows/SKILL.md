---
name: pact-workflows
description: |
  PACT workflow family: orchestrate, comPACT, rePACT, imPACT, plan-mode, peer-review.
  Use when: Selecting which workflow to use, understanding workflow procedures.
  Triggers on: orchestrate, comPACT, rePACT, imPACT, plan-mode, peer-review, workflow selection
---

# PACT Workflow Family

## Workflow Selection

| Workflow | When to Use | Key Idea |
|----------|-------------|----------|
| **orchestrate** | Complex/greenfield work | Full P-A-C-T multi-agent cycle |
| **plan-mode** | Before complex work, need alignment | Multi-agent planning, no implementation |
| **comPACT** | Focused, single-domain tasks | Light ceremony, parallelizable |
| **rePACT** | Complex sub-tasks within orchestration | Nested P-A-C-T cycle |
| **imPACT** | When blocked | Triage: redo phase? add agents? |
| **peer-review** | After CODE phase complete | Multi-agent PR review |

**Decision tree**: Complex/multi-domain? Yes + need alignment → plan-mode then orchestrate. Yes alone → orchestrate. No + single domain → comPACT. No + multiple independent items → parallel comPACT.

---

## Phase Skip Rules

**CODE phase is NEVER skipped for application work.**

| Phase | Can Skip? | When |
|-------|-----------|------|
| PREPARE | Yes | Parent covered research, or task well-defined |
| ARCHITECT | Yes | Simple change, design exists, or parent designed it |
| **CODE** | **NEVER** | Application changes require specialist execution |
| TEST | Partial | Smoke tests required; comprehensive may follow |

---

## plan-mode

**Purpose**: Specialist perspectives before implementation. No code changes.

**Phases**: (1) Analyze scope, select specialists (2) Consult in parallel (3) Synthesize, resolve conflicts (4) Save to `docs/plans/`, await approval

**Rules**: No implementation, no git branch, specialists in "planning-only mode"

**After approval**: Run `/PACT:orchestrate` which references the plan.

---

## comPACT

**Purpose**: Single-domain delegation with light ceremony.

| Shorthand | Use For |
|-----------|---------|
| `backend` | Server-side logic, APIs |
| `frontend` | UI, React, client-side |
| `database` | Schema, queries, migrations |
| `prepare` | Research, requirements |
| `test` | Standalone test tasks |
| `architect` | Design guidance |

**Parallel**: Multiple independent items can invoke same specialist type in parallel.

**Light ceremony**: Work from task description, check docs/ briefly, smoke tests only.

**Escalate to orchestrate**: Task spans multiple domains or specialist hits blocker.

---

## rePACT

**Purpose**: Nested P-A-C-T cycle for complex sub-tasks within an orchestration.

**Single-domain**: `/PACT:rePACT backend "implement rate limiting"`
**Multi-domain**: `/PACT:rePACT "implement audit logging sub-system"`

**Constraints**: Max nesting 2 levels. No new branch/PR. Decision logs use `-nested` suffix.

**Phases** (mini-): Prepare → Architect → Code → Test → Integration

---

## imPACT

**Purpose**: Triage when blocked. Diagnose, don't fix.

**Two questions**: (1) Redo prior phase? (issue upstream) (2) Additional agents needed?

| Outcome | When | Action |
|---------|------|--------|
| Redo prior phase | Issue upstream | Re-delegate to redo |
| Augment present | Need help now | Add parallel agents |
| Invoke rePACT | Sub-task too complex | Nested cycle |
| Not blocked | Neither "Yes" | Continue with guidance |
| Escalate to user | 3+ imPACT cycles | Systemic issue |

**Key principle**: Knowing the fix does not equal permission to implement. Delegate.

---

## peer-review

**Purpose**: Multi-agent PR review after CODE phase.

**Invoke 3+ agents in parallel**: pact-architect (design), pact-test-engineer (coverage), domain coder (implementation quality based on PR focus)

**After reviews**: Synthesize findings, note agreements and conflicts.

---

## Escalation Heuristics

| Situation | Workflow |
|-----------|----------|
| Trivial/single-domain | comPACT |
| Multi-domain feature | orchestrate |
| Need user alignment | plan-mode first |
| Complex sub-task emerges | rePACT |
| Agent reports blocker | imPACT to triage |
| 3+ imPACT without resolution | Escalate to user |
