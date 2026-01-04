---
description: Delegate a focused task to a single specialist (light ceremony)
argument-hint: [backend|frontend|database|prepare|test|architect] <task>
---
Delegate this focused task to a single PACT specialist: $ARGUMENTS

---

## Specialist Selection

| Shorthand | Specialist | Use For |
|-----------|------------|---------|
| `backend` | pact-backend-coder | Server-side logic, APIs, middleware |
| `frontend` | pact-frontend-coder | UI, React, client-side |
| `database` | pact-database-engineer | Schema, queries, migrations |
| `prepare` | pact-preparer | Research, requirements gathering |
| `test` | pact-test-engineer | Standalone test tasks |
| `architect` | pact-architect | Quick design consultations |

### If specialist not specified

**Auto-select when clear**:
- Task contains domain-specific keywords (React, Express, PostgreSQL, Jest, etc.)
- Task mentions specific file types (.tsx, .sql, .py, etc.)
- Task describes single-domain action (API endpoint, component, migration, test)
- Proceed immediately: "Delegating to [specialist]..."

**Ask when ambiguous**:
- Generic verbs without domain context (fix, improve, update)
- Feature-level scope that spans domains (login, user profile, dashboard)
- Performance/optimization without specific layer
- Ask: "This could be [options]. Which specialist should handle it?"

---

## Invocation

**Create feature branch** if not already on one (recommended for behavior changes; optional for trivial).

**Invoke the specialist with**:
```
comPACT mode: Work directly from this task description.
Skip reviewing docs/preparation/ and docs/architecture/ (none exist for this task).
Skip creating summary documentation in docs/.
Focus on the task at hand.
Unit tests: Required for logic changes; optional for trivial changes (documentation, comments, config).

If you hit a blocker, STOP and report it so the orchestrator can run /PACT:imPACT.

Task: [user's task description]
```

---

## After Specialist Completes

- Receive handoff from specialist
- Report completion to user

**If blocker reported**:
1. Receive blocker report from specialist
2. Run `/PACT:imPACT` to triage
3. May escalate to `/PACT:orchestrate` if task exceeds single-specialist scope

---

## When to Escalate

Recommend `/PACT:orchestrate` instead if:
- Task spans multiple specialist domains
- Architectural decisions affect multiple components
- Full preparation/architecture documentation is needed
