"""
Tests for the session-record rung of the project-scope read contract, the
fail-closed env/record write refusal, and the home-scope warning.

Location: pact-plugin/tests/test_project_dir_resolution.py

Summary: Phase B of claude-project-dir-once. The read contract gains a
session-record rung (env -> session record -> git -> cwd -> home-with-warning)
shared by every consumer (memory_api._detect_project_id,
working_memory's two CLAUDE.md resolvers, backlog.project_root), and WRITES
(backlog set, memory save, WM sync) refuse when CLAUDE_PROJECT_DIR and the
session record disagree.

Used by/with:
- skills/pact-memory/scripts/pact_session.py: the record reader + refusal
  channel under test.
- tests/fixtures/project_dir.py: umbrella factory, context writer, discovery
  enabler, subprocess env builder.
- tests/test_project_id.py: the replica/equivalence pins for the pre-existing
  strategies; this file owns the record-rung coverage the replica deliberately
  omits.

HOW THE RECORD ROUTE IS EXERCISED: in-process rows use
enable_record_discovery (the test_session_discovery_route pattern — the
refusal reads os.environ, so deleting PYTEST_CURRENT_TEST supplies the REAL
predicate a different input) plus a real context file written into the
redirected tmp config root. No getter is monkeypatched: every row exercises
the shipped discovery chain. The one subprocess row crosses the real process
boundary with a constructed env (child_env), because Path.home patching does
not cross it.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import pytest

from fixtures.project_dir import (
    child_env,
    enable_record_discovery,
    make_umbrella,
    write_session_context,
)
# EVERY import here goes through the `scripts.` package route, deliberately.
# A bare `import working_memory` loads a SECOND module instance whose
# `from pact_session import ...` binds a second copy of pact_session — with
# its own discovery cache AND its own ProjectScopeDisagreementError class, so
# the cache reset would miss the live cache and pytest.raises would miss the
# raised class. The sibling files' bare-import convention is not safe for
# this file's cross-module refusal assertions.
from scripts import pact_session
from scripts import working_memory as wm
from scripts.memory_api import PACTMemory
from scripts.pact_session import ProjectScopeDisagreementError
from shared import backlog


_MEMORY_CLI = (
    Path(__file__).parent.parent / "skills" / "pact-memory" / "scripts" / "cli.py"
)
SID = "record-rung-session-0001"


def _seed_claude_md(root: Path) -> Path:
    """A minimal syncable project CLAUDE.md (Working Memory section present)."""
    claude_dir = root / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    claude_md = claude_dir / "CLAUDE.md"
    claude_md.write_text(
        "# Project\n\n## Working Memory\n"
        "<!-- Auto-managed by pact-memory skill. -->\n\n",
        encoding="utf-8",
    )
    return claude_md


def _arm_record(monkeypatch, tmp_path, record_dir) -> None:
    """Make the session record LIVE in-process: refusal off, env id set,
    context file written into the redirected tmp config root."""
    enable_record_discovery(monkeypatch, pact_session)
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", SID)
    write_session_context(Path.home() / ".claude", SID, record_dir)


def _git_repo(path: Path) -> Path:
    """A fresh git repo (no commit needed for --git-common-dir)."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "init", "-q", str(path)],
        check=True,
        capture_output=True,
        env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull},
    )
    return path


# ---------------------------------------------------------------------------
# The record reader's contract (pact_session.get_project_dir_from_session_record)
# ---------------------------------------------------------------------------

