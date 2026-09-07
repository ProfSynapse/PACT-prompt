"""Unit tests for session_end's self-registration registry prune
(_prune_registry_dead_teams).

Commit-F coverage: drops registry lines whose @team has no live directory under
~/.claude/teams/, keeps live-team lines, drops malformed/no-@ lines, is
idempotent (no needless rewrite when nothing is stale), and is fail-safe
(missing file / symlink / write race → 0, never raises). Preserves 0o600 on
rewrite.
"""

import inspect
import json
import os
import re
import stat
import sys
from pathlib import Path

import pytest

from session_end import _prune_registry_dead_teams


@pytest.fixture
def prune_env(tmp_path):
    """Build an isolated ~/.claude tree: a teams_dir with caller-chosen live
    teams + a registry file. Returns a helper namespace."""
    teams_dir = tmp_path / ".claude" / "teams"
    teams_dir.mkdir(parents=True)
    reg_path = tmp_path / ".claude" / "pact-sessions" / ".teammate-registry.jsonl"
    reg_path.parent.mkdir(parents=True)

    class _Env:
        teams = teams_dir
        registry = reg_path

        @staticmethod
        def live_team(name):
            (teams_dir / name).mkdir(parents=True, exist_ok=True)

        @staticmethod
        def write_registry(lines):
            reg_path.write_text("".join(l + "\n" for l in lines), encoding="utf-8")

        @staticmethod
        def line(session_id, value):
            return json.dumps({"session_id": session_id, "value": value})

        @staticmethod
        def prune():
            return _prune_registry_dead_teams(
                registry_path=reg_path, teams_dir=teams_dir
            )

        @staticmethod
        def remaining():
            return reg_path.read_text(encoding="utf-8").splitlines() if reg_path.exists() else []

    return _Env


def test_drops_dead_team_keeps_live_team(prune_env):
    prune_env.live_team("pact-live")
    prune_env.write_registry([
        prune_env.line("s1", "alice@pact-live"),
        prune_env.line("s2", "bob@pact-dead"),  # no dir under teams → dead
    ])
    pruned = prune_env.prune()
    assert pruned == 1
    assert prune_env.remaining() == [prune_env.line("s1", "alice@pact-live")]


def test_drops_malformed_and_no_at_lines(prune_env):
    prune_env.live_team("pact-live")
    prune_env.write_registry([
        prune_env.line("s1", "alice@pact-live"),
        prune_env.line("s2", "no-at-separator"),  # no @ → dropped
        "this-is-not-json",                        # garbage → dropped
    ])
    pruned = prune_env.prune()
    assert pruned == 2
    assert prune_env.remaining() == [prune_env.line("s1", "alice@pact-live")]


def test_unsafe_at_team_is_dropped_not_kept_and_never_raises(prune_env):
    """L1/M1 regression: an @team that is not a single safe path segment must be
    DROPPED — never KEPT via a traversal that happens to resolve to a real dir,
    and never raise.

    NON-VACUITY (lever works on the test runtime, Python 3.12+, where
    ``Path.is_dir()`` returns False on a NUL instead of raising): the ``.`` and
    ``pact-live/..`` cases both resolve to ``teams_dir`` itself, so PRE-fix
    ``(teams_dir / team).is_dir()`` was True and the bogus lines were KEPT
    (the L1 containment hole); POST-fix the segment validator rejects them, so
    they drop. Reverting the validation flips those lines back to KEPT → this
    assertion FAILS. The NUL case additionally guards the Python <=3.11 path
    where ``is_dir()`` propagated ``ValueError`` out of the prune (there the
    revert turns this into an ERROR). NUL is built with ``chr(0)`` so the test
    file holds no literal null byte.
    """
    prune_env.live_team("pact-live")
    nul_team = "pact-" + chr(0) + "evil"
    prune_env.write_registry([
        prune_env.line("s1", "alice@pact-live"),       # valid single segment → kept
        prune_env.line("s2", "bob@."),                 # '.' resolves to teams_dir → pre-fix KEPT; drop
        prune_env.line("s3", "eve@pact-live/.."),      # traversal → teams_dir → pre-fix KEPT; drop
        prune_env.line("s4", "mallory@" + nul_team),   # NUL → drop (guards <=3.11 raise)
    ])
    pruned = prune_env.prune()  # must NOT raise on any supported Python
    assert pruned == 3
    assert prune_env.remaining() == [prune_env.line("s1", "alice@pact-live")]


