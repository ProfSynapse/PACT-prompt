"""
Structural pin tests for the memory-index append-method rule.

Pins the reader-facing instruction surfaces that carry the append-not-rewrite
rule for an agent's persistent MEMORY.md index:

  canonical (skills/pact-agent-teams/SKILL.md, "Index upkeep" paragraph):
    - the forbidden method family named explicitly, including the shell
      one-liner form (`read_text()` → `replace()` → `write_text()` in one
      shell command is still a whole-file rewrite),
    - stale-anchor `Edit` failure semantics: re-read from disk, re-anchor on
      the fresh text, retry — never answer a failed `Edit` with a rewrite,
    - the satellite presence-check appended to the roll-up paragraph:
      before reporting an entry as lost, check the `MEMORY-*.md` and
      `INDEX_*.md` satellites and run the reachability command without
      `--emit-edit`.
  lead variant (agents/pact-orchestrator.md):
    - the same method family and stale-anchor semantics inline (the lead's
      own surface carries the point-of-action stop-rule), with the
      presence-check routed to the canonical surface as a pointer tail.

PRESENCE pins, not counts. None of these phrases is intended to recur a
fixed number of times per surface, so count pins would add
lockstep-maintenance cost without catching a real erosion shape (same
rationale test_wake_ordering_pinned.py records). No EXPECTED_COUNTS-style
lockstep is introduced by this module. No HEADING_PINS: the rule lands
inside existing paragraphs and adds no section. No mirror discipline: the
rule has no protocols/ presence, so the byte-parity gate is not in play.

PHRASES, not line shapes. The pinned sentences are hard-wrapped in the
shipped markdown and tool language inside a pinned span is inline-code
formatted. Phrase pins therefore match against backtick-AND-whitespace-
NORMALIZED text (see _phrase: strip backticks, then
`" ".join(text.split())`) so they survive re-wrapping and inline-code
rendering alike. The Unicode arrows in the one-liner call sequence are
literal text on both sides of normalization and must be copied exactly.

ABSENCE pins lock out the retired pre-fix scope ("never a whole-file
rewrite from a copy you read earlier") on both surfaces. A full revert
to the two-step-only scope flips the presence pins too (the new clauses
are gone with it), so the absence pins' unique catch is the retired
phrase restored ALONGSIDE the new clauses — a co-existence muddle (a
merge or partial edit keeping both forms) leaves the presence pins
green, and only the retired phrase witnesses the regression.

Counter-test-by-revert (verified): with both doc surfaces reverted to
their pre-change state, every test in this module fails — all 12
presence cases (no pinned phrase pre-existed on either surface) and
both absence cases (the retired phrase was present pre-fix). The
flip-set cardinality and its measurement history are recorded in the
module-level comment at the bottom of this file. Post-restore, all
cases pass.
"""

from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent

SKILL = PLUGIN_ROOT / "skills" / "pact-agent-teams" / "SKILL.md"
ORCHESTRATOR = PLUGIN_ROOT / "agents" / "pact-orchestrator.md"


