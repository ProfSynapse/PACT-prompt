## Phase Skip Completeness Check

> **Purpose**: Prevent premature phase skipping by requiring positive evidence of completeness.
> A section or document existing does NOT mean the work is done.

---

### Core Principle

**Existence does not equal Completeness.** Before skipping any phase, verify POSITIVE evidence that the phase's work is already done. "Plan exists" or "docs present" is insufficient — you must confirm the content is complete for the scope at hand.

---

### The 6 Incompleteness Signals

Any of these signals means the phase is **REQUIRED** (do not skip):

| # | Signal | What to Look For |
|---|--------|------------------|
| 1 | **Unchecked checkboxes** | `[ ]` items remain in the relevant plan section |
| 2 | **TBD/placeholder language** | "TBD", "to be determined", "placeholder", "TODO" |
| 3 | **Forward references** | Standardized: "Handled during {PHASE}". Informal variants: "handled during PREPARE", "deferred to ARCHITECT", "addressed in [PHASE]" |
| 4 | **Unresolved questions** | Items in "Open Questions > Require Further Research" that map to this phase |
| 5 | **Empty or stub sections** | Section header exists but content is missing or minimal |
| 6 | **Explicit phase requirement** | Plan's "Phase Requirements" section lists this phase as REQUIRED |

---

### Backward Compatibility

Plans created before this convention (without a "Phase Requirements" section) are evaluated using signals 1-5 only. The absence of a Phase Requirements section is NOT itself an incompleteness signal.

---

### Skip Justification

When skipping any phase, state WHY briefly and confirm completeness:

**Good** (confirms completeness):
- `Skipping PREPARE: all 4 research items checked, no TBD language, no forward references`
- `Skipping ARCHITECT: plan Architecture section complete, all decisions resolved`

**Bad** (does not confirm completeness):
- `Skipping PREPARE (approved plan exists)` — too vague, does not confirm completeness

---

### Context-Specific Usage

Different workflows apply completeness checks in different contexts:

| Workflow | Context |
|----------|---------|
| **orchestrate** | Check plan sections before skipping PREPARE, ARCHITECT, or TEST phases |
| **rePACT** | Check parent phase outputs for sub-task scope coverage before skipping mini-phases |
| **imPACT** | Check prior phase outputs for completeness when diagnosing blockers — incomplete outputs suggest redoing the phase |
| **comPACT** | Flag unresolved items found in existing docs during light-ceremony work |
| **plan-mode** | Produces the signals (checkboxes, TBD markers, Phase Requirements table); uses this protocol to populate the Phase Requirements section |

---