def test_idempotent_no_rewrite_when_nothing_stale(prune_env):
    prune_env.live_team("pact-live")
    prune_env.write_registry([prune_env.line("s1", "alice@pact-live")])
    mtime_before = prune_env.registry.stat().st_mtime_ns
    pruned = prune_env.prune()
    assert pruned == 0
    # no rewrite happened → mtime unchanged (the "no needless rewrite" guard)
    assert prune_env.registry.stat().st_mtime_ns == mtime_before


def test_all_dead_empties_the_file(prune_env):
    # no live teams written; every line is dead
    prune_env.write_registry([
        prune_env.line("s1", "alice@pact-gone"),
        prune_env.line("s2", "bob@pact-also-gone"),
    ])
    pruned = prune_env.prune()
    assert pruned == 2
    assert prune_env.remaining() == []


def test_missing_file_returns_zero_no_raise(prune_env):
    # registry never written
    assert prune_env.prune() == 0


def test_preserves_0o600_on_rewrite(prune_env):
    prune_env.live_team("pact-live")
    prune_env.write_registry([
        prune_env.line("s1", "alice@pact-live"),
        prune_env.line("s2", "bob@pact-dead"),
    ])
    prune_env.prune()
    mode = stat.S_IMODE(prune_env.registry.stat().st_mode)
    assert mode == 0o600, f"expected 0o600 after rewrite, got {oct(mode)}"


def test_symlink_registry_is_skipped(prune_env, tmp_path):
    # A symlink at the registry path is NOT followed (O_NOFOLLOW posture) →
    # prune returns 0 and does not rewrite through the link.
    real = tmp_path / "real_target.jsonl"
    real.write_text(prune_env.line("s1", "alice@pact-dead") + "\n", encoding="utf-8")
    prune_env.registry.symlink_to(real)
    assert prune_env.prune() == 0
    # the link target is untouched
    assert real.read_text(encoding="utf-8").strip() == prune_env.line("s1", "alice@pact-dead")
    # WHICH MECHANISM THIS PINS: the READ-TIME is_symlink refusal (guarantee 4),
    # not the write path. Deleting that check leaves read_text following the
    # link and the prune reaching os.replace, which REPLACES the symlink with a
    # regular file -- so the deliberate arrangement is silently destroyed while
    # the target's bytes survive. Asserting the target alone cannot see that;
    # this line is what separates the two.
    assert prune_env.registry.is_symlink()


def _make_root_absent(root):
    pass  # the path is simply never created


def _make_root_plain_file(root):
    root.write_text("not a directory", encoding="utf-8")


def _make_root_dangling_symlink(root):
    root.symlink_to(root.parent / "nonexistent-target")


def _make_root_unreadable(root):
    # A root with live teams INSIDE it, which the process cannot enumerate.
    root.mkdir()
    (root / "pact-live").mkdir()
    (root / "pact-also-live").mkdir()
    root.chmod(0o000)


