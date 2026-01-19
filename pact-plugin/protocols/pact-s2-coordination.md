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

2. **Decision log reference**: If first agent wrote a decision log, subsequent agents should read it

3. **For truly parallel invocation** (all start simultaneously):
   - Orchestrator pre-defines conventions in all prompts
   - Or: Run one agent first to establish conventions, then parallelize the rest

### Convention Extraction Template

When the first agent completes work, extract conventions using this format:

```markdown
**Conventions Established** (propagate to parallel agents):
- Naming: {pattern — e.g., camelCase for functions, PascalCase for classes}
- File structure: {pattern — e.g., one component per file, co-located tests}
- Error handling: {pattern — e.g., custom error classes, Result<T,E> pattern}
- Imports: {pattern — e.g., absolute paths, grouped by type}
- Documentation: {pattern — e.g., JSDoc for public APIs, inline for complex logic}
- [Other domain-specific conventions discovered]
```

**What to extract**:
- Explicit choices mentioned in decision log or handoff
- Implicit patterns observable in the code produced
- Deviations from project defaults (and why)

### Convention Announcement Protocol

When parallel agents are running and conventions need propagation:

| Step | Actor | Action |
|------|-------|--------|
| 1 | First agent | Completes work, provides handoff with decisions |
| 2 | Orchestrator | Extracts conventions using template above |
| 3 | Orchestrator | Announces conventions to remaining parallel agents |
| 4 | Remaining agents | Acknowledge receipt and align ongoing work |

**Announcement format** (inject into running agent context):

```markdown
**Convention Update** (from completed parallel work):

Agent {name} established these conventions — align your work accordingly:
{extracted conventions}

If you've already made conflicting choices, note in handoff for reconciliation.
```

**Timing considerations**:
- Announce as soon as first agent completes (don't wait for all)
- If multiple agents complete near-simultaneously, merge their conventions before announcing
- Late-completing agents receive accumulated conventions from all prior completions

### Conflict Resolution: When Conventions Collide

When two agents started simultaneously establish different conventions before either receives the other's output:

**Detection signals**:
- Two agents' outputs use different naming patterns for similar concepts
- File structure choices conflict (e.g., flat vs nested)
- Error handling approaches differ within same domain

**Resolution protocol**:

| Scenario | Resolution | Rationale |
|----------|------------|-----------|
| One completes first, other still running | First completes wins; notify second | Simpler; second can still adapt |
| Both complete before conflict detected | Architect arbitrates; normalize both | Need authoritative decision |
| Conventions are compatible (just different) | Document both as acceptable variants | Avoid unnecessary churn |
| Conventions directly conflict | Pick one; refactor the other | Consistency over individual preference |

**Arbitration criteria** (when Architect decides):
1. Which convention better aligns with existing project patterns?
2. Which is more idiomatic for the language/framework?
3. Which is simpler to maintain long-term?
4. If equal, prefer the convention from the larger body of work

**After resolution**:
- Document chosen convention in decision log
- Note the conflict and resolution (helps future similar situations)
- Refactoring of non-chosen convention may be deferred if low-impact

### Convention Extraction Examples

**Good example** — Clear, actionable conventions extracted:

```markdown
**Conventions Established** (propagate to parallel agents):
- Naming: camelCase for functions/variables, PascalCase for types/classes,
  SCREAMING_SNAKE for constants
- File structure: Feature folders with index.ts barrel exports;
  tests co-located as `*.test.ts`
- Error handling: Custom `AppError` class with error codes;
  wrap external errors at boundary
- Imports: Absolute paths from `@/`; group order: external, internal, relative
- API responses: `{ success: boolean, data?: T, error?: { code, message } }`
- Logging: Structured JSON via `logger.info({ event, context })`
```

**Poor example** — Vague, missing actionable detail:

```markdown
**Conventions Established**:
- Naming: Standard conventions
- File structure: Organized appropriately
- Error handling: Proper error handling implemented
- Other: Following best practices
```

**Why the poor example fails**:
- "Standard" and "proper" are subjective and undefined
- No specific patterns a parallel agent could replicate
- Forces parallel agents to guess or inspect code directly
- Creates convention drift risk

**What to do with poor extraction**: If you find yourself writing vague conventions, review the first agent's actual output and extract specific, replicable patterns. If patterns aren't clear from the output, that's a signal the first agent's work may need clarification.

### Shared Language

All agents operating in parallel must:
- Use project glossary and established terminology
- Follow consistent decision log format (see CODE → TEST Handoff)
- Use standardized handoff structure (see Phase Handoffs)

### Anti-Oscillation Protocol

If agents produce contradictory outputs (each "fixing" the other's work):

1. **Detect**: Outputs conflict OR agents undo each other's work
2. **Pause**: Stop both agents immediately
3. **Diagnose**: Root cause—technical disagreement or requirements ambiguity?
4. **Resolve**:
   - Technical disagreement → Architect arbitrates
   - Requirements ambiguity → User (S5) clarifies
5. **Document**: Record resolution in decision log for future reference
6. **Resume**: Only after documented resolution

**Detection Signals**:
- Agent A modifies what Agent B just created
- Both agents claim ownership of same interface
- Output contradicts established convention
- Repeated "fix" cycles in same file/component

### Routine Information Sharing

After each specialist completes work:
1. **Extract** key decisions, conventions, interfaces established
2. **Propagate** to subsequent agents in their prompts
3. **Update** shared context for any agents still running in parallel

This transforms implicit knowledge into explicit coordination, reducing "surprise" conflicts.

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

