# Architecture: #1590 — Append-Not-Rewrite Method Gap

Worktree: `/Users/mj/Sites/collab/PACT-prompt/.worktrees/fix/1590-append-index-method`. Paths below are relative to `pact-plugin/` in the worktree. Input: `docs/preparation/1590-append-index-method.md` (surface census, satellite convention, pin-harness conventions, gap analysis).

## 1. Executive Summary

Three wording edits and one new pin module. The rule's two carrying surfaces — `skills/pact-agent-teams/SKILL.md:540` (canonical, R1) and `agents/pact-orchestrator.md:607` (lead variant, R2) — each gain (a) the forbidden method family named explicitly, including the shell one-liner form, and (b) stale-anchor `Edit` failure semantics. R1 additionally gains (c) the presence-check procedure, placed at the roll-up paragraph (`:542`), with R2 carrying (c) as a pointer only — per the team-lead's ruling: method + stale-anchor are point-of-action stop-rules the lead's own surface must contain; presence-check is a rarer audit-time operation where a pointer suffices, and drift-avoidance is served by per-surface pins rather than duplication. A new test module `tests/test_index_append_method_pinned.py` pins every phrase that lands, on each surface it lands on. No `protocols/` surface is touched; the SSOT byte-mirror gate does not fire.

## 2. Decisions

### D1 — Placement of the presence-check procedure: the roll-up paragraph (`:542`), not the index-upkeep paragraph (`:540`)

The dispatch left this open (index-upkeep paragraph vs beside the roll-up rule). Decision: `:542`, appended after its closing hazard sentence ("no later reader can tell the difference between a memory you retired and one you lost"). Three reasons:

1. **Adjacency to its own hazard.** The misread the check prevents (absent-from-`MEMORY.md` reads as lost update) is the audit-direction instance of the lost/retired indistinguishability that `:542` already states. The check is that sentence's remedy; it belongs in the same breath.
2. **Satellites are defined in context.** `:540` is already the densest paragraph in the skill (limits, naming convention, placement, method, refuse-compaction, anticipated-instruction, self-measure). `:542` is where roll-up and pointer semantics live; the check presupposes exactly that context.
3. **Forward reference is one line away.** The reachability command is printed at `:544`, immediately after `:542`; "the reachability command below" resolves without the reader hunting.

### D2 — Stale-anchor failure semantics: generalized into the `:540` rule, `:544` left unchanged

The existing failure text at `:544` ("If the `Edit` reports no match, the file changed while you were working — STOP, re-run the command, and apply the fresh block") is scoped to the emit-edit pointer-placement flow. Rather than duplicate it, the general form goes into the `:540` append rule itself (re-read, re-anchor, retry, never fall back to a rewrite). `:544` stays as the specialized instance (its remedy is correctly "re-run the command", since the anchor comes from a freshly printed block). The two texts do not contradict: the general rule names the response class; the specialized rule names the concrete re-run step for that flow.

### D3 — R2 (`:607`) mirroring: method + stale-anchor inline, presence-check as pointer

Per the team-lead's ruling on the teachback's least-confident item. The lead was an observed near-miss writer (scripted rewrite at the moment of append), so the stop-rule must be on the lead's surface at the point of action. The presence-check is audit-time; the pointer tail ("for the enforced limits and the satellite presence-check") routes to the canonical home. The pin module covers each surface's required phrases, which is what keeps the two surfaces from drifting — not full restatement.

### D4 — Micro-drift repair in R2: restore the "of your agent type" qualifier

The prep flagged that `:607` drops R1's type-keyed mechanism qualifier ("other instances of your agent type … other projects and other sessions"). The sentence is being edited anyway; restoring "of your agent type" is three words inside an already-touched clause and makes the mechanism accurate on the lead surface. **Flagged for lead review** — it is beyond the four acceptance criteria and may be struck without affecting any of them. The full "other projects and other sessions" tail is NOT restored: R2 is the lead persona, whose index is written by lead instances; the shorter qualifier suffices and keeps R2 short per its variant role.

### D5 — Protocols/ untouched (confirmed)

The prep's negative result (§1e) is confirmed by this phase's own sweep: the contingency paraphrase grep (`clobber|trample|overwrite the|overwrites the|stomps` over `agents/ skills/ commands/ protocols/`) returned only unrelated uses (pact-memory SQLite column semantics, handoff-harvest internals) — no out-of-net variant of the index rule. The surface list stands at R1 + R2 + four pointer sites. `scripts/verify-protocol-extracts.sh` / `test_audit_protocol.py` are unaffected.

