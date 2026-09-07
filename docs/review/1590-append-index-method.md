# Review Synthesis: 1590-append-index-method (PR #1611)

**Scope**: two commits — 7284a456 (rule wording + pin module) and 9d3c35ea (version bump 4.7.9 → 4.7.10).
**Reviewers**: architect (design coherence), test-engineer (pin quality/coverage), backend-coder (implementation craftsmanship, independence limitation declared — builder self-read, compensated by measurement-anchored passes).
**Prior independent verification**: auditor GREEN on all 8 staged-diff claims; full-suite gate GREEN (15,542 passed / 0 errors / rc=0, collect-twice delta 0).

## Verdict

All three reviewers GREEN. **Zero blocking findings.** The design is coherent against issue #1590, the pins are load-bearing and non-vacuous (measured), and the implementation is verbatim-faithful to the design.

## Findings

| # | Finding | Severity | Reviewer | Disposition |
|---|---------|----------|----------|-------------|
| 1 | Absence-pin rationale sentence has inverted flip-logic in two copies (`test_index_append_method_pinned.py:38-42`, `:164-168`) — says presence pins "stay green if the clauses are merely deleted alongside", but deletion flips presence RED; the absence pins' unique catch is the retired phrase restored ALONGSIDE the new clauses (merge-muddle co-existence). Pins correct; prose wrong. | Minor | architect | **Fix now** (greedy) — test-engineer as fixer |
| 2 | `docs/preparation/1590-append-index-method.md` untracked while the committed architecture doc cites it as input — dangling reference post-merge. | Minor | architect | **Fix now** — lead commits it (`git add -f`) |
| 3 | Lead-surface stale-anchor RESPONSE clause `re-read from disk, re-anchor, and retry` is unpinned — a measured deletion probe leaves pins 9+10 green. One-tuple addition recommended by the finder. | Minor | test-engineer | **Fix now** (greedy) — test-engineer as fixer |
| 4 | False-trip shape: a scope-preserving reword restoring the contiguous retired prefix would trip the absence pins with retired-scope semantics untouched. Low likelihood; the pin text already carries the deliberate-update escape hatch. | Minor | test-engineer | **Record only** — no actionable fix beyond the designed escape hatch |
| 5 | `_lines_outside_fences` copied into the new module but unused (no heading pins in this module). | Minor/Future | backend-coder (minor), architect (future), test-engineer (informational) | **Excluded from remediation** — the per-module helper-duplication convention (architecture §4, matching the existing template modules) mandates the triplet copy; removing it would diverge from the pinned convention. Revisit only if a lint ever complains. |

## Reviewer open_questions dispositions

| Reviewer | Question | Disposition |
|----------|----------|-------------|
| test-engineer | Adopt the one-tuple pin addition in this PR or let it ride? (recommendation: add) | **Ruled: adopt** — in-scope (the clause is this PR's own acceptance-criterion-2 text), one-tuple diff, measured gap |
| architect | Two minors: fix pre-merge or accept as-is? | **Ruled: fix both pre-merge** — both are one-command fixes and were introduced by this PR |
| backend-coder | None | — |

## Greedy-fix note

`PR greedy-fix: ON` — minor findings batched into remediation without the per-finding gate. Exclusions surfaced: finding 4 (record-only, escape hatch by design), finding 5 (convention-mandated helper duplication; removal would violate the pinned per-module triplet convention).
