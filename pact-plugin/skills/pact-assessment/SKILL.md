---
name: pact-assessment
description: |
  S4 Intelligence layer: Checkpoints, tension detection, variety management, environment scanning.
  Use when: Phase boundaries, complexity assessment, S3/S4 tension, risk evaluation.
  Triggers on: S4 checkpoint, phase boundary, environment change, S3/S4 tension, variety score, complexity assessment, risk assessment, adaptation
---

# PACT Assessment (S4 Intelligence Layer)

S4 provides strategic intelligence: "Are we building the right thing? Is our approach still valid?"
Operates at a **days** horizon (milestones/sprints), not minute-level details.

## Temporal Horizons

| System | Horizon | Focus | PACT Context |
|--------|---------|-------|--------------|
| **S1** | Minutes | Current subtask | Agent executing implementation |
| **S3** | Hours | Current task/phase | Orchestrator coordinating feature |
| **S4** | Days | Milestone/sprint | Planning, adaptation, risk |
| **S5** | Persistent | Project identity | Values, principles, non-negotiables |

---

## S4 Checkpoint Protocol

**Triggers**: After PREPARE/ARCHITECT/CODE phases, on unexpected complexity, user-initiated pause.

### Checkpoint Questions

| Question | Sub-questions |
|----------|---------------|
| **Environment Change?** | New requirements? Constraints invalidated? Dependencies changed? |
| **Model Divergence?** | Assumptions wrong? Estimates off? Risks materialized? |
| **Plan Viability?** | Continue as planned? Adapt? Escalate? |

### Outcomes

| Finding | Action |
|---------|--------|
| All clear | Continue to next phase |
| Minor drift | Note in decision log, continue |
| Significant change | Pause, may re-run prior phase |
| Fundamental shift | Escalate to user (S5) |

### Checkpoint Format

```
**S4 Checkpoint** [Phase->Phase]:
- Environment: [stable / shifted: {what}]
- Model: [aligned / diverged: {what}]
- Plan: [viable / adapt: {how} / escalate: {why}]
```

**Enforcement**: Checkpoint not documented = phase transition incomplete.

---

## Variety Management

Variety = complexity requiring matched response capacity. Score each dimension 1-4:

| Dimension | 1 (Low) | 2 (Medium) | 3 (High) | 4 (Extreme) |
|-----------|---------|------------|----------|-------------|
| **Novelty** | Routine | Familiar | Novel | Unprecedented |
| **Scope** | Single concern | Few concerns | Many | Cross-cutting |
| **Uncertainty** | Clear reqs | Mostly clear | Ambiguous | Unknown |
| **Risk** | Low impact | Medium | High | Critical |

### Workflow by Score

| Score | Level | Workflow |
|-------|-------|----------|
| **4-6** | Low | `/PACT:comPACT` |
| **7-10** | Medium | `/PACT:orchestrate` |
| **11-14** | High | `/PACT:plan-mode` then orchestrate |
| **15-16** | Extreme | Research spike, then reassess |

### Variety Strategies

**Attenuate** (reduce variety): Apply patterns, decompose tasks, constrain scope
**Amplify** (increase capacity): Add specialists, parallel execution, nested PACT

### Variety Reassessment (at phase boundaries)

```
**Variety Reassessment** [Phase->Phase]:
- Initial: {N} / Current: {N}
- Change: [increased/decreased/stable] - {rationale}
- Adjustment: [none / add agents / simplify / escalate]
```

---

## S3/S4 Tension Detection

S3 (operational) and S4 (strategic) are in healthy tension. Unrecognized tension leads to poor decisions.

### Tension Indicators

| Type | S3 Push | S4 Pull |
|------|---------|---------|
| Schedule vs Quality | Skip phases | Thorough work |
| Execute vs Investigate | Code now | Understand first |
| Commit vs Adapt | Stay course | Change approach |
| Efficiency vs Safety | Parallel fast | Coordinate carefully |

### Detection Phrases

| When you think... | You're experiencing... |
|-------------------|------------------------|
| "We're behind, skip PREPARE" | S3 pushing |
| "Requirements unclear, dig deeper" | S4 pulling |
| "Just code it and see" | S3 shortcutting |
| "Feels risky, plan more" | S4 cautioning |

### Resolution Protocol

1. **Name it**: "S3/S4 tension: {specific tension}"
2. **Trade-offs**: S3 path [gains/risks] vs S4 path [gains/risks]
3. **Assess**: Project values, risk level, user preferences
4. **Decide or escalate**: Clear? Document. Unclear? Escalate to S5.

### Escalation Format

```
S3/S4 Tension: {One-line summary}
**Context**: {why tension exists}
**Option A (S3)**: {action} - Gains: {X} / Risks: {Y}
**Option B (S4)**: {action} - Gains: {X} / Risks: {Y}
**Recommendation**: {Option} - {rationale}
```

---

## Environment Model

Makes assumptions explicit. Required for high-variety (11+), recommended for medium (7-10).

### Template (save to `docs/preparation/environment-model-{feature}.md`)

```markdown
# Environment Model: {Feature}

## Tech Stack Assumptions
- Language/framework/dependencies with versions

## External Dependencies
- APIs, services, data sources with availability assumptions

## Constraints
- Performance, security, time, resources

## Unknowns
- Areas of uncertainty, questions needing answers

## Invalidation Triggers
- If {X} proves false -> {response}
```

### Update Protocol

| Event | Action |
|-------|--------|
| Assumption invalidated | Update model, note in checkpoint |
| New constraint discovered | Add to model, assess impact |
| Model significantly outdated | Consider returning to PREPARE |

---

## Quick Reference

### Phase Boundary Checklist

- [ ] S4 checkpoint questions answered and documented?
- [ ] Variety reassessed (initial vs current)?
- [ ] S3/S4 tension detected and resolved?
- [ ] Environment model updated (if exists)?

### When to Escalate to User

- Fundamental shift in checkpoint
- S3/S4 tension unresolved after analysis
- Variety score 15+ (extreme)
- 3+ assessments show consistent drift

### S4 Assessment vs imPACT

| S4 Assessment | imPACT |
|---------------|--------|
| "Is approach still valid?" | "How do we proceed?" |
| Phase boundary analysis | Execution blocker triage |
| Strategic (days) | Tactical (hours) |

Both complement: S4 checkpoints may trigger imPACT if issues found.