@pytest.mark.parametrize("make_root", [
    _make_root_absent,
    _make_root_plain_file,
    _make_root_dangling_symlink,
    # DO NOT DROP AS REDUNDANT. Measured: the three above pass under a
    # root-level `is_dir()`/`exists()` guard too, so they pin only that SOME
    # guard exists. mode-000 is the one that pins its FORM — it is the sole
    # arm that separates the scandir enumeration from a stat-based predicate.
    _make_root_unreadable,
], ids=["absent", "plain-file", "dangling-symlink", "mode-000"])
def test_unobservable_teams_root_prunes_nothing(tmp_path, make_root):
    """CANNOT-OBSERVE guard: a teams root that cannot be ENUMERATED must prune
    NOTHING — the registry survives byte-identical and is not rewritten.

    Deliberately does NOT use `prune_env` — that fixture mkdirs a readable
    teams root (line 25), so no existing arm can reach any of these states.

    NON-VACUITY, measured against the unguarded base: every one of these four
    roots made `(teams_dir / team).is_dir()` return False for every line, so
    the prune returned 2 and rewrote the file to 0 bytes. Reverting the guard
    reddens all four. `mode-000` is the arm a root-level `is_dir()`/`exists()`
    guard does NOT catch: the root passes both, yet each per-team stat inside
    it fails into False — the same truncation through a different door.

    The mtime assertion catches a rewrite that reproduces identical bytes.

    This is NOT `test_all_dead_empties_the_file` with a broken root: there the
    root is enumerable and the teams are genuinely gone, which stays a
    legitimate truncation. The observable-root control is
    `test_idempotent_no_rewrite_when_nothing_stale`.
    """
    teams_dir = tmp_path / "teams"
    make_root(teams_dir)
    reg_path = tmp_path / "pact-sessions" / ".teammate-registry.jsonl"
    reg_path.parent.mkdir(parents=True)
    payload = (
        json.dumps({"session_id": "s1", "value": "alice@pact-live"}) + "\n"
        + json.dumps({"session_id": "s2", "value": "bob@pact-also-live"}) + "\n"
    )
    reg_path.write_text(payload, encoding="utf-8")
    mtime_before = reg_path.stat().st_mtime_ns

    try:
        pruned = _prune_registry_dead_teams(
            registry_path=reg_path, teams_dir=teams_dir
        )
    finally:
        # Restore traversal, or tmp_path cleanup fails on the mode-000 arm.
        if teams_dir.is_dir():
            teams_dir.chmod(0o755)

    assert pruned == 0
    assert reg_path.read_text(encoding="utf-8") == payload
    assert reg_path.stat().st_mtime_ns == mtime_before


def test_unlistable_root_refuses_rather_than_pruning_a_dead_line(tmp_path):
    """A mode-111 root (traversable, not listable) is OBSERVABLE per entry, so
    the dead line is pruned and the live one kept.

    THIS ARM WAS INVERTED BY THE PER-ENTRY PROBE. It previously pinned a
    disclosed OVER-REFUSAL: the old root-listability guard refused here,
    keeping a line it could have proved dead. Guarantee 6 stats each team
    individually, and traversal is permitted at mode 111, so the stats now
    answer correctly and the over-refusal is gone. The arm is kept, and
    inverted, because the state is the one that separates listability from
    traversability -- the only state where the two disagree.

    Distinct from the four arms above, which use live-only registries where
    refusing and pruning-correctly both leave 2 lines and cannot be told apart.
    Here one team is live and one is dead, so the two outcomes differ: 1 line
    if the entries were probed, 2 if the root was judged unobservable.

    NON-VACUITY: reinstating any root-LISTABILITY guard reddens this arm --
    scandir on a mode-111 root raises, so such a guard returns 0 and keeps
    both lines. That is what the arm now forbids.
    """
    teams_dir = tmp_path / "teams"
    teams_dir.mkdir()
    (teams_dir / "pact-live").mkdir()  # "pact-dead" deliberately not created
    reg_path = tmp_path / ".teammate-registry.jsonl"
    payload = (
        json.dumps({"session_id": "s1", "value": "alice@pact-live"}) + "\n"
        + json.dumps({"session_id": "s2", "value": "bob@pact-dead"}) + "\n"
    )
    reg_path.write_text(payload, encoding="utf-8")
    teams_dir.chmod(0o111)

    try:
        pruned = _prune_registry_dead_teams(
            registry_path=reg_path, teams_dir=teams_dir
        )
    finally:
        teams_dir.chmod(0o755)

    remaining = reg_path.read_text(encoding="utf-8")
    assert pruned == 1
    assert "alice@pact-live" in remaining     # observable and live -> kept
    assert "bob@pact-dead" not in remaining   # observable and dead -> pruned


def test_defaults_resolve_without_args(monkeypatch, tmp_path):
    """Calling with no args resolves REGISTRY_PATH + ~/.claude/teams; a missing
    default registry is a clean 0 (no raise)."""
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    import session_end
    # patch the module-bound registry-path accessor to the isolated home
    monkeypatch.setattr(
        session_end, "_get_registry_path",
        lambda: tmp_path / ".claude" / "pact-sessions" / ".teammate-registry.jsonl",
    )
    assert session_end._prune_registry_dead_teams() == 0


# --------------------------------------------------------------------------
# Arms that separate a guarantee from its NEIGHBOUR.
#
# The arms above assert on return values and file contents. Six guard lines in
# this function were found deletable with nothing red, because that is the
# layer at which a deletable line is invisible: its neighbour reproduces the
# same return and the same bytes. Each arm below observes the one thing that
# differs.
# --------------------------------------------------------------------------


