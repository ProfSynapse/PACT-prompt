# PACT Protocols (Lean Reference)

> **Purpose**: Minimal protocols for PACT workflows. Agents reference this when needed, not memorized.
>
> **Design principle**: One-liners in prompts, details here.

---

## The PACT Workflow Family

| Workflow | When to Use | Key Idea |
|----------|-------------|----------|
| **PACT** | Complex/greenfield work | Multi-agent orchestration with formal handoffs |
| **plan-mode** | Before complex work, need alignment | Multi-agent planning consultation, no implementation |
| **comPACT** | Focused, single-domain tasks | Single-specialist delegation with light ceremony |
| **imPACT** | When blocked or need to iterate | Triage: Redo prior phase? Additional agents needed? |

---

## plan-mode Protocol

**Purpose**: Multi-agent planning consultation before implementation. Get specialist perspectives synthesized into an actionable plan.

**When to use**:
- Complex features where upfront alignment prevents rework
- Tasks spanning multiple specialist domains
- When you want user approval before implementation begins
- Greenfield work with significant architectural decisions

**Four phases**:

| Phase | What Happens |
|-------|--------------|
| 0. Analyze | Orchestrator assesses scope, selects relevant specialists |
| 1. Consult | Specialists provide planning perspectives in parallel |
| 2. Synthesize | Orchestrator resolves conflicts, sequences work, assesses risk |
| 3. Present | Save plan to `docs/plans/`, present to user, await approval |

**Key rules**:
- **No implementation** — planning consultation only
- **No git branch** — that happens when `/PACT:orchestrate` runs
- Specialists operate in "planning-only mode" (analysis, not action)
- Conflicts surfaced and resolved (or flagged for user decision)

**Output**: `docs/plans/{feature-slug}-plan.md`

**After approval**: User runs `/PACT:orchestrate {task}`, which references the plan.

**When to recommend alternatives**:
- Trivial task → `/PACT:comPACT`
- Unclear requirements → Ask clarifying questions first
- Need research before planning → Run preparation phase alone first

---

## imPACT Protocol

**Trigger when**: Blocked; get similar errors repeatedly; or prior phase output is wrong.

**Two questions**:
1. **Redo prior phase?** — Is the issue upstream in P→A→C→T?
2. **Additional agents needed?** — Do I need subagents to assist?

**Three outcomes**:
| Outcome | When | Action |
|---------|------|--------|
| Redo solo | Prior phase broken, I can fix it | Loop back and fix yourself |
| Redo with help | Prior phase broken, need specialist | Loop back with subagent assistance |
| Proceed with help | Current phase correct, blocked on execution | Invoke subagents to help forward |

If neither question is "Yes," you're not blocked—continue.

---

## comPACT Protocol

**Core idea**: Single-specialist delegation with light ceremony.

comPACT invokes exactly ONE specialist based on the task domain. No doc artifacts, no multi-phase orchestration—just focused work.

**Available specialists**:
| Shorthand | Specialist | Use For |
|-----------|------------|---------|
| `backend` | pact-backend-coder | Server-side logic, APIs, middleware |
| `frontend` | pact-frontend-coder | UI, client-side |
| `database` | pact-database-engineer | Schema, queries, migrations |
| `prepare` | pact-preparer | Research, requirements |
| `test` | pact-test-engineer | Standalone test tasks |
| `architect` | pact-architect | Design patterns, structure advice, architectural questions |

**Smart specialist selection**:
- *Clear task* → Auto-select (domain keywords, file types, single-domain action)
- *Ambiguous task* → Ask user which specialist

**Light ceremony instructions** (injected when invoking specialist):
- Work directly from task description
- Check docs/plans/, docs/preparation/, docs/architecture/ briefly if they exist—reference relevant context
- Do not create new documentation artifacts
- Unit tests: Required for logic changes; optional for trivial changes (documentation, comments, config)

**Escalate to `/PACT:orchestrate` when**:
- Task spans multiple specialist domains
- Specialist reports a blocker (run `/PACT:imPACT` first)

**If blocker reported**:
1. Receive blocker from specialist
2. Run `/PACT:imPACT` to triage
3. May escalate to `/PACT:orchestrate` if task exceeds single-specialist scope

---

## Phase Handoffs

**On completing any phase, state**:
1. What you produced (with file paths)
2. Key decisions made
3. What the next agent needs to know

Keep it brief. No templates required.

---

## Backend ↔ Database Boundary

**Sequence**: Database delivers schema → Backend implements ORM.

| Database Engineer Owns | Backend Engineer Owns |
|------------------------|----------------------|
| Schema design, DDL | ORM models |
| Migrations | Repository/DAL layer |
| Complex SQL queries | Application queries via ORM |
| Indexes | Connection pooling |

**Collaboration**: If Backend needs a complex query, ask Database. If Database needs to know access patterns, ask Backend.

---

## Test Engagement

| Test Type | Owner |
|-----------|-------|
| Unit tests | Coders (part of "done") |
| Integration tests | Test Engineer |
| E2E tests | Test Engineer |

**Coders**: Your work isn't done until unit tests pass.

**Test Engineer**: Engage after Code phase. Route failures back to relevant coder.

---

## Cross-Cutting Concerns

Before completing any phase, consider:
- **Security**: Input validation, auth, data protection
- **Performance**: Query efficiency, caching
- **Accessibility**: WCAG, keyboard nav (frontend)
- **Observability**: Logging, error tracking

Not a checklist—just awareness.

---

## Architecture Review (Optional)

For complex features, before Code phase:
- Coders quickly validate architect's design is implementable
- Flag blockers early, not during implementation

Skip for simple features or when "just build it."

---

## Documentation Locations

| Phase | Output Location |
|-------|-----------------|
| Plan | `docs/plans/` |
| Prepare | `docs/preparation/` |
| Architect | `docs/architecture/` |
| Code | `docs/codebase/` |
| Test | `docs/testing/` |
| Decisions | `docs/decisions/` |
| Iterations | `docs/impact/` |

**Plan vs. Architecture artifacts**:
- **Plans** (`docs/plans/`): Pre-approval roadmaps created by `/PACT:plan-mode`. Multi-specialist consultation synthesized into scope estimates, sequencing, and risk assessment. Created *before* implementation begins.
- **Architecture** (`docs/architecture/`): Formal specifications created by `pact-architect` *during* the Architect phase of `/PACT:orchestrate`. Detailed component designs, interface contracts, and technical decisions.

Plans inform implementation strategy; architecture documents define the technical blueprint.

---

## Session Continuity

If work spans sessions, update CLAUDE.md with:
- Current phase and task
- Blockers or open questions
- Next steps

---

## Related

- Agent definitions: `.claude/agents/`
- Commands: `.claude/commands/PACT/`
