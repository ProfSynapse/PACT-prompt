# PACT Protocols (Lean Reference)

> **Purpose**: Minimal protocols for PACT workflows. Agents reference this when needed, not memorized.
>
> **Design principle**: One-liners in prompts, details here.
>
> **Theoretical basis**: Structure informed by Stafford Beer's Viable System Model (VSM). See [vsm-glossary.md](../reference/vsm-glossary.md) for full terminology.
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

### S5 Decision Framing Protocol

When escalating any decision to user, apply variety attenuation to present decision-ready options rather than raw information.

#### Framing Template

```
{ICON} {DECISION_TYPE}: {One-line summary}

**Context**: [2-3 sentences max — what happened, why escalation needed]

**Options**:
A) {Option label}
   - Action: [What happens]
   - Trade-off: [Gain vs cost]

B) {Option label}
   - Action: [What happens]
   - Trade-off: [Gain vs cost]

C) Other (specify)

**Recommendation**: {Option} — [Brief rationale if you have a recommendation]
```

#### Decision Types and Icons

| Type | Icon | When |
|------|------|------|
| S3/S4 Tension | ⚖️ | Operational vs strategic conflict |
| Scope Change | 📐 | Task boundaries shifting |
| Technical Choice | 🔧 | Multiple valid approaches |
| Risk Assessment | ⚠️ | Uncertainty requiring judgment |
| Principle Conflict | 🎯 | Values in tension |
| Algedonic (HALT) | 🛑 | Viability threat — stops work |
| Algedonic (ALERT) | ⚡ | Attention needed — pauses work |

#### Example: Good Framing

> ⚖️ **S3/S4 Tension**: Skip PREPARE phase for faster delivery?
>
> **Context**: Task appears routine based on description, but touches auth code which has been problematic before.
>
> **Options**:
> A) **Skip PREPARE** — Start coding now, handle issues as they arise
>    - Trade-off: Faster start, but may hit avoidable blockers
>
> B) **Run PREPARE** — Research auth patterns first (~30 min)
>    - Trade-off: Slower start, but informed approach
>
> **Recommendation**: B — Auth code has caused issues; small investment reduces risk.

#### Example: Poor Framing (Avoid)

> "I'm not sure whether to skip the prepare phase. On one hand we could save time but on the other hand there might be issues. The auth code has been problematic. What do you think we should do? Also there are some other considerations like..."

#### Attenuation Guidelines

1. **Limit options to 2-3** — More creates decision paralysis
2. **Lead with recommendation** if you have one
3. **Quantify when possible** — "~30 min" beats "some time"
4. **State trade-offs explicitly** — Don't hide costs
5. **Keep context brief** — User can ask for more

---

## S4 Checkpoint Protocol

At phase boundaries, the orchestrator performs an S4 checkpoint to assess whether the current approach remains valid.

> **Temporal Horizon**: S4 operates at a **days** horizon—asking questions about the current milestone or sprint, not minute-level implementation details. See `CLAUDE.md > Temporal Horizons` for the full horizon model.

### Trigger Points

- After PREPARE phase completes
- After ARCHITECT phase completes
- After CODE phase completes (before TEST)
- When any agent reports unexpected complexity
- On user-initiated "pause and assess"

### Checkpoint Questions

1. **Environment Change**: Has external context shifted?
   - New requirements discovered?
   - Constraints invalidated?
   - Dependencies changed?

2. **Model Divergence**: Does our understanding match reality?
   - Assumptions proven wrong?
   - Estimates significantly off?
   - Risks materialized or emerged?

3. **Plan Viability**: Is current approach still optimal?
   - Should we continue as planned?
   - Adapt the approach?
   - Escalate to user for direction?

### Checkpoint Outcomes

| Finding | Action |
|---------|--------|
| All clear | Continue to next phase |
| Minor drift | Note in handoff, continue |
| Significant change | Pause, assess, may re-run prior phase |
| Fundamental shift | Escalate to user (S5) |

### Checkpoint Format (Brief)

