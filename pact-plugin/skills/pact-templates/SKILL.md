---
name: pact-templates
description: |
  Documentation templates and formats for PACT artifacts.
  Use when: Creating decision logs, architecture docs, preparation docs, review docs.
  Triggers on: decision log, documentation template, architecture doc, preparation doc, test report, review document
---

# PACT Documentation Templates

## Locations

| Phase | Location |
|-------|----------|
| Plan | `docs/plans/{feature-slug}-plan.md` |
| Prepare | `docs/preparation/{feature}.md` |
| Environment Model | `docs/preparation/environment-model-{feature}.md` |
| Architect | `docs/architecture/{feature}.md` |
| Code Decision Log | `docs/decision-logs/{feature}-{domain}.md` |
| Test Decision Log | `docs/decision-logs/{feature}-test.md` |
| Orchestration Log | `docs/decision-logs/orchestration-{feature}.md` |

**Domain**: `backend`, `frontend`, or `database`

---

## CODE Decision Log

```markdown
# Decision Log: {Feature}
## Summary
What was implemented.
## Key Decisions
- Decision: rationale
## Assumptions
- Assumption: why
## Known Limitations
- What wasn't handled
## Areas of Uncertainty
- Where bugs might hide
## Integration Context
- Depends on: [list] | Consumed by: [list]
## Smoke Tests
- Verified: compile, run, happy path
```

---

## TEST Decision Log

```markdown
# Test Decision Log: {Feature}
## Testing Approach
Strategy and rationale.
## Areas Prioritized
Focus areas from CODE decision logs.
## Coverage Notes
Achieved coverage, gaps.
## What Was NOT Tested
Scope boundaries, rationale.
```

---

## Orchestration Log (Variety 10+)

```markdown
# Orchestration Log: {Feature}
Date: {YYYY-MM-DD} | Variety: {score} ({N}/{S}/{U}/{R})
## Phase Log
| Phase | Agents | Key Outcome |
|-------|--------|-------------|
| PREPARE | {list} | {findings} |
| ARCHITECT | {list} | {decisions} |
| CODE | {list} | {blockers} |
| TEST | {list} | {issues} |
## Outcome
Result: [success/partial/blocked] | Follow-up: [items]
```

**Variety 7-9**: Key Decisions table + Outcome only.

---

## Environment Model

```markdown
# Environment Model: {Feature}
## Tech Stack
Language, framework, key dependencies with versions.
## External Dependencies
APIs, services, data sources with assumptions.
## Constraints
Performance, security, time, resources.
## Unknowns
Open questions, risks to monitor.
```

---

## Review Synthesis

```markdown
# Review: {Feature/PR}
## Findings
- Architect: [points]
- Test Engineer: [points]
- Domain Specialist: [points]
## Agreements
Aligned points.
## Conflicts & Resolution
Disagreements and how resolved.
## Action Items
- [ ] Required | - [ ] Optional
```
