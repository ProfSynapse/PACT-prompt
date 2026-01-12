# PACT Protocols (Lean Reference)

> **Purpose**: Minimal protocols for PACT workflows. Agents reference this when needed, not memorized.
>
> **Design principle**: One-liners in prompts, details here.
>
> **Theoretical basis**: Structure informed by Stafford Beer's Viable System Model (VSM). See `pact-plugin/reference/vsm-glossary.md` for full terminology.
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

### Delegation Enforcement

**Application code** (orchestrator must delegate):
- Source files (`.py`, `.ts`, `.js`, `.rb`, `.go`, etc.)
- Test files (`.spec.ts`, `.test.js`, `test_*.py`)
- Scripts (`.sh`, `Makefile`, `Dockerfile`)
- Infrastructure (`.tf`, `.yaml`, `.yml`)
- App config (`.env`, `.json`, `config/`)

**Not application code** (orchestrator may edit):
- AI tooling (`CLAUDE.md`, `.claude/`)
- Documentation (`docs/`)
- Git config (`.gitignore`)
- IDE settings (`.vscode/`, `.idea/`)

**Tool Checkpoint**: Before `Edit`/`Write`:
1. STOP — Is this application code?
2. Yes → Delegate | No → Proceed | Uncertain → Delegate

**Recovery Protocol** (if you catch yourself mid-violation):
1. Stop immediately
2. Revert uncommitted changes (`git checkout -- <file>`)
3. Delegate to appropriate specialist
4. Note the near-violation for learning

**Why delegation matters**:
- **Role integrity**: Orchestrators coordinate; specialists implement
- **Accountability**: Clear ownership of code changes
- **Quality**: Specialists apply domain expertise
- **Auditability**: Clean separation of concerns

### Policy Checkpoints

At defined points, verify alignment with project principles:

| Checkpoint | When | Question |
|------------|------|----------|
| **Pre-CODE** | Before CODE phase begins | "Does the architecture align with project principles?" |
| **Pre-Edit** | Before using Edit/Write tools | "Is this application code? If yes, delegate." |
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

### Convention Propagation

When "first agent's choice becomes standard," subsequent agents need to discover those conventions:

1. **Orchestrator responsibility**: When invoking parallel agents after the first completes:
   - Extract key conventions from first agent's output (naming patterns, file structure, API style)
   - Include in subsequent agents' prompts: "Follow conventions established: {list}"

2. **Decision log reference**: If first agent wrote a decision log, subsequent agents should read it

3. **For truly parallel invocation** (all start simultaneously):
   - Orchestrator pre-defines conventions in all prompts
   - Or: Run one agent first to establish conventions, then parallelize the rest

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
- **Algedonic signals**: Algedonic signals from nested cycles still go **directly to user**—they bypass both the nested orchestration AND the parent orchestrator. Viability threats don't wait for hierarchy.

**Example:**
```
Parent task: "Implement user authentication service"
Nested PACT: "Research and implement OAuth2 token refresh mechanism"
  - Mini-Prepare: Research OAuth2 refresh token best practices
  - Mini-Architect: Design token storage and refresh flow
  - Mini-Code: Implement the mechanism
  - Mini-Test: Smoke test the refresh flow
```

### Orchestrator-Initiated Recursion (/PACT:rePACT)

While specialists can invoke nested cycles autonomously, the orchestrator can also initiate them:

| Initiator | Mechanism | When |
|-----------|-----------|------|
| Specialist | Autonomy Charter | Discovers complexity during work |
| Orchestrator | `/PACT:rePACT` command | Identifies complex sub-task upfront |

**Usage:**
- Single-domain: `/PACT:rePACT backend "implement rate limiting"`
- Multi-domain: `/PACT:rePACT "implement audit logging sub-system"`

See `rePACT.md` for full command documentation.

---

## S3* Continuous Audit

S3* provides real-time quality signals during CODE phase, complementing the sequential TEST phase. This enables early detection of critical issues without waiting for phase completion.

### When to Invoke Parallel Audit

| Condition | Risk Level | Action |
|-----------|------------|--------|
| Security-sensitive code (auth, payments, PII) | High | Invoke test engineer in parallel |
| Complex multi-component integration | High | Invoke for early integration review |
| Novel patterns (first use of new approach) | Medium-High | Invoke for testability assessment |
| User explicitly requests monitoring | Variable | Invoke parallel audit |
| Routine, well-understood code | Low | Sequential TEST phase sufficient |

**Default**: Sequential TEST phase. Parallel audit is opt-in for higher-risk work.

### Audit Modes

| Mode | When | Focus |
|------|------|-------|
| **Parallel Audit** | During CODE phase | Testability, early risks, integration concerns |
| **Comprehensive Test** | After CODE phase | Full coverage, edge cases, performance, security |

### Audit Signals

Test engineer surfaces to orchestrator:

| Signal | Meaning | Action |
|--------|---------|--------|
| 🟢 **GREEN** | "Code is testable, no concerns" | Continue normally |
| 🟡 **YELLOW** | "Testability concerns: {list}" | Note for TEST phase, continue |
| 🔴 **RED** | "Critical issue: {description}" | Interrupt CODE, triage immediately |

### 🔴 Signal Response Flow

When test engineer emits RED signal during parallel audit:

1. Orchestrator receives signal (S3* direct channel)
2. Orchestrator pauses affected coder(s)
3. Orchestrator triages: `/PACT:imPACT` with signal as input
4. imPACT determines: fix now, redo phase, or escalate
5. Resume CODE after resolution

