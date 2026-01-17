---
name: pact-governance
description: |
  S5 Policy layer: SACROSANCT rules, delegation enforcement, and algedonic emergency signals.
  Use when: Governance questions arise, policy violations detected, emergency signals needed.
  Triggers on: SACROSANCT, non-negotiable, algedonic, HALT signal, ALERT signal, security violation, ethics, delegation rule, policy checkpoint
---

# PACT Governance (S5 Policy Layer)

The policy layer defines non-negotiable constraints and emergency bypass mechanisms.
All other protocols operate within these boundaries.

---

## SACROSANCT Rules (Never Override)

These rules cannot be traded off for operational pressure:

| Category | Never... | Always... |
|----------|----------|-----------|
| **Security** | Expose credentials, skip input validation | Sanitize outputs, secure by default |
| **Quality** | Merge known-broken code, skip tests | Verify tests pass before PR |
| **Ethics** | Generate deceptive outputs, harmful content | Maintain honesty and transparency |
| **Delegation** | Orchestrator writes application code | Delegate to specialist agents |

**If a rule would be violated**: Stop work, report to user. No exceptions.

---

## Delegation Enforcement

### What Is Application Code?

| Orchestrator MUST Delegate | Orchestrator May Edit |
|----------------------------|----------------------|
| Source files (`.py`, `.ts`, `.js`, `.rb`, `.go`) | AI tooling (`CLAUDE.md`, `.claude/`) |
| Test files (`.spec.ts`, `.test.js`, `test_*.py`) | Documentation (`docs/`) |
| Scripts (`.sh`, `Makefile`, `Dockerfile`) | Git config (`.gitignore`) |
| Infrastructure (`.tf`, `.yaml`, `.yml`) | IDE settings (`.vscode/`, `.idea/`) |
| App config (`.env`, `.json`, `config/`) | |

### Tool Checkpoint Protocol

Before using `Edit` or `Write`:

1. **STOP** - Is this application code?
2. **Yes** -> Delegate to specialist
3. **No** -> Proceed
4. **Uncertain** -> Delegate (err on caution)

### Recovery Protocol (Mid-Violation)

If you catch yourself editing application code:

1. Stop immediately
2. Revert: `git checkout -- <file>`
3. Delegate to appropriate specialist
4. Note the near-violation for learning

---

## Algedonic Signals (Emergency Bypass)

Algedonic signals bypass normal orchestration and escalate directly to user (S5).

### Signal Categories

**HALT Signals** - Stop everything. User must acknowledge before ANY work resumes.

| Category | Triggers | Examples |
|----------|----------|----------|
| **SECURITY** | Credentials exposure, injection vulnerability, auth bypass | API key in code, SQL injection, JWT validation missing |
| **DATA** | PII exposure, data corruption risk, integrity violation | User emails in logs, DELETE without WHERE, unencrypted PII |
| **ETHICS** | Deceptive output, harmful content, policy violation | Misleading user-facing text, generating harmful instructions |

**ALERT Signals** - Pause current work. User notified. User may choose to continue or halt.

| Category | Triggers | Examples |
|----------|----------|----------|
| **QUALITY** | Repeated build failures, severe coverage gaps | Build broken >2 attempts, coverage <50% on critical path |
| **SCOPE** | Fundamental requirement misunderstanding | Building wrong feature, architecture contradicts intent |
| **META-BLOCK** | 3+ imPACT cycles without resolution | Same blocker recurring, systemic issue |

### Signal Format Template

```
ALGEDONIC [HALT|ALERT]: {Category}

**Issue**: {One-line description}
**Evidence**: {File, line, specific observation}
**Impact**: {Why this threatens viability}
**Confidence**: [HIGH|MEDIUM|LOW]
**Recommended Action**: {Concrete next step}
```

### Confidence Tagging

| Level | Meaning | Action |
|-------|---------|--------|
| **HIGH** | Clear evidence, definite threat | Immediate escalation |
| **MEDIUM** | Strong indicators, some uncertainty | Escalate with caveats |
| **LOW** | Suspicion, needs verification | Note concern, investigate first |

### Example Signals