class TestSessionRecordReader:
    """The reader never raises and fails open to "" on every ambiguous shape."""

    def test_returns_the_recorded_absolute_project_dir(self, tmp_path, monkeypatch):
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        assert pact_session.get_project_dir_from_session_record() == str(umbrella.project)

    def test_missing_context_file_yields_empty(self, tmp_path, monkeypatch):
        enable_record_discovery(monkeypatch, pact_session)
        monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", SID)
        assert pact_session.get_project_dir_from_session_record() == ""

    def test_corrupt_context_file_yields_empty(self, tmp_path, monkeypatch):
        enable_record_discovery(monkeypatch, pact_session)
        monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", SID)
        write_session_context(Path.home() / ".claude", SID, tmp_path, body="{not json")
        assert pact_session.get_project_dir_from_session_record() == ""

    def test_two_matching_slugs_yield_empty(self, tmp_path, monkeypatch):
        enable_record_discovery(monkeypatch, pact_session)
        monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", SID)
        write_session_context(Path.home() / ".claude", SID, tmp_path, slug="project-a")
        write_session_context(Path.home() / ".claude", SID, tmp_path, slug="project-b")
        assert pact_session.get_project_dir_from_session_record() == ""

    def test_non_string_project_dir_yields_empty(self, tmp_path, monkeypatch):
        enable_record_discovery(monkeypatch, pact_session)
        monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", SID)
        write_session_context(
            Path.home() / ".claude", SID, tmp_path,
            body=json.dumps({"session_id": SID, "project_dir": 12345}),
        )
        assert pact_session.get_project_dir_from_session_record() == ""

    def test_relative_project_dir_is_rejected(self, tmp_path, monkeypatch):
        """Pre-fix records can hold ".": resolving that HERE would alias the
        record rung to the reader's cwd ABOVE the git rung — inverting the
        precedence the rung exists to establish. Non-absolute reads as absent."""
        enable_record_discovery(monkeypatch, pact_session)
        monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", SID)
        write_session_context(
            Path.home() / ".claude", SID, tmp_path,
            body=json.dumps({"session_id": SID, "project_dir": "."}),
        )
        assert pact_session.get_project_dir_from_session_record() == ""

    def test_second_call_is_served_from_the_cache(self, tmp_path, monkeypatch):
        """The glob runs once per process per env id, not once per caller."""
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)

        calls = []
        real = pact_session._context_record_on_disk

        def counting(env_session):
            calls.append(1)
            return real(env_session)

        monkeypatch.setattr(pact_session, "_context_record_on_disk", counting)
        first = pact_session.get_project_dir_from_session_record()
        second = pact_session.get_project_dir_from_session_record()
        assert first == second == str(umbrella.project)
        assert len(calls) == 1, "record discovery must glob once per process"

    def test_pytest_refusal_fires_with_a_live_record(self, tmp_path, monkeypatch):
        """Non-vacuity leg: file present AND id set, so ONLY the refusal can
        explain the empty answer."""
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "some_test (call)")
        assert pact_session.get_project_dir_from_session_record() == ""

    def test_absent_env_id_yields_empty_with_a_live_record(self, tmp_path, monkeypatch):
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
        assert pact_session.get_project_dir_from_session_record() == ""


# ---------------------------------------------------------------------------
# Precedence: _detect_project_id's Strategy 1.5 (record below env, above git)
# ---------------------------------------------------------------------------

class TestDetectProjectIdRecordRung:
    def test_env_wins_over_a_disagreeing_record_on_reads(self, tmp_path, monkeypatch):
        """READS FOLLOW ENV: a present CLAUDE_PROJECT_DIR declares the scope;
        the record never overrides it and nothing refuses on a read path."""
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        repo = _git_repo(tmp_path / "declared-repo")
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(repo))
        assert PACTMemory._detect_project_id() == "declared-repo"

    def test_record_outranks_the_cwd_git_root(self, tmp_path, monkeypatch):
        """#1485's core shape as a unit row: cwd inside a git repo whose root
        is the WRONG scope; the record names the umbrella. Without the rung
        the git strategy would answer the repo's name, so a green here proves
        the rung fired."""
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        repo = _git_repo(tmp_path / "foreign-repo")
        monkeypatch.chdir(repo)
        assert PACTMemory._detect_project_id() == "umbrella"

    def test_record_fallthrough_to_git_when_absent(self, tmp_path, monkeypatch):
        """No record (no env id) -> the git strategy answers exactly as before."""
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        repo = _git_repo(tmp_path / "plain-repo")
        monkeypatch.chdir(repo)
        assert PACTMemory._detect_project_id() == "plain-repo"

    def test_record_in_a_worktree_names_the_main_repo(self, tmp_path, monkeypatch):
        """The record leg shares Strategy 1's main-repo rewrite: a recorded
        worktree path must key on the MAIN repo's basename, not the worktree's,
        or one project fragments across its own checkouts."""
        umbrella = make_umbrella(tmp_path)
        main = _git_repo(tmp_path / "main-proj")
        linked = tmp_path / "wt"
        subprocess.run(
            ["git", "-C", str(main), "worktree", "add", "-q", str(linked), "-b", "wt"],
            check=True,
            capture_output=True,
            env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull},
        )
        _arm_record(monkeypatch, tmp_path, linked)
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        # cwd must not contribute a repo answer: the guard-verified git-less
        # umbrella keeps the arm hermetic even for a contributor whose TMPDIR
        # sits under a repository.
        monkeypatch.chdir(umbrella.project)
        assert PACTMemory._detect_project_id() == "main-proj"


