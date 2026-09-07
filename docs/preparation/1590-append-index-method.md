# Prepare Research: #1590 — Append-Not-Rewrite Method Gap

Worktree: `/Users/mj/Sites/collab/PACT-prompt/.worktrees/fix/1590-append-index-method`. All paths below are relative to the worktree root; line numbers are as of the worktree HEAD at research time. Read-only research; nothing outside this file was changed.

## Executive Summary

The append-not-rewrite rule lives in exactly **two** instruction surfaces — the canonical paragraph at `skills/pact-agent-teams/SKILL.md:540` and a shortened variant at `agents/pact-orchestrator.md:607` — plus four pointer sites that name the rule without restating it. It does **not** appear in `protocols/` (extracts or the SSOT), so editing the rule text does not trigger the byte-mirror gate. The satellite-index convention is fully defined in-repo (same SKILL.md section, plus the recognition code in `scripts/memory_reachability.py`). The pin-test machinery exists as a **per-module convention, not a shared library**: each `test_*_pinned.py` carries its own local copy of the normalization helpers, and the cheapest way to pin new wording is a `(surface, phrase)` tuple in a `PHRASE_PINS`-style list. The current rule text covers the two-step "read earlier, rewrite later" shape but does not obviously name the single-command scripted `read_text()→replace()→write_text()` form — the exact method both observed near-misses used. The stale-anchor `Edit` failure guidance exists in-repo but is scoped to the `memory_reachability --emit-edit` flow at SKILL.md:544, not to the general append at :540. No instruction surface tells an agent auditing for a lost update which index to check — the presence-check procedure the issue's secondary finding asks for does not exist anywhere.

## 1. Surface Census — the rule and its variants

### 1a. Rule-carrying surfaces (the text itself)

| # | Location | Surface type | What it carries |
|---|----------|--------------|-----------------|
| R1 | `pact-plugin/skills/pact-agent-teams/SKILL.md:540` | Teammate skill, `## Before Completing` (:522) → item 1 → "Index upkeep — pointers go in the head, never the tail." | **Canonical, fullest form.** Limits (200 lines / 25,000 UTF-16 code units), satellite/archive naming-convention preamble, append-below-preamble placement, the `Edit`-against-disk rule with mechanism ("other instances of your agent type write this same index, including instances in other projects and other sessions") and failure mode ("a rewrite silently drops whatever they added while you worked"), the refuse-compaction clause ("compaction is a whole-file rewrite, which this rule already forbids"), the anticipated-instruction warning, and the self-measure one-liner. |
| R2 | `pact-plugin/agents/pact-orchestrator.md:607` | Lead persona, `## 13. Workflows, Specialists & Reference` → `### Memory Management` (:597) | **Shortened variant.** Keeps: `Edit`-against-disk, "never a whole-file rewrite from a copy you read earlier", the shared-store rationale, "keep pointers in the head", and a link back to R1 "for the enforced limits". Omits: satellites, roll-up, `memory_reachability`, limits measurement, refuse-compaction, anticipated-instruction. Drift vs R1: "other instances write that same index" — drops the "of your agent type … other projects and other sessions" qualifier that carries the type-keyed mechanism. |

### 1b. Pointer sites (name the rule, do not restate it)

| # | Location | Text |
|---|----------|------|
| P1 | `pact-plugin/agents/pact-orchestrator.md:603` | Auto-memory bullet; names "the append discipline that protects entries you did not write" and links to R1. |
| P2 | `pact-plugin/skills/pact-memory/SKILL.md:480` | Memory-layers table, Auto-memory row: "see the index-upkeep rule in `pact-agent-teams`". |
| P3 | `pact-plugin/skills/pact-memory/SKILL.md:482` | Memory-layers table, Agent persistent memory row: same pointer, "for the enforced limits (per memory directory)". |
| P4 | `pact-plugin/skills/pact-agent-teams/SKILL.md:6` | Skill frontmatter `description`: "Invoke it at spawn, and again before you append to your MEMORY.md index … append to a shared index without dropping another instance's entries." — the skill is designed to be re-invoked immediately before an append. |

The single-source discipline (pointers instead of restatement) is itself pinned: `tests/test_agent_memory_cap_single_source.py` (see §3).