class _ReadCountingPath(type(Path())):
    """A Path that counts its own read_text calls."""

    reads = 0

    def read_text(self, *args, **kwargs):
        type(self).reads += 1
        return super().read_text(*args, **kwargs)


def test_unusable_root_is_rejected_before_the_registry_is_read(tmp_path):
    """Guarantee 2 (S_ISDIR): an unusable root never reaches a file read.

    ORDERING PIN -- READ THIS BEFORE "FIXING" A RED HERE. This arm asserts an
    implementation ORDERING, not a behaviour, and it will redden on a
    legitimate restructure that still behaves correctly. That is acceptable
    only because the ordering IS the claim the S_ISDIR line makes: on a
    plain-file root the per-entry probes are meaningless, so the function
    declines before reading anything. A restructure that keeps the refusal but
    reads first has changed that claim and should be re-argued, not silenced.

    WHY NOTHING ELSE SEES IT: with the S_ISDIR line deleted, the per-entry
    stats raise ENOTDIR, guarantee 6 catches them and returns 0, and the
    registry is untouched. Measured: pruned and file contents are IDENTICAL
    with and without the line -- 0 and intact both ways. Only the read count
    differs (0 shipped, 1 ablated).
    """
    root = tmp_path / "teams"
    root.write_text("not a directory\n", encoding="utf-8")  # stat-able, not a dir
    registry = _ReadCountingPath(tmp_path / "registry.jsonl")
    registry.write_text(
        json.dumps({"session_id": "s1", "value": "ghost@pact-dead"}) + "\n",
        encoding="utf-8",
    )
    before = registry.read_text(encoding="utf-8")

    _ReadCountingPath.reads = 0
    pruned = _prune_registry_dead_teams(registry_path=registry, teams_dir=root)

    assert _ReadCountingPath.reads == 0, (
        "the registry was read despite an unusable teams root: the S_ISDIR "
        "refusal no longer precedes the read"
    )
    # Stated so a future reader can see these do NOT separate the mechanisms.
    assert pruned == 0
    assert registry.read_text(encoding="utf-8") == before


def test_registry_is_0600_even_when_the_umask_would_not_grant_it(prune_env):
    """Guarantee 3: the explicit 0600 is load-bearing, not double-held.

    The temp file is created with `O_CREAT|O_EXCL, 0o600`, whose mode argument
    IS honoured (the temp is always new) -- but it is masked by the process
    umask, so at the common umasks the explicit chmod and the open mode agree
    and neither can be told from the other. Measured: at umask 022 and 077 both
    routes give 0o600; at umask 0o200 the open alone gives 0o400.

    This arm runs under a umask that masks a bit in 0600, which is the only
    condition under which deleting the explicit chmod reddens anything.

    os.umask is PROCESS-GLOBAL. It is restored in the finally below; a leak
    would silently change the mode of every file every later test writes, with
    no symptom in this file.
    """
    prune_env.live_team("pact-live")
    prune_env.write_registry([
        prune_env.line("s1", "alice@pact-live"),
        prune_env.line("s2", "bob@pact-dead"),
    ])

    previous = os.umask(0o200)  # strip owner-write from anything newly created
    try:
        assert prune_env.prune() == 1
    finally:
        os.umask(previous)

    mode = stat.S_IMODE(prune_env.registry.stat().st_mode)
    assert mode == 0o600, (
        f"expected 0o600 under a masking umask, got {oct(mode)} -- the explicit "
        f"chmod is gone and only the open's mode argument remains, which the "
        f"umask has masked"
    )


def test_invalid_utf8_registry_returns_rather_than_propagating(prune_env):
    """Guarantee 5: a registry that is not valid UTF-8 prunes nothing.

    UnicodeDecodeError subclasses ValueError, not OSError, so it is not caught
    by the never-raises handlers around it. The separating observation is that
    the function RETURNS with the registry byte-identical, rather than raising
    out of a contract that forbids raising.
    """
    prune_env.live_team("pact-live")
    payload = (
        json.dumps({"session_id": "s1", "value": "alice@pact-live"}).encode("utf-8")
        + b"\n"
        + b'{"session_id": "s2", "value": "bob@\xff\xfe-dead"}\n'  # invalid UTF-8
    )
    prune_env.registry.write_bytes(payload)

    assert prune_env.prune() == 0
    assert prune_env.registry.read_bytes() == payload