def _raw(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _phrase(text: str) -> str:
    """Phrase-matching normalization: strip backticks, then collapse any
    whitespace run (including newlines from hard-wrapping) to a single
    space. Tool language is inline-code formatted in the shipped markdown,
    so a pinned phrase must match a subject rendered with backticks inside
    the phrase span. Applied to BOTH sides (file text and pinned phrase) so
    phrases stored with or without backticks match consistently."""
    return " ".join(text.replace("`", "").split())


def _normalized(path: Path) -> str:
    """Backtick-and-whitespace-normalized file text for phrase pins: an
    intentional re-wrap of a rule sentence does not fail the pin while a
    re-WORD still does, and inline-code backticks inside a phrase span do
    not mask a retired rendering."""
    return _phrase(_raw(path))


def _lines_outside_fences(path: Path) -> list:
    """Stripped lines of the file, excluding fenced-code-block content and
    the fence delimiter lines themselves. A heading-shaped line inside a
    ``` / ~~~ fence is example text, not a real section heading, and must
    not satisfy a heading pin (a section deletion that leaves behind a
    fenced example of its own heading would otherwise stay green)."""
    lines = []
    in_fence = False
    for line in _raw(path).splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(stripped)
    return lines


# ---------------------------------------------------------------------------
# Phrase pins — whitespace-normalized presence.
# ---------------------------------------------------------------------------

PHRASE_PINS = [
    # --- canonical SKILL surface ---
    # Scope generalization marker: the forbidden family is "however
    # produced", not the two-step copy form alone.
    (SKILL, "never a whole-file rewrite however produced"),
    # The shell one-liner form named by its exact call sequence — the form
    # both observed near-misses used. The arrows are literal text.
    (SKILL, "read_text() → replace() → write_text() in one shell command is still a whole-file rewrite"),
    # The stale-anchor response: re-read, re-anchor, retry.
    (SKILL, "re-read the file from disk, re-anchor on the fresh text, and retry the Edit"),
    # The anti-fallback clause (sentence-initial capital N on this surface).
    (SKILL, "Never answer a failed Edit with a rewrite"),
    # The presence-check names the satellite indexes explicitly.
    (SKILL, "check the MEMORY-*.md and INDEX_*.md satellites the preamble names"),
    # The audit-direction procedure: reachability command in read-only mode.
    (SKILL, "without --emit-edit, which reports every leaf no index still points at"),
    # --- lead-variant ORCHESTRATOR surface ---
    # Method scope on the lead surface (R2 pins flip independently of R1).
    (ORCHESTRATOR, "never a whole-file rewrite however produced"),
    # The one-liner form named on the lead surface.
    (ORCHESTRATOR, "a scripted read-replace-write from a shell one-liner"),
    # Stale-anchor semantics on the lead surface.
    (ORCHESTRATOR, "If the Edit fails on a stale anchor, the file changed under you"),
    # The stale-anchor response on the lead surface (the condition above
    # and the anti-fallback below leave this imperative clause unpinned
    # without it — measured: deleting it alone leaves both green).
    (ORCHESTRATOR, "re-read from disk, re-anchor, and retry"),
    # Anti-fallback, lowercase n — mid-sentence on this surface; the
    # distinct case from the SKILL pin above is deliberate (per-surface
    # casing — do not normalize case to unify these pins).
    (ORCHESTRATOR, "never answer a failed Edit with a rewrite"),
    # The pointer tail routing the presence-check to the canonical home.
    (ORCHESTRATOR, "for the enforced limits and the satellite presence-check"),
]


@pytest.mark.parametrize(
    "doc_path, phrase",
    PHRASE_PINS,
    ids=[f"{p.name}::{ph[:40]}" for p, ph in PHRASE_PINS],
)
def test_rule_phrase_present(doc_path: Path, phrase: str):
    """Each load-bearing rule phrase must be present on its surface.
    Matching is whitespace-normalized: hard-wrap and same-line-rider
    renderings both satisfy the pin; a re-WORD does not. If a phrase was
    changed intentionally, update the pin in lockstep — otherwise the rule
    has eroded on a surface an LLM loads at runtime."""
    normalized_phrase = _phrase(phrase)
    assert normalized_phrase in _normalized(doc_path), (
        f"{doc_path.name}: rule phrase {phrase!r} not found "
        f"(backtick-and-whitespace-normalized match). If the wording was changed "
        f"intentionally, update this pin in lockstep; otherwise the "
        f"append-method rule this phrase carries is missing from a "
        f"runtime-loaded surface."
    )


# ---------------------------------------------------------------------------
# Absence pins — retired pre-fix scope phrase.
# ---------------------------------------------------------------------------

# The pre-fix rule scoped the prohibition to the two-step form only
# ("never a whole-file rewrite from a copy you read earlier"). A full
# revert to that scope flips the presence pins too (the new clauses are
# gone with it); the absence pins' unique catch is the retired phrase
# restored ALONGSIDE the new clauses — a co-existence muddle (a merge or
# partial edit keeping both forms) leaves the presence pins green — so
# the retired phrase itself is pinned absent on both surfaces.
RETIRED_SCOPE = "never a whole-file rewrite from a copy you read earlier"

ABSENCE_PINS = [
    (SKILL, RETIRED_SCOPE),
    (ORCHESTRATOR, RETIRED_SCOPE),
]


@pytest.mark.parametrize(
    "doc_path, retired",
    ABSENCE_PINS,
    ids=[f"{p.name}::{ph[:40]}" for p, ph in ABSENCE_PINS],
)
def test_retired_scope_phrase_absent(doc_path: Path, retired: str):
    """Regression guard: the retired two-step-only scope phrase must not
    reappear on either surface — reintroduction would re-narrow the
    prohibition to the copy-from-earlier form and re-open the scripted
    one-liner gap. Checked against backtick-and-whitespace-normalized text
    so neither a hard-wrapped nor an inline-code rendering slips past."""
    assert _phrase(retired) not in _normalized(doc_path), (
        f"{doc_path.name}: retired scope phrase {retired!r} reappeared. "
        f"The append rule now forbids a whole-file rewrite however "
        f"produced; do not reintroduce the two-step-only scope (if a "
        f"future rule genuinely narrows it, update this guard "
        f"deliberately)."
    )


# ---------------------------------------------------------------------------
# Counter-test flip-set record (see module docstring). Current inventory:
# 12 presence + 2 absence = 14 cases. With both doc surfaces reverted to
# their pre-change state and this module run against them: {14 failed,
# 0 passed} — all 12 presence cases RED (no pinned phrase pre-existed on
# either surface) and both absence cases RED (the retired scope phrase
# was present on both surfaces pre-fix). Post-restore: 14/14 green.
# Measurement history: {13 failed, 0 passed} measured at authoring time
# 2026-09-07 (working-tree revert of the 2 doc paths, edits saved aside),
# when the module had 11 presence cases. The 12th presence case — the
# lead-surface stale-anchor response clause "re-read from disk,
# re-anchor, and retry" — was added in review remediation after being
# measured unpinned (deleting it alone left the condition and
# anti-fallback pins green); {14 failed, 0 passed} then measured
# 2026-09-07 against the pre-change surfaces in a throwaway detached
# worktree with the current module copied in. The same remediation
# corrected the absence-pin rationale in the docstring and the
# RETIRED_SCOPE comment: their unique catch is the retired phrase
# restored ALONGSIDE the new clauses (co-existence); a bare clause
# deletion flips the presence pins itself.
# ---------------------------------------------------------------------------