### 1c. Sibling anti-rewrite rules on other stores (variants by family, not by wording)

These are not copies of the index rule but belong in the census because they are the same hazard class with **two different remedies**, and ARCHITECT's wording should not contradict either:

| # | Location | Store | Rule shape |
|---|----------|-------|------------|
| S1 | `pact-plugin/skills/pact-handoff-harvest/SKILL.md:401` | Handoff ledger (`## team=` section) | **Append-only by construction**: "every write is **APPEND-ONLY** … never rewrite the existing ones … you never need to have read the section you are writing to — which is what makes the write safe, because a truncated read looks exactly like a complete one." Safety comes from union-readers + append-only lines, not from the `Edit` tool. |
| S2 | `pact-plugin/commands/wrap-up.md:190`, `commands/orchestrate.md:230`, `commands/orchestrate.md:971`, `commands/comPACT.md:165`, `commands/comPACT.md:408`, `commands/imPACT.md:21`, `commands/next.md:33` | pact-backlog | **The opposite remedy**: "Run the command rather than editing the file: it loads through `load_or_create`, which is what stashes the compare-and-swap baseline. A document built any other way is written with NO lost-update protection and nothing reports that." Here the *script* is the safe path (it carries CAS); hand-editing is the unsafe one. The memory-index rule forbids the script; the backlog rule forbids the hand-edit. Both are correct for their store; new wording for #1590 should not claim "scripts are always the hazard" without scoping. |

### 1d. Mechanism documentation (context, not rule text)

- `pact-plugin/commands/peer-review.md:219` states the type-keyed mechanism explicitly: "Persistent agent-memory is keyed by agent TYPE, so a reviewer of the same type loads at spawn the same store the builder has been writing to."
- `pact-plugin/scripts/memory_reachability.py:9-12` (module docstring) already articulates this issue's core design principle: "`--emit-edit` … PRINTS an edit block for an agent to apply with its own editing tool, which is the mechanism the index upkeep rule already mandates. Rebuilding that inside a script was the earlier design and it was the problem, not the solution."

### 1e. Negative results (verified absences)

- `pact-plugin/protocols/` (all extracts **and** `pact-protocols.md` SSOT): zero hits for `whole-file`, `as it is on disk`, `silently drops`. The rule is not in any protocol surface, so the SSOT-mirror same-commit requirement does **not** fire for edits to R1/R2 wording. (It fires only if ARCHITECT chooses to *add* text to a protocols extract.)
- Hooks: `grep -rli whole-file hooks/` returns five files (`bootstrap_marker_writer.py:423`, `task_claim_gate.py:287`, `pin_staleness_gate.py:633`, `shared/claude_md_manager.py:711`, `shared/pin_markers.py:735,739,956`) — all are code comments about those hooks' own file-write internals. **No hook injects the index-upkeep rule into context.**
- `pact-plugin/agents/pact-secretary.md`: no index-write rule (only an auto-memory mention at :278). The secretary writes to pact-memory (SQLite), a different store.
- Other vocabulary swept with zero rule-relevant hits: `stale anchor`, `re-anchor`, `read-replace-write`, `lost update` (the seven backlog hits in S2 are the CAS family), `never rewrite` / `full-file rewrite` / `overwrite the whole` (only S1), `presence check`.

## 2. Satellite Index Convention

**What exists:** the `MEMORY-*.md` / `INDEX_*.md` / `ARCHIVE_*.md` naming convention.

**Where defined:**