def test_a_decodable_registry_still_prunes(prune_env):
    """Over-swallowing control for the arm above.

    Without this, widening the guarantee-5 handler to swallow every ValueError
    -- or bailing out on any registry at all -- would leave that arm green
    while the prune had stopped working entirely.
    """
    prune_env.live_team("pact-live")
    prune_env.write_registry([
        prune_env.line("s1", "alice@pact-live"),
        prune_env.line("s2", "bob@pact-dead"),
    ])

    assert prune_env.prune() == 1
    remaining = prune_env.remaining()
    assert len(remaining) == 1
    assert "alice@pact-live" in remaining[0]


GUARANTEE_ARMS = {
    1: ["test_unobservable_teams_root_prunes_nothing"],
    2: ["test_unusable_root_is_rejected_before_the_registry_is_read"],
    3: ["test_registry_is_0600_even_when_the_umask_would_not_grant_it",
        "test_preserves_0o600_on_rewrite"],
    4: ["test_symlink_registry_is_skipped"],
    5: ["test_invalid_utf8_registry_returns_rather_than_propagating",
        "test_a_decodable_registry_still_prunes"],
    6: ["test_unobservable_teams_root_prunes_nothing",
        "test_unlistable_root_refuses_rather_than_pruning_a_dead_line"],
}


def test_every_guarantee_marker_has_an_arm():
    """Each `SAFETY GUARANTEE n of m` in the function is claimed by an arm here.

    WHAT THIS CATCHES, and it is more than self-consistency. The marker
    numbers are checked against each other AND against the arms mapped below.
    The second is the load-bearing half: a marker DELETED with the rest
    renumbered consistently satisfies every check the markers make about
    themselves -- totals agree, count equals total, numbers run 1..N -- and is
    caught only by the set no longer matching GUARANTEE_ARMS. Measured on a
    blind mutation: guarantee 2's marker removed and the remaining five
    renumbered to `of 5`, with the guard line itself untouched. A
    self-consistency check alone would have passed it. A consistent lie is
    still consistent.

    THE ONE DIRECTION THAT IS NOT MECHANISED is narrower than it first looks:
    a guard that was NEVER marked. Nothing here can recognise an unmarked
    guard line, and guarantee 6 was exactly that -- a working, well-armed
    handler invisible for six passes because no marker named it. That rests on
    review. A guard that LOSES its marker is caught, so long as
    GUARANTEE_ARMS still names an arm for it.

    COLLATERAL vs TARGETED: `test_defaults_resolve_without_args` reddens when
    guarantee 1 is ablated, but it is NOT listed against it. It exercises the
    no-argument default path, so it breaks on anything that raises downstream;
    it pins nothing about the unobservable root. An arm that merely reddens is
    not an arm that pins.

    Numbers are read from the markers, never hardcoded, and the markers sit
    deliberately out of source order -- so this keys on the parsed number and
    a reordering is a no-op here, as it should be.
    """
    source = inspect.getsource(_prune_registry_dead_teams)
    markers = re.findall(r"SAFETY GUARANTEE (\d+) of (\d+)", source)
    assert markers, "no SAFETY GUARANTEE markers in the function -- parser is blind"

    numbers = sorted(int(n) for n, _ in markers)
    declared = {int(m) for _, m in markers}
    assert len(declared) == 1, f"markers disagree on the total: {sorted(declared)}"
    total = declared.pop()

    assert len(numbers) == total, (
        f"{len(numbers)} markers present but each declares 'of {total}' -- a "
        f"guarantee was added or removed without renumbering the others"
    )
    assert numbers == list(range(1, total + 1)), (
        f"marker numbers are not 1..{total}: {numbers}"
    )
    assert set(numbers) == set(GUARANTEE_ARMS), (
        f"markers {numbers} do not match the arms mapped here "
        f"{sorted(GUARANTEE_ARMS)} -- a guarantee has no arm, or an arm claims "
        f"a guarantee that no longer exists"
    )

    module = sys.modules[__name__]
    for number, arms in GUARANTEE_ARMS.items():
        for arm in arms:
            assert hasattr(module, arm), (
                f"guarantee {number} names {arm!r}, which does not exist in "
                f"this module -- the mapping has gone stale"
            )