> **S4 Checkpoint** [Phase→Phase]:
> - Environment: [stable / shifted: {what}]
> - Model: [aligned / diverged: {what}]
> - Plan: [viable / adapt: {how} / escalate: {why}]

### Output Behavior

**Default**: Silent-unless-issue — checkpoint runs internally; only surfaces to user when drift or issues detected.

**Examples**:

*Silent (all clear)*:
> (Internal) S4 Checkpoint Post-PREPARE: Environment stable, model aligned, plan viable → continue

*Surfaces to user (issue detected)*:
> **S4 Checkpoint** [PREPARE→ARCHITECT]:
> - Environment: Shifted — API v2 deprecated, v3 has breaking changes
> - Model: Diverged — Assumed backwards compatibility, now false
> - Plan: Adapt — Need PREPARE extension to research v3 migration path

### Relationship to Variety Checkpoints

S4 Checkpoints complement Variety Checkpoints (see Variety Management):
- **Variety Checkpoints**: "Do we have enough response capacity for this complexity?"
- **S4 Checkpoints**: "Is our understanding of the situation still valid?"

Both occur at phase transitions but ask different questions.

---

## S4 Environment Model

S4 checkpoints assess whether our mental model matches reality. The **Environment Model** makes this model explicit—documenting assumptions, constraints, and context that inform decision-making.

### Purpose

- **Make implicit assumptions explicit** — What do we assume about the tech stack, APIs, constraints?
- **Enable divergence detection** — When reality contradicts the model, we notice faster
- **Provide checkpoint reference** — S4 checkpoints compare current state against this baseline

### When to Create

| Trigger | Action |
|---------|--------|
| Start of PREPARE phase | Create initial environment model |
| High-variety tasks (11+) | Required — model complexity demands explicit tracking |
| Medium-variety tasks (7-10) | Recommended — document key assumptions |
| Low-variety tasks (4-6) | Optional — implicit model often sufficient |

### Model Contents

```markdown
# Environment Model: {Feature/Project}

## Tech Stack Assumptions
- Language: {language/version}
- Framework: {framework/version}
- Key dependencies: {list with version expectations}

## External Dependencies
- APIs: {list with version/availability assumptions}
- Services: {list with status assumptions}
- Data sources: {list with schema/format assumptions}

## Constraints
- Performance: {expected loads, latency requirements}
- Security: {compliance requirements, auth constraints}
- Time: {deadlines, phase durations}
- Resources: {team capacity, compute limits}

## Unknowns (Acknowledged Gaps)
- {List areas of uncertainty}
- {Questions that need answers}
- {Risks that need monitoring}

## Invalidation Triggers
- If {assumption X} proves false → {response}
- If {constraint Y} changes → {response}
```

### Location

`docs/preparation/environment-model-{feature}.md`

Created during PREPARE phase, referenced during S4 checkpoints.

### Update Protocol

| Event | Action |
|-------|--------|
| Assumption invalidated | Update model, note in S4 checkpoint |
| New constraint discovered | Add to model, assess impact |
| Unknown resolved | Move from Unknowns to appropriate section |
| Model significantly outdated | Consider returning to PREPARE |

### Relationship to S4 Checkpoints

The Environment Model is the baseline against which S4 checkpoints assess:
- "Environment shifted" → Compare current state to Environment Model
- "Model diverged" → Assumptions in model no longer hold
- "Plan viable" → Constraints in model still valid for current approach

---

## S3/S4 Tension Detection and Resolution

S3 (operational control) and S4 (strategic intelligence) are in constant tension. This is healthy—but unrecognized tension leads to poor decisions.

### Tension Indicators

S3/S4 tension exists when:
- **Schedule vs Quality**: Pressure to skip phases vs need for thorough work
- **Execute vs Investigate**: Urge to code vs need to understand
- **Commit vs Adapt**: Investment in current approach vs signals to change
- **Efficiency vs Safety**: Speed of parallel execution vs coordination overhead

### Detection Phrases