- **Convention definition (instruction surface):** `skills/pact-agent-teams/SKILL.md:540` — the preamble "names satellite and archive files by NAMING CONVENTION rather than by filename, using these three and no others: '`MEMORY-*.md` and `INDEX_*.md` roll up a topic; `ARCHIVE_*.md` holds retired entries.' These are fixed, not examples — a satellite named any other way is not recognised as one, and everything it holds reads as lost."
- **Creation procedure:** same file, `:542` — roll-up: "move one topic's entries into a satellite file, then leave a pointer to that satellite in the part of the index that still loads." Satellites are created by roll-up from `MEMORY.md`, one topic at a time; nothing in any surface describes writing a new entry *directly* into a satellite.
- **Recognition code:** `pact-plugin/scripts/memory_reachability.py:62` — `INDEX_SHAPED = ("MEMORY-", "INDEX_", "ARCHIVE")`, with the load-bearing comment at :57-59: the pattern decides what *may* become a root; roots are found "by FOLLOWING POINTERS, never by globbing this pattern. An unnamed satellite is genuinely unreachable." :206 notes satellites may name satellites (multi-level roll-up is live in real trees). :67 `ARCHIVE_MARKERS` separates retired content from orphans.
- **Platform layer beneath it:** one-file-per-memory plus a `MEMORY.md` index whose head auto-loads is the *platform's* agent-memory format; SKILL.md:538 acknowledges this ("the platform hands you its absolute path, and the schema for writing to it, in your own context"). The satellite convention is the PACT-layer addition on top. The platform schema is not in this repo.
- **Which store at all:** SKILL.md:538 disambiguates competing memory-directory instructions by path ("use the one whose path contains `/agent-memory/`"); pact-memory vs auto-memory vs agent-memory roles are tabulated at `skills/pact-memory/SKILL.md:478-483`.

**How an agent knows which index an entry belongs in:** from the index's own preamble pointers (the roll-up rule makes the pointer the load-bearing artifact: "A moved entry whose pointer was never written is unreachable"). There is **no other procedure** — and specifically no presence-check procedure. Nothing in any instruction surface tells an agent "before reporting an entry as lost, check the satellites named in the preamble" or "run `memory_reachability.py` to ask whether a leaf is still pointed at" for the audit direction; the tool is referenced only for pointer *placement* (:544). The issue's secondary finding (a zero from the wrong index reads as a lost update) has no answering text today. Closest existing vocabulary: "everything it holds reads as lost" (:540) and "no later reader can tell the difference between a memory you retired and one you lost" (:542) — both describe the hazard, neither prescribes the check.

## 3. Pin-Test Harness

**Correction to the dispatch framing:** there is no shared "pin module". The backtick-stripping matcher is a **local helper convention duplicated in each pin module**, and `tests/helpers.py` (frontmatter parsing, transcript factories) contains no phrase-matching utility. Verified: `def _phrase` exists only at `tests/test_wake_ordering_pinned.py:93` and `tests/test_dual_channel_acceptance_pinned.py:149` (plus `_normalized` at :107/:159, `_lines_outside_fences` at :117); neither pin module imports anything project-local beyond `re`/`pathlib`/`pytest`.

### 3a. The matcher

```python
def _phrase(text: str) -> str:
    return " ".join(text.replace("`", "").split())
```

Applied to **both sides** (file text and pinned phrase), so a pin survives hard-wrapping, same-line riders, and inline-code backticks inside the phrase span; a re-*wording* still fails. Rationale in the helper docstring (wake_ordering:94-105): measured blindness being closed was the retired rendering "`SendMessage` FIRST", invisible to a whitespace-only normalizer.

### 3b. The pin shapes (all with working examples)

| Shape | Mechanism | Example |
|-------|-----------|---------|
| **Phrase pin** (presence) | `PHRASE_PINS = [(path, phrase), …]` (:178), parametrized; `assert _phrase(phrase) in _normalized(doc_path)` | `tests/test_wake_ordering_pinned.py:178-368` (test fn :353); `tests/test_dual_channel_acceptance_pinned.py` |
| **Heading pin** | `HEADING_PINS = [(path, exact heading line)]` (:139); exact-line membership against `_lines_outside_fences` (fenced code excluded; heading *level* is part of the contract — `### X` ≠ `#### X`) | `tests/test_wake_ordering_pinned.py:139-173` |
| **Absence pin** | `assert _phrase(retired) not in _normalized(doc_path)` — retired renderings stay retired | `tests/test_dual_channel_acceptance_pinned.py:380,664,1179,1284` |
| **Count pin** | `EXPECTED_COUNTS = {path: n}` — only where a phrase is intended to recur a fixed number of times; wake_ordering's docstring explicitly declines count pins for presence-only phrases (lockstep-maintenance cost) | `tests/test_read_trigger_precondition_pinned.py:81,186-215` |
| **Cross-ref slug pin** | literal `#anchor-slug` presence per surface, plus heading→slug slugification tests | `tests/test_wake_ordering_pinned.py:378-465` |
| **Pointer-resolution pin** | referrer must contain `POINTER_TOKEN`, target must contain `RULE_HEADING = "Index upkeep"` — directly on this issue's section | `tests/test_agent_memory_cap_single_source.py:1425-1443` (constants :77-78, :221) |

