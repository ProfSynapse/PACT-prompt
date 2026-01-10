# PACT Protocols (Lean Reference)

> **Purpose**: Minimal protocols for PACT workflows. Agents reference this when needed, not memorized.
>
> **Design principle**: One-liners in prompts, details here.
>
> **Theoretical basis**: Structure informed by Stafford Beer's Viable System Model (VSM). See `docs/preparation/vsm-glossary.md` for full terminology.
>
> **VSM Quick Reference**: S1=Operations (specialists), S2=Coordination (conflict resolution), S3=Control (orchestrator execution), S4=Intelligence (planning/adaptation), S5=Policy (governance/user authority).

---

## S5 Policy Layer (Governance)

The policy layer defines non-negotiable constraints and provides escalation authority. All other protocols operate within these boundaries.

### Non-Negotiables (SACROSANCT)

These rules are **never** overridden by operational pressure:

| Category | Rule | Rationale |
|----------|------|-----------|
| **Security** | No credentials in code; validate all inputs; sanitize outputs | Prevents breaches, injection attacks |
| **Quality** | No known-broken code merged; tests must pass | Maintains system integrity |
| **Ethics** | No deceptive outputs; no harmful content | Aligns with responsible AI principles |
| **Delegation** | Orchestrator never writes application code | Maintains role boundaries |

**If a rule would be violated**: Stop work, report to user. These are not trade-offs—they are boundaries.

### Policy Checkpoints

At defined points, verify alignment with project principles:

| Checkpoint | When | Question |
|------------|------|----------|
| **Pre-CODE** | Before CODE phase begins | "Does the architecture align with project principles?" |
| **Pre-Merge** | Before creating PR | "Does this maintain system integrity? Are tests passing?" |
| **On Conflict** | When specialists disagree | "What do project values dictate?" |
| **On Blocker** | When normal flow can't proceed | "Is this an operational issue (imPACT) or viability threat (escalate to user)?" |

### S5 Authority

The **user is ultimate S5**. When conflicts cannot be resolved at lower levels:
- S3/S4 tension (execution vs adaptation) → Escalate to user
- Principle conflicts → Escalate to user
- Unclear non-negotiable boundaries → Escalate to user

The orchestrator has authority to make operational decisions within policy. It does not have authority to override policy.

---

## S2 Coordination Layer

The coordination layer enables parallel agent operation without conflicts. Apply these protocols whenever multiple agents work concurrently.

### Pre-Parallel Coordination Check

Before invoking parallel agents, the orchestrator must:

1. **Identify potential conflicts**:
   - Shared files (merge conflict risk)
   - Shared interfaces (API contract disagreements)
   - Shared state (database schemas, config, environment)

2. **Define boundaries or sequencing**:
   - If conflicts exist, either sequence the work or assign clear file/component boundaries
   - If no conflicts, proceed with parallel invocation

3. **Establish resolution authority**:
   - Technical disagreements → Architect arbitrates
   - Style/convention disagreements → First agent's choice becomes standard
   - Resource contention → Orchestrator allocates

### Conflict Resolution

| Conflict Type | Resolution |
|---------------|------------|
| Same file | Sequence agents OR assign clear section boundaries |
| Interface disagreement | Architect arbitrates; document decision |
| Naming/convention | First agent's choice becomes standard for the batch |
| Resource contention | Orchestrator allocates; others wait or work on different tasks |

### Shared Language

All agents operating in parallel must:
- Use project glossary and established terminology
- Follow consistent decision log format (see CODE → TEST Handoff)
- Use standardized handoff structure (see Phase Handoffs)

### Oscillation Dampening

