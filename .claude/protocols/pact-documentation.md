## Documentation Locations

> **Reference Skill**: For advanced filesystem-based context patterns (scratch pads, tool output offloading, sub-agent communication via files), invoke `filesystem-context` skill.

| Phase | Output Location |
|-------|-----------------|
| Plan | `docs/plans/` |
| Prepare | `docs/preparation/` |
| Prepare (environment model) | `docs/preparation/environment-model-{feature}.md` |
| Architect | `docs/architecture/` |
| Code (decision logs) | `docs/decision-logs/{feature}-{domain}.md` |
| Test (decision log) | `docs/decision-logs/{feature}-test.md` |
| Test (artifacts) | `docs/testing/` |
| Orchestration (decision log) | `docs/decision-logs/orchestration-{feature}.md` |

**Plan vs. Architecture artifacts**:
- **Plans** (`docs/plans/`): Pre-approval roadmaps created by `/PACT:plan-mode`. Multi-specialist consultation synthesized into scope estimates, sequencing, and risk assessment. Created *before* implementation begins.
- **Architecture** (`docs/architecture/`): Formal specifications created by `pact-architect` *during* the Architect phase of `/PACT:orchestrate`. Detailed component designs, interface contracts, and technical decisions.

Plans inform implementation strategy; architecture documents define the technical blueprint.

### Orchestration Decision Log

For `/PACT:orchestrate` runs, the orchestrator maintains a decision log providing an S3-level audit trail. This log captures key orchestration decisions for retrospective analysis and pattern recognition.

**Location**: `docs/decision-logs/orchestration-{feature}.md`

**When to create**:
- Variety score 7-9: Lightweight log (key decisions only)
- Variety score 10+: Full log (complete audit trail)
- Variety 4-6 (comPACT): No orchestration log (task too simple)

**Lightweight format** (Variety 7-9):
```markdown
# Orchestration Log: {Feature}
Date: {YYYY-MM-DD}
Variety Score: {score} ({N/S/U/R})

## Key Decisions
| Phase | Decision | Rationale |
|-------|----------|-----------|
| ... | ... | ... |

## Outcome
- Result: [success / partial / blocked]
- Follow-up: [none / items]
```

**Full format** (Variety 10+):
```markdown
# Orchestration Log: {Feature}
Date: {YYYY-MM-DD}
Variety Score: {score} ({Novelty}/{Scope}/{Uncertainty}/{Risk})

## Variety Assessment
- Novelty: {1-4} — {rationale}
- Scope: {1-4} — {rationale}
- Uncertainty: {1-4} — {rationale}
- Risk: {1-4} — {rationale}
- Response: {attenuators/amplifiers applied}

## Phase Log

### PREPARE
- Agent(s): {list}
- Duration: {approx}
- S4 Checkpoint: {outcome}
- Key findings: {list}

### ARCHITECT
- Agent(s): {list}
- S2 Coordination: {pre-parallel check if applicable}
- S4 Checkpoint: {outcome}
- Key decisions: {list}

### CODE
- Agent(s): {list}
- Parallelization: {yes/no — rationale}
- S2 Coordination: {conflict prevention measures}
- S4 Checkpoint: {outcome}
- Blockers: {none / handled via imPACT}

### TEST
- Agent(s): {list}
- Coverage: {summary}
- Issues found: {list}

## S3/S4 Tensions
{Record any detected tensions and resolutions, or "None detected"}

## Algedonic Signals
{Record any HALT/ALERT signals, or "None"}

## Retrospective
- What worked: {list}
- What to improve: {list}
- Patterns to note: {list}
```

**Update cadence**:
- Create log at orchestration start (after variety assessment)
- Update after each phase completion
- Finalize after TEST phase or on early termination

---

## Session Continuity

If work spans sessions, update CLAUDE.md with:
- Current phase and task
- Blockers or open questions
- Next steps

---

