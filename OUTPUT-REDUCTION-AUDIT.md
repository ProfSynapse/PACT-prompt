# User Output Reduction Audit

> **Scope**: Opportunities to reduce AI output *to the user* only.
> **Exclusions**: Internal AI prompts, inter-agent communication (orchestrator ↔ specialists).
> **Date**: 2026-01-25

---

## Executive Summary

This audit identifies **23 specific opportunities** to reduce user-facing output across the PACT framework. The existing codebase already emphasizes conciseness (see "Output Conciseness" sections in commands), but several areas still produce verbose output that could be streamlined.

**Impact Areas**:
1. **Hook Scripts** (8 opportunities) - System messages that could be shorter or conditional
2. **Command Files** (7 opportunities) - Verbose guidance that could be trimmed
3. **Orchestrator Config** (4 opportunities) - Communication patterns that could be tightened
4. **Protocols** (4 opportunities) - Templates with excessive boilerplate

---

## Detailed Findings

### 1. Hook Scripts

#### 1.1 `memory_prompt.py` - Overly Aggressive Memory Prompts
**File**: `pact-plugin/hooks/memory_prompt.py:96-115`

**Current**: Emits verbose 7-line mandatory warning on every session stop with PACT activity:
```
⚠️ MANDATORY: You MUST delegate to pact-memory-agent NOW to save session context:
- PACT work completed with: pact-backend-coder
- Decisions made (MUST capture rationale + alternatives)
- Lessons learned (MUST preserve for future sessions)
- Blockers resolved (MUST document for next time)

This is NOT optional. Failure to save = lost context = repeated work.
```

**Recommendation**: Reduce to single-line prompt:
```
💾 Consider saving session context via pact-memory-agent (decisions, lessons, blockers detected)
```

**Rationale**: The current language ("MANDATORY", "MUST", "NOT optional") is aggressive and repetitive. Users who want memory will use it; those who don't will be annoyed by the nag.

---

#### 1.2 `phase_completion.py` - Verbose Reminder Messages
**File**: `pact-plugin/hooks/phase_completion.py:141-153`

**Current**: Two separate multi-line reminders:
```
CODE Phase Reminder: Decision logs should be created at docs/decision-logs/{feature}-{domain}.md to document key implementation decisions and trade-offs.

TEST Phase Reminder: Consider invoking pact-test-engineer to verify the implementation.
```

**Recommendation**: Combine into single concise reminder:
```
📋 CODE complete: Consider decision log + test phase
```

**Rationale**: The full path template is rarely useful mid-conversation; users can look it up if needed.

---

#### 1.3 `validate_handoff.py` - Verbose Warning Format
**File**: `pact-plugin/hooks/validate_handoff.py:137-143`

**Current**:
```
PACT Handoff Warning: Agent 'pact-backend-coder' completed without proper handoff. Missing: what was produced, key decisions. Consider including: what was produced, key decisions, and next steps. See pact-protocols.md for handoff format.
```

**Recommendation**: Shorten to:
```
⚠️ Handoff incomplete (missing: produced, decisions). See pact-protocols.md
```

---

#### 1.4 `file_size_check.py` - Verbose Guidance Block
**File**: `pact-plugin/hooks/file_size_check.py:66-84`

**Current**: 8-line block with SOLID/DRY explanation and recommendation.

**Recommendation**: Reduce to:
```
📏 {filename}: {line_count} lines (>600). Consider refactoring via pact-architect.
```

**Rationale**: Users familiar with the codebase don't need SOLID/DRY explained each time.

---

#### 1.5 `session_init.py` - Verbose Symlink Status
**File**: `pact-plugin/hooks/session_init.py:59-96`

**Current**: Reports detailed symlink operations:
```
PACT: protocols updated, 3 agents linked, 2 agents updated
```

**Recommendation**: Only report on first install or failures:
- First install: `PACT installed`
- Updates: Silent (no output)
- Failures: Keep current format

---

#### 1.6 `compaction_refresh.py` - Verbose Skip Messages
**File**: `pact-plugin/hooks/compaction_refresh.py:136-161`

**Current**: Reports validation failures:
```
Refresh skipped: checkpoint validation failed
```

**Recommendation**: Remove these messages entirely—user doesn't need to know refresh was attempted and skipped.

---

#### 1.7 `hooks.json` - Date/Time Echo on Every Prompt
**File**: `pact-plugin/hooks/hooks.json:27-36`

**Current**: Every `UserPromptSubmit` echoes:
```
Current date/time: 2026-01-25 14:30:45 UTC
```

**Recommendation**: Remove this hook entirely. The AI model has access to date/time, and displaying it to users on every prompt is noise.

---

#### 1.8 `memory_enforce.py` - Presumed Verbose (Not Read)
**File**: `pact-plugin/hooks/memory_enforce.py`

**Recommendation**: Audit this file for similar verbosity patterns.

---

### 2. Command Files

