## S3* Continuous Audit

S3* provides real-time quality signals during CODE phase, complementing the sequential TEST phase. This enables early detection of critical issues without waiting for phase completion.

### When to Invoke Parallel Audit

| Condition | Risk Level | Action |
|-----------|------------|--------|
| Security-sensitive code (auth, payments, PII) | High | Invoke test engineer in parallel |
| Complex multi-component integration | High | Invoke for early integration review |
| Novel patterns (first use of new approach) | Medium-High | Invoke for testability assessment |
| User explicitly requests monitoring | Variable | Invoke parallel audit |
| Routine, well-understood code | Low | Sequential TEST phase sufficient |

**Default**: Sequential TEST phase. Parallel audit is opt-in for higher-risk work.

### Audit Modes

| Mode | When | Focus |
|------|------|-------|
| **Parallel Audit** | During CODE phase | Testability, early risks, integration concerns |
| **Comprehensive Test** | After CODE phase | Full coverage, edge cases, performance, security |

### Audit Signals

Test engineer surfaces to orchestrator:

| Signal | Meaning | Action |
|--------|---------|--------|
| 🟢 **GREEN** | "Code is testable, no concerns" | Continue normally |
| 🟡 **YELLOW** | "Testability concerns: {list}" | Note for TEST phase, continue |
| 🔴 **RED** | "Critical issue: {description}" | Interrupt CODE, triage immediately |

### 🔴 Signal Response Flow

When test engineer emits RED signal during parallel audit:

1. Orchestrator receives signal (S3* direct channel)
2. Orchestrator pauses affected coder(s)
3. Orchestrator triages: `/PACT:imPACT` with signal as input
4. imPACT determines: fix now, redo phase, or escalate
5. Resume CODE after resolution

**Note**: RED signals do NOT bypass orchestrator (unlike algedonic signals—see below). They interrupt normal flow but remain operational (S3), not emergency (S5).

### S2 Coordination for Parallel Audit

When test engineer runs parallel with coders:

- Test engineer is **READ-ONLY** on code files (no modifications)
- Test engineer may create test scaffolding in separate test files
- Coders have priority on source files; test engineer observes
- Conflicts escalate to orchestrator

### Scope

- Parallel audit is for `/PACT:orchestrate` only
- `/PACT:comPACT` uses sequential smoke tests (light ceremony)

---

