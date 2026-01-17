---
name: pact-specialist
description: |
  S1 Operations layer: Specialist autonomy, phase transitions, and blocker handling.
  Use when: Questions about agent authority, phase handoffs, nested PACT, or blockers.
  Triggers on: specialist autonomy, agent authority, nested PACT, rePACT, phase handoff,
  test engagement, blocker protocol, scope change
---

# PACT Specialist Operations

S1 Operations layer for specialist agents: autonomy, transitions, blockers.

---

## Autonomy Charter

**CAN do without escalation:**
- Adjust implementation approach based on discoveries
- Request context from other specialists via orchestrator
- Recommend scope changes when complexity differs from estimate
- Apply domain expertise without micro-management
- Invoke nested PACT for complex sub-tasks within your domain

**MUST escalate when:**
- Discovery contradicts architecture
- Scope change exceeds 20% (see below)
- Security/policy implications emerge (potential S5 violations)
- Cross-domain dependency discovered

### The 20% Rule (Scope Change)

Measured by ANY of: time, files touched, dependencies added, or risk level change.

```
Scope change > 20%?
  YES → Escalate: what changed, why, your recommendation
  NO  → Proceed, note in decision log
```

---

## S4 Checkpoint (MANDATORY)

> **Do NOT proceed to next phase without S4 checkpoint.**

S4 checkpoints are required at phase boundaries. For full checkpoint procedure, format, and decision table, invoke the `pact-assessment` skill.

**Quick reference**: Verify Environment (context shifted?), Model (assumptions valid?), Plan (approach optimal?).

---

## Nested PACT (rePACT)

**Use when sub-task has:**
- Multiple concerns within your domain
- Uncertainty requiring research
- Multiple consumers of output
- Distinct testable lifecycle

**Flatten instead when:**
- Straightforward (just do it)
- No uncertainty
- Single consumer
- Would add ceremony without value

**Protocol:**
1. Declare: "Invoking nested PACT for {sub-task}"
2. Execute: Mini P-A-C-T (skip unneeded phases)
3. Integrate: Merge results to parent
4. Report: Include in handoff

**Constraints:** Max 2 nesting levels. Stay in your domain. Algedonic signals still bypass all hierarchy.

---

## Phase Handoffs

On completing any phase, state:
1. **Produced**: File paths, artifacts
2. **Decisions**: Key choices and rationale
3. **Next needs**: Context, gotchas for next agent

### CODE to TEST

Produce decision log at `docs/decision-logs/{feature}-{domain}.md`:
- Summary, Key Decisions, Assumptions
- Known Limitations, Areas of Uncertainty
- Integration Context, Smoke Tests performed

**Context, not prescription.** Test engineer decides what to test.

---

## Test Engagement

| Type | Owner |
|------|-------|
| Smoke tests | Coders |
| Unit/Integration/E2E | Test Engineer |

**Coders**: Done when smoke tests pass (compile, run, happy path).
**Test Engineer**: Engage after CODE. Own all substantive testing.

---

## Blocker Protocol

**Stop and report when:**
- Same error after 2+ attempts
- Missing required info
- Outside your specialty
- Viability threat (emit algedonic)

**Report format:**
```
BLOCKER: {one-line}
Attempted: {what you tried}
Needed: {what unblocks you}
```

Wait for orchestrator. Do not continue guessing.

---

## Self-Coordination (Parallel Agents)

1. Check S2 protocols first
2. Respect file boundaries
3. First agent's conventions = standard
4. Report conflicts immediately

---

## Quick Decision Trees

**Escalate?**
```
Security/policy issue? → Escalate
Contradicts architecture? → Escalate
Scope > 20%? → Escalate
Cross-domain? → Escalate
Otherwise → Proceed
```

**Nested PACT?**
```
Complex with uncertainty? → Maybe
Spans multiple concerns? → Nested PACT
Otherwise → Flatten
```

**Blocked?**
```
Same error 2+ times? → Report
Missing info? → Report
Outside specialty? → Report
Otherwise → Keep working
```