If agents produce contradictory outputs (each "fixing" the other's work):

1. **Pause** both agents immediately
2. **Identify** the root disagreement (technical approach? requirements interpretation?)
3. **Escalate** to appropriate authority:
   - Technical disagreement → Architect
   - Requirements disagreement → User (S5)
4. **Resume** only after resolution is documented

---

## S1 Autonomy & Recursion

Specialists (S1) have bounded autonomy to adapt within their domain. This section defines those boundaries and enables recursive PACT cycles for complex sub-tasks.

### Autonomy Charter

All specialists have authority to:
- **Adjust implementation approach** based on discoveries during work
- **Request context** from other specialists via the orchestrator
- **Recommend scope changes** when task complexity differs from estimate
- **Apply domain expertise** without micro-management from orchestrator

All specialists must escalate when:
- **Discovery contradicts architecture** — findings invalidate the design
- **Scope change exceeds 20%** — significantly more/less work than expected
- **Security/policy implications emerge** — potential S5 violations discovered
- **Cross-domain dependency** — need changes in another specialist's area

### Self-Coordination

When working in parallel (see S2 Coordination):
- Check S2 protocols before starting if multiple agents are active
- Respect assigned file/component boundaries
- First agent's conventions become standard for the batch
- Report potential conflicts to orchestrator immediately

### Recursive PACT (Nested Cycles)

When a sub-task is complex enough to warrant its own PACT treatment:

**Recognition Indicators:**
- Sub-task spans multiple concerns within your domain
- Sub-task has its own uncertainty requiring research
- Sub-task output feeds multiple downstream consumers
- Sub-task could benefit from its own prepare/architect/code/test cycle

**Protocol:**
1. **Declare**: "Invoking nested PACT for {sub-task}"
2. **Execute**: Run mini-PACT cycle (may skip phases if not needed)
3. **Integrate**: Merge results back to parent task
4. **Report**: Include nested work in handoff to orchestrator

**Constraints:**
- **Nesting limit**: 2 levels maximum (prevent infinite recursion)
- **Scope check**: Nested PACT must be within your domain; cross-domain needs escalate to orchestrator
- **Documentation**: Nested cycles produce their own decision logs (append `-nested` to filename)

**Example:**
```
Parent task: "Implement user authentication service"
Nested PACT: "Research and implement OAuth2 token refresh mechanism"
  - Mini-Prepare: Research OAuth2 refresh token best practices
  - Mini-Architect: Design token storage and refresh flow
  - Mini-Code: Implement the mechanism
  - Mini-Test: Smoke test the refresh flow
```

---

## The PACT Workflow Family

| Workflow | When to Use | Key Idea |
|----------|-------------|----------|
| **PACT** | Complex/greenfield work | Context-aware multi-agent orchestration |
| **plan-mode** | Before complex work, need alignment | Multi-agent planning consultation, no implementation |
| **comPACT** | Focused, single-domain tasks | Single-domain delegation with light ceremony (parallelizable) |
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

**Core idea**: Single-DOMAIN delegation with light ceremony.

comPACT handles tasks within ONE specialist domain. For independent sub-tasks, it can invoke MULTIPLE specialists of the same type in parallel.

**Available specialists**:
| Shorthand | Specialist | Use For |
|-----------|------------|---------|
| `backend` | pact-backend-coder | Server-side logic, APIs, middleware |
| `frontend` | pact-frontend-coder | UI, React, client-side |
| `database` | pact-database-engineer | Schema, queries, migrations |
| `prepare` | pact-preparer | Research, requirements |
| `test` | pact-test-engineer | Standalone test tasks |
| `architect` | pact-architect | Design guidance, pattern selection |

**Smart specialist selection**:
- *Clear task* → Auto-select (domain keywords, file types, single-domain action)
- *Ambiguous task* → Ask user which specialist

### When to Parallelize (Same-Domain)

Invoke multiple specialists of the same type when:
- Multiple independent items (bugs, components, endpoints)
- No shared files between sub-tasks
- Same patterns/conventions apply to all

| Task | Agents Invoked |
|------|----------------|
| "Fix 3 backend bugs" | 3 backend-coders (parallel) |
| "Add validation to 5 endpoints" | Multiple backend-coders (parallel) |
| "Update styling on 3 components" | Multiple frontend-coders (parallel) |

### S2 Light Coordination (for parallel comPACT)

Before parallel invocation within a domain:
1. **Check for conflicts** — Do any sub-tasks touch the same files?
2. **Assign boundaries** — If conflicts exist, sequence or define clear boundaries
3. **Set convention authority** — First agent's choices become standard for the batch

### Light ceremony instructions (injected when invoking specialist)

- Work directly from task description
- Check docs/plans/, docs/preparation/, docs/architecture/ briefly if they exist—reference relevant context
- Do not create new documentation artifacts
- Smoke tests only: Verify it compiles, runs, and happy path doesn't crash (no comprehensive unit tests—that's TEST phase work)