#### 2.1 `orchestrate.md` - Explicit Mode Announcements
**File**: `pact-plugin/commands/orchestrate.md:59-64`

**Current guidance says to avoid**:
```
"S4 Mode — Task Assessment"
```

**But still includes in documentation**:
```
When transitioning to S4 mode, pause and ask: "Are we still building the right thing..."
```

**Recommendation**: Add explicit instruction to NOT announce mode transitions to user:
```markdown
**Never announce mode to user**: Mode names (S3, S4) are internal concepts. Don't output "S4 Mode" or "S3 Mode".
```

---

#### 2.2 `plan-mode.md` - Verbose Plan Summary
**File**: `pact-plugin/commands/plan-mode.md:414-417`

**Current concise example**:
```
Plan saved. Complexity: Medium. 3 decisions need your input.
```

**But the plan template itself (lines 227-398)** is very long. The output includes:
- Full specialist perspectives with effort levels
- Detailed tables for components, decisions, files
- Risk assessment tables
- Cross-cutting concerns

**Recommendation**: Add a "Summary Mode" option that outputs just:
```
Plan saved to docs/plans/{slug}-plan.md
Complexity: {level} | Decisions needed: {N} | Est. files: {M}
```

Full plan still written to file; user can read it there.

---

#### 2.3 `peer-review.md` - Excessive Question Flow
**File**: `pact-plugin/commands/peer-review.md:69-102`

**Current**: Multi-step questioning process:
1. Gate question: "Would you like to review minor and future recommendations?"
2. Per-recommendation questions with "More context" option
3. Re-asking after providing context

**Recommendation**: Streamline to single batch question:
```
Minor/Future items found. Quick options:
A) Address all minor now
B) Skip all
C) Review individually
```

---

#### 2.4 `comPACT.md` - Auto-Selection Announcement
**File**: `pact-plugin/commands/comPACT.md:37`

**Current**: `Auto-selected: database (SQL keywords detected)`

**Recommendation**: Just proceed with delegation without announcing the selection rationale:
```
Delegating to pact-database-engineer
```

---

#### 2.5 `imPACT.md` - Diagnostic Format
**File**: `pact-plugin/commands/imPACT.md:65-68`

**Current concise example is good**:
```
imPACT: Redo ARCHITECT — interface mismatch
```

**Recommendation**: Ensure this format is consistently enforced. Add negative example:
```markdown
| Verbose (avoid) | Concise (prefer) |
| "After analyzing the blocker, I've determined that..." | `imPACT: [outcome] — [reason]` |
```

---

#### 2.6 `rePACT.md` - Nested Cycle Announcements
**File**: `pact-plugin/commands/rePACT.md:105-108`

**Current verbose examples to avoid**:
```
"Starting mini-PREPARE phase for the nested cycle..."
"The nested cycle has completed successfully..."
```

**Recommendation**: Strengthen guidance to single-line only:
```
rePACT: backend "OAuth2 refresh" → complete
```

---

#### 2.7 `wrap-up.md` - Verbose Status Report
**File**: `pact-plugin/commands/wrap-up.md:24-31`

**Current**:
```
Docs updated: [List files]
Files archived: [List files]
Temp files deleted: [List files]
Status: READY FOR COMMIT / REVIEW
```

**Recommendation**: Reduce to:
```
Cleanup: {N} docs updated, {M} temp files removed. Ready for commit.
```

Or if nothing done: `Workspace clean.`

---

### 3. Orchestrator Config (CLAUDE.md)

#### 3.1 Identity Prefix
**File**: `pact-plugin/CLAUDE.md:205`

**Current**: `Start every response with "🛠️:" to maintain consistent identity`

**Recommendation**: Consider removing this requirement. The emoji prefix adds noise to every message and users know they're talking to PACT.

---

#### 3.2 Phase Explanation
**File**: `pact-plugin/CLAUDE.md:207`

**Current**: `Explain which PACT phase you're operating in and why`

**Recommendation**: Change to: `State phase only when transitioning (not every response)`

---

#### 3.3 Principle Reference
**File**: `pact-plugin/CLAUDE.md:208`

**Current**: `Reference specific principles being applied`

**Recommendation**: Remove this requirement. Users don't need to know "applying Single Responsibility principle" - just do it.

---

#### 3.4 Verbose Delegation Warnings
**File**: `pact-plugin/CLAUDE.md:232-236`

**Current**: Multiple warning blocks about delegation:
```
⚠️ Bug fixes, logic, refactoring, tests—NOT exceptions. DELEGATE.
⚠️ "Simple" tasks, post-review cleanup—NOT exceptions. DELEGATE.
⚠️ Urgent fixes, production issues—NOT exceptions. DELEGATE.
⚠️ Rationalizing "it's small"... = failure mode. DELEGATE.
```

**These are internal instructions** and should NOT be output to user. Add explicit note:
```markdown
> Note: These delegation rules are for orchestrator behavior, not user-facing output.
```

---

### 4. Protocols