### 3c. Conventions a new pin must follow

- **Mirror discipline:** a phrase living in a byte-mirrored protocols region is pinned on the extract **and** on `protocols/pact-protocols.md` as separate surfaces (wake_ordering docstring, "Mirror discipline"). Not applicable to the index-upkeep rule (§1e: not in protocols/), but applicable if ARCHITECT adds rule text to a protocols extract.
- **Counter-test-by-revert:** at authoring time, revert the doc surface(s) to pre-change state and record which cases flip; the flip-set cardinality is recorded in the module docstring (wake_ordering:62-68 is the template).
- **Per-surface comments explain why each phrase is load-bearing** and what regression shape flips exactly that case (see the PHRASE_PINS entries — every tuple carries one).
- **Existing coverage of this rule:** `tests/test_agent_memory_cap_single_source.py` pins the *limits'* single-sourcing (unit-vocabulary and subject-tainted arms) and the pointer↔rule resolution — but **no test pins the append-method sentence itself**. The rule text could erode or be deleted from SKILL.md:540 today with every existing test staying green, provided the limits and the "Index upkeep" heading survive. That is the pin gap #1590's acceptance criterion ("a test pins whichever of these lands in an instruction surface") exists to close.

### 3d. Minimal shape of adding a pin for new rule wording

For a phrase landing in `skills/pact-agent-teams/SKILL.md` or `agents/pact-orchestrator.md`:

1. Cheapest: add `(SKILL, "<new phrase>")` / `(ORCHESTRATOR, "<new phrase>")` tuples to an existing module's `PHRASE_PINS` — but neither existing module is thematically about the memory-index rule, so the cleaner precedent-consistent move is:
2. New module `tests/test_<feature>_pinned.py`: copy the three helpers (`_phrase`, `_normalized`, `_lines_outside_fences` — duplication is the established convention, not a smell), define `PLUGIN_ROOT` + surface `Path` constants, declare `PHRASE_PINS` (and `HEADING_PINS` if a new section is added), add the parametrized presence test, run the counter-test-by-revert, and record the flip-set in the docstring. Full working template: `tests/test_wake_ordering_pinned.py` (691 lines, docstring-first).

## 4. Placement Evidence (issue item 4)

What the current text covers vs the two observed near-misses:

| Near-miss | Rule text today | Coverage gap |
|-----------|-----------------|--------------|
| `MEMORY.md` index updated via `read_text()→replace()→write_text()` **in one shell command** (×3) | "never a whole-file rewrite **from a copy you read earlier**" (:540, :607) | The literal scope names the two-step shape (read at T1, write at T2 from the stale copy). A single command that reads fresh and immediately rewrites the whole file is arguably *outside* "a copy you read earlier" — the unsafe method arrives through diligence, reading as compliant. The forbidden *shape* (whole-file rewrite) is named; the forbidden *method family* (scripted read-replace-write, however produced, including shell one-liners) is not. |
| Lead's `python3 -c` read-replace-write for every index update that session | Same text; the orchestrator variant :607 is explicitly about the lead's own index, so the audience is covered | Same method gap. Additionally the rule gives no positive alternative for "change one line from a shell" — the only sanctioned non-interactive path in-repo is `memory_reachability.py --emit-edit` (:544), which is scoped to pointer placement, not general appends. |
| Stale-anchor `Edit` failure | Covered **only** at :544 and only for the emit-edit application flow: "If the `Edit` reports no match, the file changed while you were working — STOP, re-run the command, and apply the fresh block; never broaden the match or replace every occurrence to force it through." | The general append at :540 carries no failure-semantics text. An agent whose append-`Edit` fails on a stale anchor has no in-surface instruction that this is the loud failure the rule wants, or what to do next. The :544 text is reusable vocabulary but its scope is one tool's output block. |
| Secondary finding: absent-from-`MEMORY.md` reads as lost update | Hazard described (:540 "reads as lost", :542 "no later reader can tell the difference") | No presence-check procedure anywhere: nothing names *which* index to check, nothing points an auditor at the satellites or at `memory_reachability.py` for the detection direction (§2). |