# ---------------------------------------------------------------------------
# Home scope warns (the last resort must not be silent)
# ---------------------------------------------------------------------------

class TestHomeScopeWarning:
    def _force_cwd_resolution(self, monkeypatch, resolved_root: Path):
        """Kill the env/record/git legs so Strategy 3 answers `resolved_root`.
        The walk itself is not the thing under test — the warning branch is —
        so _find_project_root is pinned to the answer directly."""
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)

        def _no_git(*args, **kwargs):
            raise FileNotFoundError("git unavailable in this arm")

        monkeypatch.setattr("subprocess.run", _no_git)
        monkeypatch.setattr(
            PACTMemory, "_find_project_root",
            staticmethod(lambda start: resolved_root),
        )

    def test_home_resolution_warns(self, tmp_path, monkeypatch, caplog):
        home = Path.home().resolve()  # autouse-redirected to tmp_path
        self._force_cwd_resolution(monkeypatch, home)
        with caplog.at_level(logging.WARNING):
            result = PACTMemory._detect_project_id()
        assert result == home.name
        assert any(
            "HOME directory" in r.message and "CLAUDE_PROJECT_DIR" in r.message
            for r in caplog.records
        ), f"home scope resolved silently: {[r.message for r in caplog.records]}"

    def test_project_resolution_does_not_warn(self, tmp_path, monkeypatch, caplog):
        project = tmp_path / "a-real-project"
        project.mkdir()
        self._force_cwd_resolution(monkeypatch, project.resolve())
        with caplog.at_level(logging.WARNING):
            result = PACTMemory._detect_project_id()
        assert result == "a-real-project"
        assert not any("HOME directory" in r.message for r in caplog.records), (
            "a project-root resolution raised the home-scope warning"
        )


# ---------------------------------------------------------------------------
# Fail-closed writes: env vs record disagreement
# ---------------------------------------------------------------------------