#### 4.1 `algedonic.md` - Signal Format Verbosity
**File**: `pact-plugin/protocols/algedonic.md:38-45`

**Current signal template**:
```
⚠️ ALGEDONIC [HALT|ALERT]: {Category}

**Issue**: {One-line description}
**Evidence**: {Specific details}
**Impact**: {Why this threatens viability}
**Recommended Action**: {What you suggest}
```

**Recommendation**: Provide abbreviated format for ALERT (keep full format for HALT):
```
⚠️ ALERT: {Category} — {One-line issue}. Action: {recommendation}
```

Full format only for HALT since those require user decision.

---

#### 4.2 `pact-s5-policy.md` - Decision Framing Template
**File**: `pact-plugin/protocols/pact-s5-policy.md:82-99`

**Current**: 15+ line template for every escalation.

**Recommendation**: Add "Quick Frame" option for low-stakes decisions:
```
{ICON} {summary}? A) {option1} B) {option2}
```

Reserve full template for high-stakes only.

---

#### 4.3 Handoff Format (referenced in orchestrate.md)
**File**: `pact-plugin/commands/orchestrate.md:170-177`

**Current**:
```
1. **Produced**: Files created/modified
2. **Key context**: Decisions made, patterns used, assumptions
3. **Areas of uncertainty**: Where bugs might hide, tricky parts
4. **Open questions**: Anything unresolved
```

**This is agent-to-orchestrator communication** (excluded from this audit), but when the orchestrator **summarizes** handoffs to user, it should be condensed.

**Recommendation**: Add guidance:
```markdown
When reporting handoff to user, summarize as:
`{agent} complete: {N} files, {key decision if notable}. Proceeding to {next}.`
```

---

#### 4.4 Plan Template Length
**File**: `pact-plugin/commands/plan-mode.md:227-398`

**Current**: 170+ line template with many optional sections.

**Recommendation**: Mark sections as "include only if non-empty":
- Limitations section: Only if gaps exist
- Risk Assessment: Only if risks identified
- Cross-Cutting Concerns: Only if notable

---

## Implementation Priority

### High Priority (Immediate User Experience Impact)
1. **Memory prompt verbosity** (1.1) - Most frequent annoyance
2. **Date/time echo removal** (1.7) - Noise on every prompt
3. **Phase completion reminders** (1.2) - Frequent and verbose
4. **Identity prefix** (3.1) - Every response

### Medium Priority (Workflow Improvements)
5. **File size check verbosity** (1.4)
6. **Handoff validation format** (1.3)
7. **Mode announcement guidance** (2.1)
8. **Plan summary mode** (2.2)

### Lower Priority (Polish)
9. **Symlink status** (1.5)
10. **Compaction skip messages** (1.6)
11. **Review question flow** (2.3)
12. **Signal format variants** (4.1)

---

## Summary Table

| # | Location | Current | Proposed | Impact |
|---|----------|---------|----------|--------|
| 1.1 | memory_prompt.py | 7-line mandatory warning | 1-line suggestion | High |
| 1.2 | phase_completion.py | 2 multi-line reminders | 1 short reminder | High |
| 1.3 | validate_handoff.py | 50+ char warning | 30 char warning | Medium |
| 1.4 | file_size_check.py | 8-line guidance | 1-line alert | Medium |
| 1.5 | session_init.py | Always report symlinks | Report only on install/fail | Low |
| 1.6 | compaction_refresh.py | Report skip reasons | Silent skip | Low |
| 1.7 | hooks.json | Echo date/time every prompt | Remove hook | High |
| 2.1 | orchestrate.md | May announce modes | Never announce modes | Medium |
| 2.2 | plan-mode.md | Full output | Summary + file | Medium |
| 2.3 | peer-review.md | Multi-step questions | Batch question | Medium |
| 2.4 | comPACT.md | Announce selection | Silent selection | Low |
| 2.5 | imPACT.md | (already good) | Add negative example | Low |
| 2.6 | rePACT.md | Verbose cycle msgs | Single-line only | Low |
| 2.7 | wrap-up.md | List format | Count format | Low |
| 3.1 | CLAUDE.md | 🛠️: prefix required | Remove requirement | High |
| 3.2 | CLAUDE.md | Explain phase always | Phase on transition only | Medium |
| 3.3 | CLAUDE.md | Reference principles | Remove requirement | Medium |
| 3.4 | CLAUDE.md | Delegation warnings | Mark as internal-only | Low |
| 4.1 | algedonic.md | Full format always | Quick format for ALERT | Medium |
| 4.2 | pact-s5-policy.md | 15-line template | Quick frame option | Medium |
| 4.3 | orchestrate.md | 4-item handoff summary | 1-line summary | Medium |
| 4.4 | plan-mode.md | All sections always | Conditional sections | Low |

---

## Next Steps

1. Review this audit with stakeholders
2. Prioritize based on user feedback
3. Implement changes incrementally (high priority first)
4. Measure impact through user satisfaction