**Escalate to `/PACT:orchestrate` when**:
- Task spans multiple specialist domains
- Complex cross-domain coordination needed
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
| Smoke tests | Coders (minimal verification) |
| Unit tests | Test Engineer |
| Integration tests | Test Engineer |
| E2E tests | Test Engineer |

**Coders**: Your work isn't done until smoke tests pass. Smoke tests verify: "Does it compile? Does it run? Does the happy path not crash?" No comprehensive testing—that's TEST phase work.

**Test Engineer**: Engage after Code phase. You own ALL substantive testing: unit tests, integration, E2E, edge cases, adversarial testing. Target 80%+ meaningful coverage of critical paths.

### CODE → TEST Handoff

CODE phase produces decision log(s) at `docs/decision-logs/{feature}-{domain}.md`:
- `{feature}` = kebab-case feature name (match branch slug when available)
- `{domain}` = `backend`, `frontend`, or `database`
- Example: `user-authentication-backend.md`

**Decision log contents:**
```markdown
# Decision Log: {Feature Name}

## Summary
Brief description of what was implemented.

## Key Decisions
- Decision: rationale

## Assumptions
- Assumption made and why

## Known Limitations
- What wasn't handled and why

## Areas of Uncertainty
- Where bugs might hide, tricky parts

## Integration Context
- Depends on: [services, modules]
- Consumed by: [downstream code]

## Smoke Tests
- What was verified (compile, run, happy path)
```

**This is context, not prescription.** The test engineer decides what and how to test. The decision log helps inform that judgment.

**If decision log is missing**: For `/PACT:orchestrate`, request it from the orchestrator. For `/PACT:comPACT` (light ceremony), proceed with test design based on code analysis—decision logs are optional.

### TEST Decision Log

TEST phase produces its own decision log at `docs/decision-logs/{feature}-test.md`:

```markdown
# Test Decision Log: {Feature Name}

## Testing Approach
What strategy was chosen and why.

## Areas Prioritized
Referenced CODE logs: [list files read, e.g., `user-auth-backend.md`]
Focus areas based on their "areas of uncertainty".

## Edge Cases Identified
What boundary conditions and error scenarios were tested.

## Coverage Notes
What coverage was achieved, any significant gaps.

## What Was NOT Tested
Explicit scope boundaries and rationale (complexity, time, low risk).

## Known Issues
Flaky tests, environment dependencies, or unresolved concerns.
```

Focus on the **"why"** not the "what" — test code shows what was tested, the decision log explains the reasoning.

For `/PACT:comPACT` (light ceremony), this is optional.

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

> **Reference Skill**: For advanced filesystem-based context patterns (scratch pads, tool output offloading, sub-agent communication via files), invoke `filesystem-context` skill.

| Phase | Output Location |
|-------|-----------------|
| Plan | `docs/plans/` |
| Prepare | `docs/preparation/` |
| Architect | `docs/architecture/` |
| Code (decision logs) | `docs/decision-logs/{feature}-{domain}.md` |
| Test (decision log) | `docs/decision-logs/{feature}-test.md` |
| Test (artifacts) | `docs/testing/` |

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
