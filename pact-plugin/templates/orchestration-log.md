# Orchestration Decision Log

> Two formats available based on variety score:
> - **Lightweight** (Variety 7-9): Use the first template
> - **Full** (Variety 10+): Use the second template

---

## Lightweight Format (Variety 7-9)

```markdown
# Orchestration Log: {Feature}

**Date**: {YYYY-MM-DD}
**Variety Score**: {score} ({N/S/U/R})

## Key Decisions

| Phase | Decision | Rationale |
|-------|----------|-----------|
| PREPARE | {e.g., Skipped—existing docs sufficient} | {why} |
| ARCHITECT | {e.g., Single component, no formal spec} | {why} |
| CODE | {e.g., Backend only, no parallelization} | {why} |
| TEST | {e.g., Unit tests focused on edge cases} | {why} |

## Outcome

- **Result**: [success / partial / blocked]
- **Follow-up**: [none / items to address]
```

---

## Full Format (Variety 10+)

```markdown
# Orchestration Log: {Feature}

**Date**: {YYYY-MM-DD}
**Variety Score**: {score} ({Novelty}/{Scope}/{Uncertainty}/{Risk})

## Variety Assessment

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Novelty | {1-4} | {why this score} |
| Scope | {1-4} | {why this score} |
| Uncertainty | {1-4} | {why this score} |
| Risk | {1-4} | {why this score} |

**Response**: {attenuators/amplifiers applied—e.g., "Added research spike", "Enabled parallelization"}

---

## Phase Log

### PREPARE

- **Agent(s)**: pact-preparer
- **Duration**: {approx time}
- **S4 Checkpoint**: {stable / shifted / diverged}
- **Key findings**:
  - {finding 1}
  - {finding 2}

### ARCHITECT

- **Agent(s)**: pact-architect
- **S2 Coordination**: {pre-parallel check if applicable}
- **S4 Checkpoint**: {stable / shifted / diverged}
- **Key decisions**:
  - {decision 1}
  - {decision 2}

### CODE

- **Agent(s)**: {list agents invoked}
- **Parallelization**: {yes/no — rationale}
- **S2 Coordination**: {conflict prevention measures taken}
- **S4 Checkpoint**: {stable / shifted / diverged}
- **Blockers**: {none / handled via imPACT: {summary}}

### TEST

- **Agent(s)**: pact-test-engineer
- **Coverage**: {summary of what was tested}
- **Issues found**: {list or "none"}

---

## S3/S4 Tensions

{Record any detected tensions and how they were resolved}

| Tension | Resolution | Outcome |
|---------|------------|---------|
| {e.g., Schedule vs Quality} | {e.g., User chose quality} | {result} |

*Or: "None detected"*

---

## Algedonic Signals

{Record any HALT/ALERT signals emitted during orchestration}

| Signal | Category | Resolution |
|--------|----------|------------|
| {HALT/ALERT} | {SECURITY/DATA/ETHICS/QUALITY/SCOPE} | {how resolved} |

*Or: "None"*

---

## Retrospective

- **What worked well**:
  - {item}
- **What to improve**:
  - {item}
- **Patterns to note**:
  - {item for future reference}
```
