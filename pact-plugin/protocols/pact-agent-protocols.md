# PACT Agent Protocols

> **Purpose**: Protocols for specialist agents operating within the PACT framework.
> **Referenced by**: All PACT specialist agents (pact-architect, pact-backend-coder, pact-frontend-coder, pact-database-engineer, pact-test-engineer, pact-preparer, pact-n8n)
> **See also**: `pact-protocols.md` for full orchestration protocols

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

When working in parallel (S2 Coordination Layer):
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

See `/PACT:rePACT` command for full documentation.

---

## Phase Handoffs

**On completing any phase, state**:
1. What you produced (with file paths)
2. Key decisions made
3. What the next agent needs to know

Keep it brief. No templates required.

---

## Algedonic Signals (Emergency Bypass)

Algedonic signals handle viability-threatening conditions that require immediate user attention. Unlike normal blockers (handled by imPACT), algedonic signals bypass normal orchestration flow.

> **VSM Context**: In Beer's VSM, algedonic signals are "pain/pleasure" signals that bypass management hierarchy to reach policy level (S5) instantly.

For full protocol details, see `algedonic.md`.

### Quick Reference

| Level | Categories | Response |
|-------|------------|----------|
| **HALT** | SECURITY, DATA, ETHICS | All work stops; user must acknowledge |
| **ALERT** | QUALITY, SCOPE, META-BLOCK | Work pauses; user decides |

### Signal Format

```
ALGEDONIC [HALT|ALERT]: {Category}

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
