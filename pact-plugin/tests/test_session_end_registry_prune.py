"""Unit tests for session_end's self-registration registry prune
(_prune_registry_dead_teams).

Commit-F coverage: drops registry lines whose @team has no live directory under
~/.claude/teams/, keeps live-team lines, drops malformed/no-@ lines, is
idempotent (no needless rewrite when nothing is stale), and is fail-safe
(missing file / symlink / write race → 0, never raises). Preserves 0o600 on
rewrite.
"""

import json
import stat
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