When you find yourself thinking:
- "We're behind, let's skip PREPARE" → S3 pushing
- "Requirements seem unclear, we should dig deeper" → S4 pulling
- "Let's just code it and see" → S3 shortcutting
- "This feels risky, we should plan more" → S4 cautioning

### Resolution Protocol

1. **Name the tension explicitly**:
   > "S3/S4 tension detected: [specific tension]"

2. **Articulate trade-offs**:
   > "S3 path: [action] — gains: [X], risks: [Y]"
   > "S4 path: [action] — gains: [X], risks: [Y]"

3. **Assess against project values**:
   - Does CLAUDE.md favor speed or quality for this project?
   - Is this a high-risk area requiring caution?
   - What has the user expressed preference for?

4. **If resolution is clear**: Decide and document
5. **If resolution is unclear**: Escalate to user (S5)

### Escalation Format

When escalating S3/S4 tension to user, use S5 Decision Framing:

> ⚖️ **S3/S4 Tension**: {One-line summary}
>
> **Context**: [What's happening, why tension exists]
>
> **Option A (S3 — Operational)**: [Action]
> - Gains: [Benefits]
> - Risks: [Costs]
>
> **Option B (S4 — Strategic)**: [Action]
> - Gains: [Benefits]
> - Risks: [Costs]
>
> **Recommendation**: [If you have one, with rationale]

### Integration with S4 Checkpoints

S4 Checkpoints are natural points to assess S3/S4 tension:
- Checkpoint finds drift → S3 wants to continue, S4 wants to adapt → Tension
- Checkpoint finds all-clear but behind schedule → S3 wants to skip phases, S4 wants thoroughness → Tension

When a checkpoint surfaces tension, apply the Resolution Protocol above.

---

## S2 Coordination Layer

The coordination layer enables parallel agent operation without conflicts. S2 is **proactive** (prevents conflicts) not just **reactive** (resolves conflicts). Apply these protocols whenever multiple agents work concurrently.

### Information Flows

S2 manages information flow between agents:

| From | To | Information |
|------|-----|-------------|
| Earlier agent | Later agents | Conventions established, interfaces defined |
| Orchestrator | All agents | Shared context, boundary assignments |
| Any agent | Orchestrator → All others | Resource claims, conflict warnings |

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

### S2 Pre-Parallel Checkpoint Format

When analyzing parallel work, emit proactive coordination signals:

> **S2 Pre-Parallel Check**:
> - Shared files: [none / list with mitigation]
> - Shared interfaces: [none / contract defined by X]
> - Conventions: [pre-defined / first agent establishes]
> - Anticipated conflicts: [none / sequencing X before Y]

**Example**:
> **S2 Pre-Parallel Check**:
> - Shared files: `src/types/api.ts` — Backend defines, Frontend consumes (read-only)
> - Shared interfaces: API contract defined in architecture doc
> - Conventions: Follow existing patterns in `src/utils/`
> - Anticipated conflicts: None

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

2. **Handoff reference**: Orchestrator passes first agent's key decisions to subsequent agents

3. **For truly parallel invocation** (all start simultaneously):
   - Orchestrator pre-defines conventions in all prompts
   - Or: Run one agent first to establish conventions, then parallelize the rest
   - **Tie-breaker**: If agents complete simultaneously and no first-agent convention exists, use alphabetical domain order (backend, database, frontend) for convention precedence

### Shared Language

All agents operating in parallel must:
- Use project glossary and established terminology
- Use standardized handoff structure (see Phase Handoffs)

### Parallelization Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Sequential by default** | Missed parallelization opportunity | Run QDCL; require justification for sequential |
| **Ignoring shared files** | Merge conflicts; wasted work | QDCL catches this; sequence or assign boundaries |
| **Over-parallelization** | Coordination overhead; convention drift | Limit parallel agents; use S2 coordination |
| **Analysis paralysis** | QDCL takes longer than the work | Time-box to 1 minute; default to parallel if unclear |

**Recovery**: If in doubt, default to parallel with S2 coordination active. Conflicts are recoverable; lost time is not.

### Anti-Oscillation Protocol

If agents produce contradictory outputs (each "fixing" the other's work):

1. **Detect**: Outputs conflict OR agents undo each other's work
2. **Pause**: Stop both agents immediately
3. **Diagnose**: Root cause—technical disagreement or requirements ambiguity?
4. **Resolve**:
   - Technical disagreement → Architect arbitrates
   - Requirements ambiguity → User (S5) clarifies
5. **Document**: Note resolution in handoff for future reference
6. **Resume**: Only after documented resolution

**Detection Signals**:
- Agent A modifies what Agent B just created
- Both agents claim ownership of same interface
- Output contradicts established convention
- Repeated "fix" cycles in same file/component

**Heuristic**: Consider it oscillation if the same file is modified by different agents 2+ times in rapid succession.

### Routine Information Sharing

After each specialist completes work:
1. **Extract** key decisions, conventions, interfaces established
2. **Propagate** to subsequent agents in their prompts
3. **Update** shared context for any agents still running in parallel

This transforms implicit knowledge into explicit coordination, reducing "surprise" conflicts.

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
- **Documentation**: Nested cycles report via handoff to parent
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

See [rePACT.md](../commands/rePACT.md) for full command documentation.

---

## Algedonic Signals (Emergency Bypass)

Algedonic signals handle viability-threatening conditions that require immediate user attention. Unlike normal blockers (handled by imPACT), algedonic signals bypass normal orchestration flow.

> **VSM Context**: In Beer's VSM, algedonic signals are "pain/pleasure" signals that bypass management hierarchy to reach policy level (S5) instantly.

For full protocol details, see [algedonic.md](algedonic.md).

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
- Apply risk-tiered testing (CRITICAL/HIGH) for high-risk areas

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

Coders provide handoff summaries to the orchestrator, who passes them to the test engineer.

**Enhanced Handoff Format**:
```
1. Produced: Files created/modified
2. Key decisions: Decisions with rationale, assumptions that could be wrong
3. Areas of uncertainty (PRIORITIZED):
   - [HIGH] {description} — Why risky, suggested test focus
   - [MEDIUM] {description}
   - [LOW] {description}
4. Integration points: Other components touched
5. Open questions: Unresolved items
```

Note: Not all priority levels need to be present. Most handoffs have 1-3 uncertainty items total.

**Example**:
```
1. Produced: `src/auth/token-manager.ts`, `src/auth/token-manager.test.ts`
2. Key decisions: Used JWT with 15min expiry (assumed acceptable for this app)
3. Areas of uncertainty:
   - [HIGH] Token refresh race condition — concurrent requests may get stale tokens; test with parallel calls
   - [MEDIUM] Clock skew handling — assumed <5s drift; may fail with larger skew
4. Integration points: Modified `src/middleware/auth.ts` to use new manager
5. Open questions: Should refresh tokens be stored in httpOnly cookies?
```

**Uncertainty Prioritization**:
- **HIGH**: "This could break in production" — Test engineer MUST cover these
- **MEDIUM**: "I'm not 100% confident" — Test engineer should cover these
- **LOW**: "Edge case I thought of" — Test engineer uses discretion

**Test Engineer Response**:
- HIGH uncertainty areas require explicit test cases (mandatory)
- If skipping a flagged area, document the rationale
- Report findings using the Signal Output System (GREEN/YELLOW/RED)

**This is context, not prescription.** The test engineer decides *how* to test, but flagged HIGH uncertainty areas must be addressed.

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

**Plan vs. Architecture artifacts**:
- **Plans** (`docs/plans/`): Pre-approval roadmaps created by `/PACT:plan-mode`. Created *before* implementation begins.
- **Architecture** (`docs/architecture/`): Formal specifications created by `pact-architect` *during* the Architect phase.

**No persistent logging for CODE/TEST phases.** Context passes via structured handoffs between agents. Git commits capture the audit trail.

---

## Session Continuity

If work spans sessions, update CLAUDE.md with:
- Current phase and task
- Blockers or open questions
- Next steps

---

## Related

- Agent definitions: `agents/`
- Commands: `commands/`
