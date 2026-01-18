---
name: pact-agent-coordination
description: |
  Coordination protocols for specialist agents working in parallel.
  Use when: Working alongside other agents, editing shared codebases, discovering cross-domain issues.
  Triggers on: parallel work, convention drift, cross-agent discovery, file editing, coordination
---

# Agent Coordination Protocols

Protocols for specialist agents working in parallel with other agents.
Follow these when the orchestrator invokes multiple agents concurrently.

---

## Convention Drift Check

Before editing any file:

1. **Check existing conventions** in the file/module
   - Naming patterns, formatting, code organization
   - Import styles, error handling patterns
   - Comment conventions

2. **Follow established conventions** (even if you'd do it differently)
   - Consistency within a codebase trumps personal preference
   - The first agent's choices become the standard for the batch

3. **If conventions seem wrong**, escalate to orchestrator
   - Do NOT silently change conventions
   - Report: "Convention concern: {what seems wrong} in {file}"
   - Let orchestrator decide whether to change or maintain

---

## Cross-Agent Discovery Handoff

When you discover something affecting another domain:

```
⚠️ CROSS-AGENT: {what was discovered}
Affects: {which domain/agent}
Impact: {what they need to know/do}
```

**Rules:**
- Report to orchestrator immediately
- Do NOT attempt cross-domain fixes yourself
- Note it prominently in your handoff (not buried in details)
- Orchestrator will relay to affected agent or adjust coordination

**Examples:**
- Backend discovers frontend needs a new API field → CROSS-AGENT
- Database discovers schema change affects backend queries → CROSS-AGENT
- Frontend discovers API contract doesn't match docs → CROSS-AGENT

---

## Self-Coordination Checklist

When working in parallel with other agents:

- [ ] **Check S2 boundaries** — Am I staying in my assigned area?
- [ ] **Respect file boundaries** — Not editing files assigned to others?
- [ ] **Follow conventions** — Using established patterns from first agent?
- [ ] **Report conflicts immediately** — Found overlap or contradiction?

---

## Conflict Response

If you detect a conflict with another agent's work:

1. **STOP** — Don't continue the conflicting edit
2. **Report** — Tell orchestrator immediately:
   ```
   CONFLICT: {what conflicts}
   My work: {what I was doing}
   Their work: {what I see they did}
   ```
3. **Wait** — Let orchestrator resolve before continuing

---

## Domain Boundaries

### Backend ↔ Database

| Database Owns | Backend Owns |
|---------------|--------------|
| Schema design, DDL | ORM models |
| Migrations | Repository/DAL layer |
| Complex SQL queries | App queries via ORM |
| Indexes | Connection pooling |

**Sequence**: Database delivers schema → Backend implements ORM.

**Need cross-domain work?** Report to orchestrator—don't reach across boundaries yourself.

---

## Quick Reference

| Situation | Action |
|-----------|--------|
| Editing a file | Check conventions first |
| Conventions seem wrong | Escalate, don't change |
| Discover cross-domain issue | Emit CROSS-AGENT signal |
| See another agent's changes | Follow their conventions |
| Detect conflict | Stop, report, wait |
| Need something from another domain | Report to orchestrator |