**Adjacent placement candidates** (where the rule could additionally live, with what each site argues):

- **Same section, new paragraph (:540-544 region):** everything the rule needs is already here; the satellite and stale-anchor texts are adjacent. Lowest-friction placement.
- **`skills/pact-memory/SKILL.md` memory-layers table (:478-483):** where an agent deciding *which store* to write reads. Currently pointer-only (P2/P3); the single-source pin (`test_agent_memory_cap_single_source.py`) constrains restating *limits* there, not method guidance, but the single-source principle argues against duplicating rule text here.
- **`agents/pact-orchestrator.md` §13 (:597-607):** already carries the R2 variant; any new method language added to R1 must be mirrored here in shortened form or the two surfaces drift further.
- **`skills/pact-handoff-harvest/SKILL.md:401` (S1) and the backlog family (S2):** sibling stores with their own remedies — evidence that "which remedy" is store-specific. New wording that universalizes the `Edit` remedy should be scoped to the agent-memory index so it does not contradict the backlog's run-the-command remedy.

**Detection-side fact:** the collision warning the issue quotes is a PACT hook, not the platform: `pact-plugin/hooks/file_tracker.py:170-171` (PostToolUse on `Edit|Write`, registered in `hooks/hooks.json`) emits "File conflict: {file} was also edited by {others}. Consider coordinating via SendMessage" via `additionalContext`. Non-blocking by construction (PostToolUse cannot block). Detection exists in-plugin; prevention remains instruction-only — consistent with the issue's framing and its out-of-scope note (agents cannot lock).

## 5. Gaps and Non-Findings (contingency-clause accounting)

Per the dispatch's instruction to report gaps explicitly rather than force a quote:

1. **No gap on the satellite convention** — it is fully defined in-repo (§2). Assumption (B) from my teachback holds.
2. **No gap on pin-machinery existence, but a shape correction** — the machinery is a duplicated per-module helper convention, not a shared pin module (§3). A generalizable example exists (`test_wake_ordering_pinned.py`). Assumption (C) holds with that correction.
3. **Found gap:** the append-method sentence of the rule is unpinned (§3c) — no test currently guards it.
4. **Found gap:** no presence-check procedure on any surface (§2, §4).
5. **Found gap:** stale-anchor failure semantics exist only scoped to the emit-edit flow (:544), not the general append (§4).
6. **Non-finding:** the rule has no protocols/ presence, so no byte-mirror lockstep applies to editing it — unless ARCHITECT adds text to a protocols extract, in which case the same-commit SSOT-mirror requirement fires (`scripts/verify-protocol-extracts.sh`, gated by `tests/test_audit_protocol.py`).

## 6. Boundaries of this research

- Wording proposals are deliberately absent — placement options in §4 name sites and constraints only; the text is ARCHITECT's.
- The platform's agent-memory schema (one file per memory, `MEMORY.md` index, head auto-load) is referenced at SKILL.md:538 as platform-delivered; it is not in this repo and was not re-verified against a platform bundle.
- The census swept `agents/`, `skills/`, `protocols/`, `commands/` (the dispatch's scope) plus `hooks/`, `scripts/`, and `tests/` for mechanism and pins. Vocabulary net: `whole-file`, `as it is on disk`, `silently drops`, `drops whatever`, `read-replace-write`/`read-modify-write`, `rewrite` (every hit eyeballed), `stale anchor`, `re-anchor`, `lost update`, `satellite`, `MEMORY-*`/`INDEX_*`/`ARCHIVE_*`, `other instances`/`same store`, `presence check`, `never rewrite`/`full-file rewrite`/`overwrite the whole`. A variant phrased entirely outside that net (e.g. "clobbers", "tramples") would not have been caught; the two strongest semantic anchors (`other instances`, `satellite`) returned no out-of-net hits.