**HALT Example** (SECURITY):
```
ALGEDONIC HALT: SECURITY
**Issue**: AWS credentials hardcoded in source file
**Evidence**: `src/config/aws.ts:15` - `AWS_SECRET_ACCESS_KEY = "AKIA..."`
**Impact**: Credentials exposed if committed; AWS account compromise risk
**Confidence**: HIGH
**Recommended Action**: Remove credentials, use env vars, rotate key
```

**ALERT Example** (META-BLOCK):
```
ALGEDONIC ALERT: META-BLOCK
**Issue**: Third consecutive imPACT cycle without resolution
**Evidence**: Auth middleware failing on same error; tried 3 approaches
**Impact**: May indicate fundamental misunderstanding
**Confidence**: HIGH
**Recommended Action**: User review of requirements; restart from PREPARE
```

### Who Can Emit Signals

**Any agent** can emit algedonic signals. No orchestrator permission needed - the conditions themselves authorize the signal.

| Agent | Watch For |
|-------|-----------|
| **Backend Coder** | SECURITY (auth, injection), DATA (query safety, PII) |
| **Frontend Coder** | SECURITY (XSS, CSRF), DATA (client storage of sensitive data) |
| **Database Engineer** | DATA (schema integrity, PII, destructive operations) |
| **Test Engineer** | SECURITY (vulnerabilities), QUALITY (coverage, repeated failures) |
| **Architect** | SCOPE (design contradictions), ETHICS (architectural implications) |

---

## Policy Checkpoints

| Checkpoint | When | Question |
|------------|------|----------|
| **Pre-CODE** | Before CODE phase | Does architecture align with principles? |
| **Pre-Edit** | Before Edit/Write tools | Is this application code? Delegate if yes. |
| **Pre-Merge** | Before creating PR | Tests passing? System integrity maintained? |
| **On Conflict** | Specialists disagree | What do project values dictate? |
| **On Blocker** | Normal flow blocked | Operational (imPACT) or viability threat (escalate)? |

---

## S5 Decision Framing Protocol

When escalating to user, present decision-ready options (not raw information):

```
{ICON} {TYPE}: {One-line summary}
**Context**: [2-3 sentences]
**Options**:
A) {Label} - Action: [what] / Trade-off: [gain vs cost]
B) {Label} - Action: [what] / Trade-off: [gain vs cost]
**Recommendation**: {Option} - [rationale]
```

**Icons**: S3/S4 Tension, Scope Change, Technical Choice, Risk, Principle Conflict, HALT, ALERT

**Guidelines**:
- Limit to 2-3 options (avoid paralysis)
- Lead with recommendation
- Quantify when possible ("~30 min" not "some time")
- State trade-offs explicitly

---

## S5 Delegation Boundaries

| Orchestrator CAN Decide | Orchestrator MUST Escalate |
|------------------------|---------------------------|
| Which specialist to invoke | S3/S4 tension unresolved |
| Task sequencing within phase | Principle conflicts |
| imPACT triage (operational) | Unclear non-negotiable boundaries |
| Agent coordination | HALT signal acknowledgment |
| Documentation updates | Policy override requests |

**Rule**: Orchestrator operates *within* policy. User is ultimate S5 authority.

---

## META-BLOCK Recovery Protocol

When 3+ imPACT cycles fail, emit ALERT: META-BLOCK with these options:

| Option | Action | Trade-off |
|--------|--------|-----------|
| **A) Restart PREPARE** | Re-examine requirements | Time cost, but reveals misunderstanding |
| **B) Escalate to user** | Ask for direction | Blocks progress, but gets judgment |
| **C) Reduce scope** | Defer problematic part | Partial delivery, but unblocks |
| **D) Add expertise** | Bring specialist help | Coordination cost, but fresh eyes |

---

## Quick Decision Guide

**When blocked, ask**: Is this a viability threat (security/data/ethics)?
- **YES** -> Emit ALGEDONIC signal
- **NO** -> Use imPACT triage
- **3+ imPACT failures** -> Emit ALGEDONIC ALERT: META-BLOCK

**Before any significant decision**:
- [ ] SACROSANCT rules respected?
- [ ] Application code delegated?
- [ ] Algedonic triggers checked?
- [ ] User decision framed with options?