class TestWriteRefusalOnDisagreement:
    def test_memory_save_refuses_naming_both_values(self, tmp_path, monkeypatch):
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        other = tmp_path / "other"
        other.mkdir()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(other))

        memory = PACTMemory()  # constructed AFTER the env manipulation
        with pytest.raises(ProjectScopeDisagreementError) as excinfo:
            memory.save({"context": "c", "goal": "g"})
        text = str(excinfo.value)
        assert str(other) in text, "the refusal does not name the env value"
        assert str(umbrella.project) in text, "the refusal does not name the record"
        assert "Nothing was written" in text
        assert "re-export CLAUDE_PROJECT_DIR" in text, "the refusal names no remedy"

    def test_memory_sync_refuses_naming_both_values(self, tmp_path, monkeypatch):
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        other = tmp_path / "other"
        other.mkdir()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(other))

        memory = PACTMemory(project_id="proj")  # explicit id: the None guard is not the subject
        with pytest.raises(ProjectScopeDisagreementError) as excinfo:
            memory.sync()
        assert str(other) in str(excinfo.value)
        assert str(umbrella.project) in str(excinfo.value)

    def test_agreement_with_a_trailing_slash_does_not_refuse(self, tmp_path, monkeypatch):
        """normpath collapses the spelling difference; the predicate — not a
        full save — is the unit under test here."""
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(umbrella.project) + "/")
        assert pact_session.env_record_project_dir_disagreement() is None

    def test_no_record_means_no_disagreement(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        # No session id in the env (autouse scrub) -> the record side is absent.
        assert pact_session.env_record_project_dir_disagreement() is None


class TestBacklogRecordRung:
    def test_record_anchors_project_root_when_env_is_unset(self, tmp_path, monkeypatch):
        """The #1613-curing arm: an umbrella session whose env var never
        arrived resolves the session's own scope instead of refusing."""
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        assert backlog.project_root() == umbrella.project.resolve()

    def test_record_naming_a_deleted_dir_refuses_with_the_right_source(self, tmp_path, monkeypatch):
        gone = tmp_path / "deleted-between-sessions"
        _arm_record(monkeypatch, tmp_path, gone)
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        with pytest.raises(backlog.BacklogWriteError) as excinfo:
            backlog.project_root()
        text = str(excinfo.value)
        assert "session record" in text, (
            f"the refusal attributed the anchor to the wrong source: {text}"
        )
        assert str(gone) in text, "the refusal does not echo the rejected value"

    def test_disagreement_refuses_before_any_write(self, tmp_path, monkeypatch):
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        other = tmp_path / "other"
        other.mkdir()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(other))
        with pytest.raises(backlog.BacklogWriteError) as excinfo:
            backlog.project_root()
        text = str(excinfo.value)
        assert str(other) in text and str(umbrella.project) in text
        assert "Nothing was written" in text

    def test_agreement_proceeds(self, tmp_path, monkeypatch):
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(umbrella.project) + "/")
        assert backlog.project_root() == umbrella.project.resolve()

    def test_cli_add_under_record_then_set_under_disagreement(
        self, tmp_path, monkeypatch, capsys
    ):
        """End-to-end through backlog.main: the write keyed on the record
        succeeds unprefixed (the umbrella acceptance shape), and the same
        session with a disagreeing prefix refuses on stderr with exit 65."""
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        store = tmp_path / "store"
        store.mkdir()

        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        assert backlog.main(["--backlog-dir", str(store), "add", "umbrella item"]) == 0
        written = store / "umbrella.json"
        assert written.exists(), (
            f"add did not key on the record basename; store holds {list(store.iterdir())}"
        )
        item_id = json.loads(written.read_text(encoding="utf-8"))["items"][0]["id"]
        before = written.read_bytes()

        other = tmp_path / "other"
        other.mkdir()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(other))
        capsys.readouterr()  # drain the add output so the refusal text is isolated
        rc = backlog.main(["--backlog-dir", str(store), "set", item_id, "--status", "active"])
        assert rc == backlog._EXIT_REFUSED
        err = capsys.readouterr().err
        assert str(other) in err and str(umbrella.project) in err, (
            f"the stderr refusal must name both values; got: {err!r}"
        )
        assert written.read_bytes() == before, "a refused set still mutated the file"


# ---------------------------------------------------------------------------
# Working-memory resolvers: the record rung preserves the existence coupling
# ---------------------------------------------------------------------------

class TestWorkingMemoryRecordRung:
    def test_record_dir_is_probed_for_an_existing_claude_md(self, tmp_path, monkeypatch):
        umbrella = make_umbrella(tmp_path)
        claude_md = _seed_claude_md(umbrella.project)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        elsewhere = tmp_path / "elsewhere"
        elsewhere.mkdir()
        monkeypatch.chdir(elsewhere)

        assert wm._get_claude_md_path() == claude_md
        path, base = wm._resolve_display_claude_md_with_base()
        assert path == claude_md
        assert base == umbrella.project, (
            "the containment anchor must be the base the resolver USED — the "
            "recorded dir — not a re-derivation"
        )

    def test_record_without_a_claude_md_falls_through_to_git(self, tmp_path, monkeypatch):
        """The existence coupling is preserved: a record naming a dir with no
        CLAUDE.md does NOT end resolution (this resolver never creates the
        file); the git anchor answers as before."""
        umbrella = make_umbrella(tmp_path)  # has ./CLAUDE.md at the root...
        (umbrella.project / "CLAUDE.md").unlink()  # ...remove it: record probe must miss
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        repo = _git_repo(tmp_path / "repo-with-file")
        git_file = _seed_claude_md(repo)
        monkeypatch.chdir(repo)

        assert wm._get_claude_md_path() == git_file