### D6 — Pointer sites P1–P4 unchanged

P1 (`pact-orchestrator.md:603`), P2/P3 (`pact-memory/SKILL.md:480,482`), P4 (skill frontmatter `description`, `pact-agent-teams/SKILL.md:6`) name the rule without restating it; every phrase they carry ("append discipline that protects entries you did not write", "index-upkeep rule", "append to a shared index without dropping another instance's entries") remains literally true after the edits. Single-source discipline: no restatement added anywhere.

## 3. Exact Wording

### Edit 1 — R1 rule sentence, `skills/pact-agent-teams/SKILL.md:540`

OLD (one sentence inside the index-upkeep paragraph):

> Make that append with an `Edit` against the file as it is on disk, never a whole-file rewrite from a copy you read earlier — other instances of your agent type write this same index, including instances in other projects and other sessions, and a rewrite silently drops whatever they added while you worked.

NEW (three sentences, same position):

> Make that append with an `Edit` against the file as it is on disk, never a whole-file rewrite however produced — not from a copy you read earlier, and not from a scripted read-replace-write: `read_text()` → `replace()` → `write_text()` in one shell command is still a whole-file rewrite. Other instances of your agent type write this same index, including instances in other projects and other sessions, and a rewrite silently drops whatever they added while you worked. If the `Edit` fails because its anchor no longer matches, another instance wrote while you were working — re-read the file from disk, re-anchor on the fresh text, and retry the `Edit`. Never answer a failed `Edit` with a rewrite: the stale-anchor failure is the lost-update protection working, not a broken tool.

Notes:

- Acceptance 1 is met by naming the one-liner's exact call sequence (`read_text()` → `replace()` → `write_text()`), the form both observed near-misses used.
- The closing clause of the last sentence ("the stale-anchor failure is the lost-update protection working, not a broken tool") is the one justification in the new text. It earns its place under the bare-instructions rule's deviation exception: an agent's default reading of a failed `Edit` is "the tool broke, work around it" — the workaround being the scripted rewrite this rule forbids. The clause overrides that reading at the point it forms.
- Scope: every clause is about "this index" / "that append" — no universal claim about scripts. The sibling opposite-remedy rules (pact-backlog's run-the-command CAS family; handoff-ledger append-only) are about other stores and are not contradicted.

### Edit 2 — R1 roll-up tail, `skills/pact-agent-teams/SKILL.md:542`

Append two sentences after the paragraph's closing sentence ("…no later reader can tell the difference between a memory you retired and one you lost."):

> The same ambiguity cuts the other way: an entry absent from this index may be correctly filed in a satellite. Before reporting an entry as lost, check the `MEMORY-*.md` and `INDEX_*.md` satellites the preamble names — and run the reachability command below without `--emit-edit`, which reports every leaf no index still points at.

Notes:

- Acceptance 3 is met by naming the satellite indexes explicitly (`MEMORY-*.md`, `INDEX_*.md` — the two live-roll-up prefixes from the `:540` preamble; `ARCHIVE_*.md` is deliberately excluded: an entry under audit for loss is a live entry, and archive membership means retired, not lost).
- "The reachability command below" resolves at `:544`, the next paragraph. Verified against `scripts/memory_reachability.py`: without `--emit-edit` it reports unreachable leaves without writing; with it, it additionally prints the pointer-placement block.

### Edit 3 — R2 paragraph, `agents/pact-orchestrator.md:607`

OLD:

> You keep a persistent agent-memory index of your own, and it is subject to the same head-of-index limits as every specialist's. Append to it with an `Edit` against the file as it is on disk, never a whole-file rewrite from a copy you read earlier — other instances write that same index, and a rewrite silently drops whatever they added while you worked. Keep pointers in the head, where they survive the cut. See the index-upkeep rule in [pact-agent-teams](../skills/pact-agent-teams/SKILL.md) for the enforced limits.

NEW:

> You keep a persistent agent-memory index of your own, and it is subject to the same head-of-index limits as every specialist's. Append to it with an `Edit` against the file as it is on disk, never a whole-file rewrite however produced — a scripted read-replace-write from a shell one-liner (`read_text()` → `replace()` → `write_text()`) rewrites the whole file just the same. Other instances of your agent type write that same index, and a rewrite silently drops whatever they added while you worked. If the `Edit` fails on a stale anchor, the file changed under you — re-read from disk, re-anchor, and retry; never answer a failed `Edit` with a rewrite. Keep pointers in the head, where they survive the cut. See the index-upkeep rule in [pact-agent-teams](../skills/pact-agent-teams/SKILL.md) for the enforced limits and the satellite presence-check.

Notes:

- Method + stale-anchor inline per D3; presence-check as pointer tail per D3.
- "of your agent type" restored per D4 (flagged; strikable).
- `POINTER_TOKEN = "index-upkeep rule"` (pinned by `test_agent_memory_cap_single_source.py`) is preserved verbatim in the tail sentence.
- No limits restatement: the tail stays pointer-only, so the single-source pin's unit-vocabulary and subject-tainted arms stay green.

### Planning-artifact check

None of the new rule text carries an issue number, task id, PR ref, or version marker. The design-doc-only references (this file) are not LLM-loaded surfaces.

## 4. Pin Design — `tests/test_index_append_method_pinned.py` (new module)

Per the prep's §3d, precedent-consistent choice: a new module rather than tuples in an existing `PHRASE_PINS`, because neither existing pin module is thematically about the memory-index rule. The module copies the three helpers (`_phrase`, `_normalized`, `_lines_outside_fences`) from `test_wake_ordering_pinned.py` — duplication is the established convention, not a smell.

Structure: docstring-first (template: `test_wake_ordering_pinned.py`), `PLUGIN_ROOT`, two surface constants (`SKILL`, `ORCHESTRATOR`), one `PHRASE_PINS` list, one parametrized presence test, one parametrized absence test. No `HEADING_PINS` (no new section is added). No `EXPECTED_COUNTS` (no phrase is intended to recur a fixed number of times per surface — same rationale wake_ordering's docstring records). No mirror discipline (the rule has no `protocols/` presence — D5).

### PHRASE_PINS (presence) — 11 cases

Stored without backticks; `_phrase` normalization strips backticks and collapses whitespace on both sides, so hard-wrapping and inline-code rendering do not flip a pin, while a re-wording does.

SKILL surface:

| # | Phrase | Load-bearing for | Flip shape |
|---|--------|------------------|------------|
| 1 | `never a whole-file rewrite however produced` | Scope generalization marker | Revert to two-step-only scope |
| 2 | `read_text() → replace() → write_text() in one shell command is still a whole-file rewrite` | Acceptance 1 — names the one-liner form | Method name erodes or is deleted |
| 3 | `re-read the file from disk, re-anchor on the fresh text, and retry the Edit` | Acceptance 2 — the response | Response clause deleted |
| 4 | `Never answer a failed Edit with a rewrite` | Anti-fallback clause (sentence-initial capital N on this surface) | Fallback prohibition erodes |
| 5 | `check the MEMORY-*.md and INDEX_*.md satellites the preamble names` | Acceptance 3 — names the satellite indexes | Check loses its target naming |
| 6 | `without --emit-edit, which reports every leaf no index still points at` | Audit-direction procedure | Tool reference deleted |

ORCHESTRATOR surface:

| # | Phrase | Load-bearing for | Flip shape |
|---|--------|------------------|------------|
| 7 | `never a whole-file rewrite however produced` | Method scope on lead surface | R2 reverts independently of R1 |
| 8 | `a scripted read-replace-write from a shell one-liner` | Acceptance 1 on lead surface | Method name erodes on R2 |
| 9 | `If the Edit fails on a stale anchor, the file changed under you` | Acceptance 2 on lead surface | Stale-anchor semantics deleted on R2 |
| 10 | `never answer a failed Edit with a rewrite` | Anti-fallback (lowercase n — mid-sentence on this surface; distinct case from pin 4 by design) | Fallback prohibition erodes on R2 |
| 11 | `for the enforced limits and the satellite presence-check` | D3 pointer tail — presence-check routed to canonical home | Pointer deleted, R2 silently uncovered |

### ABSENCE_PINS — 2 cases

| # | Surface | Retired phrase | Why |
|---|---------|----------------|-----|
| 12 | SKILL | `never a whole-file rewrite from a copy you read earlier` | The pre-fix two-step-only scope; a revert restores it while pins 1–6 stay green if the new clauses are merely deleted alongside — this pin is red pre-fix, green post-fix |
| 13 | ORCHESTRATOR | same | Same regression shape on the lead surface |

### Counter-test-by-revert (authoring-time, per convention)

Revert both doc surfaces to pre-change state (`git checkout <pre-fix-ref> -- <2 doc paths>`; restore with `git checkout HEAD -- <paths>`; or run in a temp clone per the wake_ordering cycle-2 precedent). Expected flip-set: all 13 parametrized cases fail (11 presence + 2 absence). Record the observed cardinality in the module docstring and the dated module-bottom comment, per the convention.

## 5. Files Touched / Not Touched

Touched (3 files, one commit):

1. `skills/pact-agent-teams/SKILL.md` — Edits 1 + 2
2. `agents/pact-orchestrator.md` — Edit 3
3. `tests/test_index_append_method_pinned.py` — new

Not touched, with the pin-triage that proves each stays green (grep+categorize+decide sweep over `tests/` for both in-scope file stems):

| Test module | Pin type on in-scope file | Verdict |
|-------------|---------------------------|---------|
| `test_agent_memory_cap_single_source.py` | Pointer-resolution (`POINTER_TOKEN = "index-upkeep rule"` in orchestrator; `RULE_HEADING = "Index upkeep"` in SKILL) + limits single-source arms | Preserved: token kept verbatim in Edit 3's tail; heading kept; no limits restatement added |
| `test_handoff_key_annotation_pinned.py` | Count pin (`EXPECTED_COUNTS[SKILL] = 1`, three markers) | Markers live at SKILL.md:267, outside both edit regions; counts unchanged |
| `test_wake_ordering_pinned.py`, `test_dual_channel_acceptance_pinned.py`, `test_read_trigger_precondition_pinned.py` | Phrase pins on SKILL + ORCHESTRATOR | Zero phrase overlap with edit regions (verified by grep for `whole-file`, `pointers go in the head`, `survive the cut`, `enforced limits`, `satellite`, `memory you retired`) |
| `test_skills_structure.py` / `test_agents_structure.py` | Structure + character budget | `MAX_SKILL_CHARS` (18347) is scoped to `pact-teachback/SKILL.md` only; no budget on either in-scope file |
| `test_cross_references.py`, `test_lazy_load_cross_references.py` | Link resolution | The `[pact-agent-teams](../skills/pact-agent-teams/SKILL.md)` link is preserved in Edit 3 |

Also untouched: `:544` (D2), pointer sites P1–P4 (D6), all `protocols/` surfaces (D5), sibling rules S1/S2 (other stores, other remedies — no contradiction introduced).

## 6. Implementation Order

One commit: the three wording edits and the new pin module land together. The pins are red without the wording; the wording unpinned fails acceptance 4 — the halves are not independently shippable. Authoring-time counter-test-by-revert runs before the commit is offered; its flip-set cardinality goes in the module docstring. Merge gate: full suite from the `pact-plugin` root with no path argument (`python3 -m pytest -q`), errors token scanned.

## 7. Acceptance Mapping

| Issue criterion | Where met |
|-----------------|-----------|
| Forbidden shape names the shell one-liner form explicitly | Edit 1 (`read_text()` → `replace()` → `write_text()` in one shell command) + Edit 3; pins 2, 8 |
| Stale-anchor `Edit` failure documented with its correct response | Edit 1 sentences 3–4 + Edit 3 sentence 3; pins 3, 4, 9, 10 |
| Presence-check guidance names the satellite indexes | Edit 2 (`MEMORY-*.md` and `INDEX_*.md` named) + pointer in Edit 3; pins 5, 6, 11 |
| A test pins whichever of these lands in an instruction surface | `tests/test_index_append_method_pinned.py`, 13 cases |

## 8. Risks

- **Unicode arrows in pins.** The `→` in pin 2 is literal text on both sides of `_phrase` normalization; the coder must copy it exactly. Mitigation: the pin tuple carries the exact character, and the counter-test proves the match.
- **R1/R2 drift over time.** Accepted by design (D3, lead ruling): the per-surface pin set is the drift tripwire; a silent divergence flips the surface-specific case.
- **D4 scope.** The "of your agent type" restoration is the only text beyond the issue's four criteria; it is flagged for the lead and strikable without affecting any pin except none — no pin covers that qualifier.

## 9. Reasoning Chain (for HANDOFF)

Placement (D1) follows from where each hazard's vocabulary already lives: the method gap and its failure semantics belong at the append rule (`:540`), the presence check beside the lost/retired indistinguishability sentence (`:542`) that it remedies. Mirroring scope (D3) follows the observed near-miss audiences: the lead's own scripted rewrite means the lead surface needs the stop-rule inline, while audit-time procedures can ride a pointer — duplication being the drift source this issue documents. The pin module shape (new module, copied helpers, presence + absence, no counts) follows the prep's harness census: per-module helper duplication is the convention, the append-method sentence was the unpinned gap, and absence pins on the retired scope close the revert-with-green-suite shape. The no-touch table follows the grep+categorize+decide sweep: four pin categories exist on the two in-scope files (pointer-resolution, count, phrase, character-budget), each verified individually rather than assumed.