**Note**: RED signals do NOT bypass orchestrator (unlike algedonic signals—see below). They interrupt normal flow but remain operational (S3), not emergency (S5).

### S2 Coordination for Parallel Audit

When test engineer runs parallel with coders:

- Test engineer is **READ-ONLY** on code files (no modifications)
- Test engineer may create test scaffolding in separate test files
- Coders have priority on source files; test engineer observes
- Conflicts escalate to orchestrator

### Scope

- Parallel audit is for `/PACT:orchestrate` only
- `/PACT:comPACT` uses sequential smoke tests (light ceremony)

---

## Algedonic Signals (Emergency Bypass)

Algedonic signals handle viability-threatening conditions that require immediate user attention. Unlike normal blockers (handled by imPACT), algedonic signals bypass normal orchestration flow.

> **VSM Context**: In Beer's VSM, algedonic signals are "pain/pleasure" signals that bypass management hierarchy to reach policy level (S5) instantly.

For full protocol details, see `protocols/algedonic.md`.

### Quick Reference

| Level | Categories | Response |
|-------|------------|----------|
| **HALT** | SECURITY, DATA, ETHICS | All work stops; user must acknowledge |
| **ALERT** | QUALITY, SCOPE, META-BLOCK | Work pauses; user decides |

### Signal Format

```
⚠️ ALGEDONIC [HALT|ALERT]: {Category}

**Issue**: {One-line description}
**Evidence**: {What triggered this}
**Impact**: {Why this threatens viability}
**Recommended Action**: {Suggested response}
```

### Key Rules

- **Any agent** can emit algedonic signals when they recognize trigger conditions
- Orchestrator **MUST** surface signals to user immediately—cannot suppress or delay
- HALT requires user acknowledgment before ANY work resumes
- ALERT allows user to choose: Investigate / Continue / Stop

### Relationship to imPACT

| Situation | Protocol | Scope |
|-----------|----------|-------|
| Operational blocker | imPACT | "How do we proceed?" |
| Repeated blocker (3+ cycles) | imPACT → ALERT | Escalate to user |
| Viability threat | Algedonic | "Should we proceed at all?" |

---

## Variety Management

Variety = complexity that must be matched with response capacity. Assess task variety before choosing a workflow.

### Task Variety Dimensions

| Dimension | 1 (Low) | 2 (Medium) | 3 (High) | 4 (Extreme) |
|-----------|---------|------------|----------|-------------|
| **Novelty** | Routine (done before) | Familiar (similar to past) | Novel (new territory) | Unprecedented |
| **Scope** | Single concern | Few concerns | Many concerns | Cross-cutting |
| **Uncertainty** | Clear requirements | Mostly clear | Ambiguous | Unknown |
| **Risk** | Low impact if wrong | Medium impact | High impact | Critical |

### Quick Variety Score

Score each dimension 1-4 and sum:

| Score | Variety Level | Recommended Workflow |
|-------|---------------|---------------------|
| **4-6** | Low | `/PACT:comPACT` |
| **7-10** | Medium | `/PACT:orchestrate` |
| **11-14** | High | `/PACT:plan-mode` → `/PACT:orchestrate` |
| **15-16** | Extreme | Research spike → Reassess |

**Calibration Examples**:

| Task | Novelty | Scope | Uncertainty | Risk | Score | Workflow |
|------|---------|-------|-------------|------|-------|----------|
| "Add pagination to existing list endpoint" | 1 | 1 | 1 | 2 | **5** | comPACT |
| "Add new CRUD endpoints following existing patterns" | 1 | 2 | 1 | 2 | **6** | comPACT |
| "Implement OAuth with new identity provider" | 3 | 3 | 3 | 3 | **12** | plan-mode → orchestrate |
| "Build real-time collaboration feature" | 4 | 4 | 3 | 3 | **14** | plan-mode → orchestrate |
| "Rewrite auth system with unfamiliar framework" | 4 | 4 | 4 | 4 | **16** | Research spike → Reassess |

> **Extreme (15-16) means**: Too much variety to absorb safely. The recommended action is a **research spike** (time-boxed exploration to reduce uncertainty) followed by reassessment. After the spike, the task should score lower—if it still scores 15+, decompose further or reconsider feasibility.

### Variety Strategies

**Attenuate** (reduce incoming variety):
- Apply existing patterns/templates from codebase
- Decompose into smaller, well-scoped sub-tasks
- Constrain to well-understood territory
- Use standards to reduce decision space

**Amplify** (increase response capacity):
- Invoke additional specialists
- Enable parallel execution
- Invoke nested PACT (`/PACT:rePACT`) for complex sub-components
- Run PREPARE phase to build understanding
- Engage parallel audit (S3*) for high-risk areas

### Variety Checkpoints

At phase transitions, briefly assess:
- "Has variety increased?" → Consider amplifying (more specialists, nested PACT)
- "Has variety decreased?" → Consider simplifying (skip phases, fewer agents)
- "Are we matched?" → Continue as planned

**Who performs checkpoints**: Orchestrator, at S4 mode transitions (between phases).

---

## The PACT Workflow Family

| Workflow | When to Use | Key Idea |
|----------|-------------|----------|
| **PACT** | Complex/greenfield work | Context-aware multi-agent orchestration |
| **plan-mode** | Before complex work, need alignment | Multi-agent planning consultation, no implementation |
| **comPACT** | Focused, single-domain tasks | Single-domain delegation with light ceremony (parallelizable) |
| **rePACT** | Complex sub-tasks within orchestration | Recursive nested P→A→C→T cycle (single or multi-domain) |
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