class TestWorkingMemoryDisagreementGuard:
    def test_ambient_sync_refuses_on_disagreement(self, tmp_path, monkeypatch):
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        other = tmp_path / "other"
        other.mkdir()
        env_file = _seed_claude_md(other)  # a REAL writable target, so the
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(other))  # refusal is non-vacuous

        with pytest.raises(ProjectScopeDisagreementError) as excinfo:
            wm.sync_to_claude_md({"context": "X", "goal": "g"}, None, "id")
        assert str(other) in str(excinfo.value)
        assert str(umbrella.project) in str(excinfo.value)
        assert "X" not in env_file.read_text(encoding="utf-8"), (
            "the refused sync still wrote to the env-resolved file"
        )

    def test_explicit_target_is_a_warrant_and_proceeds(self, tmp_path, monkeypatch):
        """A caller that names its file has declared the scope; the ambient
        disagreement is moot. Mirrors the sibling guards' warrant logic."""
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path / "other"))
        target_root = tmp_path / "declared"
        target = _seed_claude_md(target_root)

        result = wm.sync_to_claude_md(
            {"context": "DECLARED-TARGET", "goal": "g"}, None, "id", target=target
        )
        assert result.reason == wm.SyncResult.WROTE
        assert "DECLARED-TARGET" in target.read_text(encoding="utf-8")

    def test_claude_md_root_is_a_warrant_and_proceeds(self, tmp_path, monkeypatch):
        umbrella = make_umbrella(tmp_path)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        anchor = tmp_path / "anchored"
        _seed_claude_md(anchor)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(anchor))
        # env == anchor, record == umbrella: a disagreement exists, but the
        # declared containment anchor is a stronger warrant than the refusal.
        result = wm.sync_to_claude_md(
            {"context": "ANCHORED", "goal": "g"}, None, "id", claude_md_root=anchor
        )
        assert result.reason == wm.SyncResult.WROTE

    def test_agreement_syncs_ambiently(self, tmp_path, monkeypatch):
        umbrella = make_umbrella(tmp_path)
        env_file = _seed_claude_md(umbrella.project)
        _arm_record(monkeypatch, tmp_path, umbrella.project)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(umbrella.project))

        result = wm.sync_to_claude_md({"context": "AGREED", "goal": "g"}, None, "id")
        assert result.reason == wm.SyncResult.WROTE
        assert "AGREED" in env_file.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Cross-process: the CLI envelope carries the refusal on stderr
# ---------------------------------------------------------------------------

class TestCliRefusalEnvelope:
    def test_memory_save_cli_envelopes_the_refusal_on_stderr(self, tmp_path):
        """The full boundary: a child process with a constructed env discovers
        the record itself (no pytest marker crosses), and cmd_save's envelope
        lands on stderr with both values. Asserting the envelope type and both
        dir names — not the exit code alone — is what pins the refusal TEXT."""
        umbrella = make_umbrella(tmp_path)
        write_session_context(umbrella.config_root, SID, umbrella.project)
        other = tmp_path / "other"
        other.mkdir()
        store = tmp_path / "memory.db"
        env = child_env(
            umbrella.config_root,
            home=tmp_path,
            session_id=SID,
            project_dir=other,
        )
        setup = subprocess.run(
            [sys.executable, str(_MEMORY_CLI), "setup", "--db-path", str(store)],
            capture_output=True, text=True, env=env, cwd=str(tmp_path), timeout=120,
        )
        assert setup.returncode == 0, f"store setup failed: {setup.stderr[:400]!r}"

        proc = subprocess.run(
            [sys.executable, str(_MEMORY_CLI), "save", "--db-path", str(store),
             json.dumps({"context": "cross-process", "goal": "g"})],
            capture_output=True, text=True, env=env, cwd=str(tmp_path), timeout=120,
        )
        assert proc.returncode != 0, f"a disagreeing save exited 0: {proc.stdout!r}"
        assert "SCOPE_DISAGREEMENT" in proc.stderr, (
            f"the envelope type is missing from stderr: {proc.stderr!r}"
        )
        # The envelope is home-scrubbed (~), so assert on the distinguishing
        # basenames rather than the absolute paths.
        assert other.name in proc.stderr and umbrella.project.name in proc.stderr, (
            f"the refusal must name both values; stderr: {proc.stderr!r}"
        )
        assert not store.exists() or "cross-process" not in store.read_bytes().decode(
            "utf-8", errors="ignore"
        ), "a refused save left the row behind"

    def test_child_env_defaults_delete_the_project_dir_var(self, tmp_path):
        """Guard the env-builder itself: DELETE is the default and the pytest
        marker never crosses — the two leaks that would make every row above
        pass against the wrong state."""
        env = child_env(tmp_path / ".claude", home=tmp_path)
        assert "CLAUDE_PROJECT_DIR" not in env
        assert "PYTEST_CURRENT_TEST" not in env
        assert "CLAUDE_CODE_SESSION_ID" not in env
        assert env["HOME"] == str(tmp_path)
