"""
Location: pact-plugin/tests/test_working_memory_redirected_store_refusal.py
Summary: DOCUMENT-PAIR arms for the refusal that stops a memory row written to a
         REDIRECTED store from being projected into an AMBIENTLY resolved
         CLAUDE.md. Each arm drives `cli.py` in a CHILD PROCESS and compares the
         document BEFORE against the document AFTER, because the guard's whole
         subject is a write that either happened or did not, and a single-line
         probe of the predicate cannot see a document at all.

         WHY A CHILD PROCESS IS THE ONLY WAY TO REACH THE GUARD. The guard
         exempts an in-process caller (`"pytest" in sys.modules`), because the
         suite binds a redirected store for every test AND syncs ambiently on
         purpose. So an in-process arm can never observe the refusal, and an
         in-process arm that appeared to would be measuring something else.

         WHY THE ENVIRONMENT IS BUILT AND NEVER INHERITED. The sibling guard
         `_refuse_ambient_target_under_pytest` raises the SAME exception type on
         the SAME path when `PYTEST_CURRENT_TEST` is present. An inherited
         environment carries that variable into the child, the sibling refuses
         first, and every arm below goes green while measuring the OTHER guard.
         Each arm therefore builds its own environment and asserts the variable
         is absent from it. That absence is the separating condition, and it is
         asserted rather than assumed.

         SAFETY, AND IT IS THE POINT OF THE WHOLE FILE. These arms drive a real
         `save`. If the guard did not hold, the write would land in a real
         CLAUDE.md. Two independent bindings keep the child below `tmp_path`:
         `CLAUDE_PROJECT_DIR` with a SEEDED document (the resolver probes that
         directory and CONTINUES when it finds nothing, so seeding is what makes
         the probe terminate), and `HOME`, which puts the default store below
         `tmp_path` as well. Every arm then asserts containment.
Used by: pytest.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


from scripts.config import STORE_ORIGIN_ENV, STORE_ORIGIN_HOME  # noqa: E402
from scripts.working_memory import (  # noqa: E402
    AmbientSyncRefused,
    SyncResult,
    _refuse_ambient_sync_from_a_redirected_store,
    _target_is_inside_the_declared_project_dir,
)

_CLI = (
    Path(__file__).resolve().parent.parent
    / "skills" / "pact-memory" / "scripts" / "cli.py"
)

# A document with the section the sync writes into. Without the section the sync
# declines for an UNRELATED reason (`SyncResult.NO_WINDOW`), and an arm built on
# that document would report a clean negative that has nothing to do with the
# guard.
_SEED_DOCUMENT = """# Project Memory

## Retrieved Context

## Working Memory
"""


def _seed_project(tmp_path: Path) -> Path:
    """Create the project tree the child resolves into, and return its CLAUDE.md."""
    target = tmp_path / "project" / ".claude" / "CLAUDE.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_SEED_DOCUMENT, encoding="utf-8")
    return target


def _base_env(tmp_path: Path) -> dict:
    """Build the child environment from nothing. NEVER `os.environ.copy()`.

    A copy carries `PYTEST_CURRENT_TEST`, which makes the SIBLING guard refuse
    and hands every arm below a green for the wrong reason. PATH is kept because
    the resolver shells out to `git`, and a missing `git` changes which
    resolution branch runs.

    NO `CLAUDE_PROJECT_DIR` HERE, AND THAT IS THE DEFAULT ON PURPOSE. Setting it
    is what an arm does to DECLARE a root, and declaring one is now an exemption,
    so a base that set it would silently exempt every arm built on it. Each arm
    below states its own choice.
    """
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(tmp_path / "home"),
    }


def _escaped_root(tmp_path: Path) -> str:
    """A declared project directory that holds NO CLAUDE.md.

    THIS REPRODUCES THE INCIDENT, not merely an unset variable. The resolver
    probes the declared directory, finds nothing, and CONTINUES, so the document
    it settles on lies outside the root the caller named. That is the escape the
    guard refuses, and it stays below `tmp_path` throughout.
    """
    root = tmp_path / "declared-but-empty"
    root.mkdir(parents=True, exist_ok=True)
    return str(root)


def _run_cli(env: dict, cwd: Path, *args: str) -> subprocess.CompletedProcess:
    """Run the CLI as the incident ran it: a child process with a built env."""
    assert "PYTEST_CURRENT_TEST" not in env, (
        "the child environment carries PYTEST_CURRENT_TEST, so the SIBLING guard "
        "would refuse and this arm would measure the wrong mechanism"
    )
    return subprocess.run(
        [sys.executable, str(_CLI), *args],
        env=env,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=180,
    )


def _save_payload(marker: str) -> str:
    return json.dumps({"context": marker, "goal": marker})


def _envelope(result: subprocess.CompletedProcess) -> dict:
    """Parse the CLI's success envelope, failing loudly on anything else.

    The shape is `{"ok": true, "result": {...}}`, and the fields this file reads
    live in `result`, NOT at the top level. A bare `in` test against stdout would
    pass on a traceback that happened to contain the word, so it is parsed.
    """
    assert result.returncode == 0, (
        f"CLI exited {result.returncode}\nstdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    payload = json.loads(result.stdout)
    assert payload.get("ok") is True, f"envelope reports a failure: {payload}"
    return payload["result"]


def _sync_status(result: subprocess.CompletedProcess) -> str:
    """Read `sync_status` off the envelope.

    An ABSENT key returns a sentinel rather than the empty string, because
    `sync_status` is documented as TOTAL on the save path: its absence is a
    different fact from any of its values, and an arm must not read the two
    alike.
    """
    return _envelope(result).get("sync_status", "<absent>")


class TestRedirectedStoreDoesNotProjectIntoAnAmbientDocument:
    """The refusal, its cost, and the write that must keep working."""

    def test_a_redirected_store_that_escaped_its_root_writes_nothing(self, tmp_path):
        """THE INCIDENT SHAPE. Redirected store, and resolution escaped the
        declared root exactly as it did on the day.

        MUTANT that reddens this arm: remove the
        `_refuse_ambient_sync_from_a_redirected_store(target, claude_md_root,
        claude_md_path)` call from `sync_to_claude_md`. The entry is then
        projected, the document grows, and the byte comparison fails.

        The BASELINE is taken before the drive rather than after, so a document
        that was already wrong cannot read as a pass.
        """
        target = _seed_project(tmp_path)
        before = target.read_bytes()

        env = _base_env(tmp_path)
        env["PACT_TEST_MEMORY_DIR"] = str(tmp_path / "isolated-store")
        env["CLAUDE_PROJECT_DIR"] = _escaped_root(tmp_path)
        result = _run_cli(
            env, tmp_path / "project", "save", _save_payload("redirected-store-arm")
        )

        assert _sync_status(result) == SyncResult.REFUSED
        assert target.read_bytes() == before, (
            "the projection reached a document outside the declared root even "
            "though the row went to a redirected store"
        )

    def test_the_record_survives_the_refusal(self, tmp_path):
        """THE COST OF THE CHOSEN FAILURE DIRECTION, MEASURED RATHER THAN ARGUED.

        The guard refuses a PROJECTION, never a RECORD. This arm is what makes
        that claim checkable: the same refused save must still report success and
        still return an id, so a wrong refusal costs a display line and no data.

        MUTANT that reddens this arm: raise the refusal BEFORE the row is
        committed (move the guard above the write in `save`). The envelope then
        carries no id and the save reports a failure.
        """
        _seed_project(tmp_path)
        env = _base_env(tmp_path)
        env["PACT_TEST_MEMORY_DIR"] = str(tmp_path / "isolated-store")
        env["CLAUDE_PROJECT_DIR"] = _escaped_root(tmp_path)

        result = _run_cli(
            env, tmp_path / "project", "save", _save_payload("record-survives-arm")
        )

        assert _sync_status(result) == SyncResult.REFUSED
        assert _envelope(result).get("memory_id"), (
            "a refused sync must not cost the record"
        )

    def test_a_redirected_store_inside_its_declared_root_still_writes(self, tmp_path):
        """THE OVER-BLOCK ARM THE SUITE ITSELF FOUND. IT PROTECTS THE PRODUCT.

        This shape is a redirected store AND an ambient resolution, and it is
        LEGITIMATE: the caller declared a project directory and resolution stayed
        inside it. It is also common, because it is how a spawned child is
        sandboxed. An earlier form of this guard refused it, and the refusal
        reddened an existing suite arm rather than any arm of mine, which is what
        makes this a regression pin rather than a restatement.

        It differs from the refusal arm above in ONE variable, the declared root,
        so the two together attribute the refusal to the ESCAPE and not to the
        store redirect alone.

        MUTANT that reddens this arm: drop the `_target_is_inside_the_declared_
        project_dir` exemption. The write stops happening and the over-block
        comes back.
        """
        target = _seed_project(tmp_path)
        before = target.read_bytes()

        env = _base_env(tmp_path)
        env["PACT_TEST_MEMORY_DIR"] = str(tmp_path / "isolated-store")
        env["CLAUDE_PROJECT_DIR"] = str(tmp_path / "project")
        result = _run_cli(
            env, tmp_path / "project", "save", _save_payload("declared-root-arm")
        )

        assert _sync_status(result) == SyncResult.WROTE
        after = target.read_bytes()
        assert after != before
        assert b"declared-root-arm" in after
        target.resolve().relative_to(tmp_path.resolve())

    def test_the_default_store_still_writes_the_entry(self, tmp_path):
        """THE SECOND OVER-BLOCK ARM, on the ordinary production shape.

        No redirected store and no declared root: the everyday save. It must
        write. This is the arm that fails first if the guard is ever widened past
        the redirected-store class.

        MUTANT that reddens this arm: drop the
        `if origin == STORE_ORIGIN_HOME: return` early exit, so the guard reaches
        the escape check on a default-store save and refuses it.
        """
        target = _seed_project(tmp_path)
        before = target.read_bytes()

        env = _base_env(tmp_path)
        assert "PACT_TEST_MEMORY_DIR" not in env
        assert "CLAUDE_PROJECT_DIR" not in env
        result = _run_cli(
            env, tmp_path / "project", "save", _save_payload("default-store-arm")
        )

        assert _sync_status(result) == SyncResult.WROTE
        after = target.read_bytes()
        assert after != before
        assert b"default-store-arm" in after
        # Containment: the write must have landed below tmp_path and nowhere else.
        target.resolve().relative_to(tmp_path.resolve())

    def test_the_default_store_is_REFUSED_when_it_escapes_into_another_project(
        self, tmp_path
    ):
        """THE UNDER-BLOCK WAS ACCEPTED, THEN DELIBERATELY CLOSED. THE TRIPWIRE
        FIRED AND THIS IS THE DECISION IT ASKED SOMEBODY TO TAKE.

        This arm previously asserted the OPPOSITE — that a default-store save
        resolving outside the declared scope is ADMITTED — and said so as an
        accepted under-block, armed so a later widening would be a decision and
        not a drift. The widening came, the arm reddened, and the decision was
        taken by the team lead: store origin was a PROXY that did not track the
        property. The incident had a redirected store and escaped anyway,
        because the projection path never consults store origin at all.
        REPOSITORY IDENTITY is the property. Working in project A while
        resolution lands in project B's file is wrong whichever store is in use.

        SO THE OLD DOCSTRING'S CAUSE WAS SOUND AND ITS SCOPE WAS TOO WIDE. It
        argued that a worktree holds no CLAUDE.md of its own, that resolution
        falls through to the main checkout on purpose, and that refusing it
        would be the cardinal over-block. Every word of that is still true and
        is still honoured — but it is honoured by `same_repository`, which asks
        whether the fall-through landed back in the SAME project, not by
        admitting every escape a default store makes. The fall-through the old
        arm was protecting is protected. What it also admitted, and should not
        have, was a fall-through into a DIFFERENT project.

        🔴 THIS FIXTURE IS NOT THE WORKTREE CASE AND MUST NOT BE READ AS ONE.
        Nothing in this file creates a git repository: `_seed_project` and
        `_escaped_root` are plain directories, so `same_repository` reaches its
        non-repo branch and returns False. That is a faithful model of the
        INCIDENT and a false model of the cardinal over-block, which the old
        docstring named but its fixture could never reach. The worktree case is
        pinned separately in `TestTheCardinalFallthroughSurvives` below, with a
        real `git worktree add` — see that class for why a subdirectory is not
        a substitute.

        THE TRIPWIRE FRAMING IS KEPT, POINTING THE OTHER WAY. If a future
        change re-admits this, the arm reddens and the narrowing becomes a
        decision somebody takes on purpose, exactly as the widening was.
        """
        target = _seed_project(tmp_path)
        before = target.read_bytes()

        env = _base_env(tmp_path)
        env["CLAUDE_PROJECT_DIR"] = _escaped_root(tmp_path)
        result = _run_cli(
            env, tmp_path / "project", "save", _save_payload("default-escape-arm")
        )

        assert _sync_status(result) == SyncResult.REFUSED, (
            "a DEFAULT-store save whose declared scope resolved into a "
            "different project was admitted. Store origin is not the property "
            "— the incident had a redirected store and escaped anyway, because "
            "the projection path never reads store origin. If this admission "
            "is deliberate, say which property replaced repository identity."
        )
        assert target.read_bytes() == before, (
            "the projection reached a document outside the declared scope"
        )

    def test_the_retrieved_context_site_is_guarded_too(self, tmp_path, monkeypatch):
        """THE SECOND CALL SITE, driven IN PROCESS because the CLI cannot reach it.

        `sync_retrieved_to_claude_md` writes the Retrieved Context section. It is
        a different function with its own guard call, so a guard added to only
        one of the two would leave this route open with every arm above green.

        WHY THIS ARM IS NOT A SUBPROCESS ARM, AND THE CAUSE IS MEASURED RATHER
        THAN ASSUMED. `cmd_search` calls `PACTMemory.search` with
        `sync_to_claude=False` UNCONDITIONALLY, so no CLI verb reaches this
        function at all. A subprocess arm here passes with the guard call
        DELETED, which is a clean negative over a path it never drove. The
        exemption is lifted the same way the message pins lift it, and the
        resolver is pinned to a tmp document so the ambient branch is both
        deterministic and safe.

        IT IS A DOCUMENT PAIR, not a predicate probe: the bytes are compared
        across the call, so the arm fails if the write happens whatever the
        function returns.

        MUTANT that reddens this arm: remove the
        `_refuse_ambient_sync_from_a_redirected_store(None, claude_md_root)`
        call from `sync_retrieved_to_claude_md`.
        """
        import scripts.working_memory as wm

        target = _seed_project(tmp_path)
        before = target.read_bytes()

        monkeypatch.delitem(sys.modules, "pytest", raising=False)
        # BOTH LIFTS ARE REQUIRED, and the second one is the trap. This arm
        # calls the PUBLIC function, so the SIBLING guard runs first. This
        # process is a pytest process, so `PYTEST_CURRENT_TEST` is in its
        # environment and the sibling raises the SAME exception type from the
        # SAME line. MEASURED: with only the `sys.modules` lift, this arm passed
        # with the guard call under test DELETED. Removing the variable is what
        # makes the raise attributable to the store origin.
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        # The declared root is removed too, so the resolved target cannot be
        # inside it and the escape condition holds deterministically.
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        monkeypatch.setattr(
            wm, "store_path_origin", lambda: STORE_ORIGIN_ENV
        )
        monkeypatch.setattr(
            wm,
            "_resolve_display_claude_md_with_base",
            lambda: (target, target.parent.parent),
        )

        retrieved = [{"id": "0" * 32, "context": "retrieved-context-arm"}]
        with pytest.raises(AmbientSyncRefused):
            wm.sync_retrieved_to_claude_md(retrieved, query="retrieved-context-arm")

        assert target.read_bytes() == before, (
            "the retrieved-context projection reached the ambiently-resolved "
            "document from a redirected store"
        )


class TestTheRefusalMessage:
    """A MESSAGE PIN, and it supplements the document arms rather than replacing them.

    The document arms above prove the write did not happen. They cannot see WHY,
    because both guards report the same `sync_status`. This arm reads the text a
    caller and a log line receive, so a refusal keeps naming its own cause.
    """

    def test_the_message_names_the_origin_and_carries_no_path(self, monkeypatch):
        """MUTANT that reddens this arm: replace the origin word in the message
        with the resolved store path. The `origin=` assertion fails, and the
        path-leak assertion fails with it.

        The in-process exemption is lifted by removing `pytest` from
        `sys.modules` for the length of the call, which is the ONLY reason this
        arm can reach the raise at all.
        """
        monkeypatch.delitem(sys.modules, "pytest", raising=False)
        monkeypatch.setattr(
            "scripts.working_memory.store_path_origin",
            lambda: STORE_ORIGIN_ENV,
        )

        with pytest.raises(AmbientSyncRefused) as excinfo:
            _refuse_ambient_sync_from_a_redirected_store(None, None)

        message = str(excinfo.value)
        assert f"origin={STORE_ORIGIN_ENV}" in message
        assert "--no-sync" in message
        assert os.sep not in message.replace("--no-sync", ""), (
            "the refusal message carries a filesystem path; it must name the "
            "origin word only"
        )

    def test_the_default_origin_does_not_raise(self, monkeypatch):
        """THE NEGATIVE HALF OF THE MESSAGE PIN, paired so the arm above cannot
        go vacuous. A guard that raised for every origin would satisfy the
        assertions above and be an unconditional over-block.

        MUTANT that reddens this arm: drop the `origin == STORE_ORIGIN_HOME`
        early exit.
        """
        monkeypatch.delitem(sys.modules, "pytest", raising=False)
        monkeypatch.setattr(
            "scripts.working_memory.store_path_origin",
            lambda: STORE_ORIGIN_HOME,
        )

        _refuse_ambient_sync_from_a_redirected_store(None, None)

    @pytest.mark.parametrize(
        "target,claude_md_root",
        [
            (Path("/tmp/named-target/CLAUDE.md"), None),
            (None, Path("/tmp/declared-root")),
        ],
        ids=["explicit-target", "declared-root"],
    )
    def test_a_caller_that_declares_its_destination_is_exempt(
        self, monkeypatch, target, claude_md_root
    ):
        """THE EXEMPTIONS THE CLI ARMS CANNOT REACH, because neither parameter has
        a CLI flag. They are the shape every in-suite caller uses, so removing
        either would break the suite rather than the hazard.

        MUTANT that reddens this arm: delete either early return. The
        corresponding parametrized case then raises.
        """
        monkeypatch.delitem(sys.modules, "pytest", raising=False)
        monkeypatch.setattr(
            "scripts.working_memory.store_path_origin",
            lambda: STORE_ORIGIN_ENV,
        )

        _refuse_ambient_sync_from_a_redirected_store(target, claude_md_root)


class TestTheDeclaredProjectDirCheck:
    """The containment helper the exemption rests on.

    IT IS PINNED SEPARATELY BECAUSE ITS WRONG FORM IS THE TEMPTING ONE. Testing
    that the variable is SET is one character shorter to write and exempts the
    escape the guard exists to catch, so the difference between the two forms
    needs its own arm rather than a comment.
    """

    def test_an_unset_variable_is_not_a_declaration(self, tmp_path, monkeypatch):
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        assert _target_is_inside_the_declared_project_dir(tmp_path / "CLAUDE.md") is False

    def test_an_empty_variable_is_not_a_declaration(self, tmp_path, monkeypatch):
        """An empty value is unset, not a declaration of the root directory."""
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", "")
        assert _target_is_inside_the_declared_project_dir(tmp_path / "CLAUDE.md") is False

    def test_a_target_inside_the_declared_root_is_a_declaration(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        assert _target_is_inside_the_declared_project_dir(
            tmp_path / ".claude" / "CLAUDE.md"
        ) is True

    def test_a_target_outside_the_declared_root_is_the_escape(
        self, tmp_path, monkeypatch
    ):
        """THE CASE A PRESENCE CHECK WOULD GET WRONG.

        The variable is SET and resolution still landed elsewhere, which is the
        incident. A check that asked only whether the variable is set would
        return True here and exempt the write.

        MUTANT that reddens this arm: replace the containment comparison with
        `return bool(declared)`.
        """
        declared = tmp_path / "declared"
        declared.mkdir()
        elsewhere = tmp_path / "elsewhere"
        elsewhere.mkdir()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(declared))
        assert _target_is_inside_the_declared_project_dir(
            elsewhere / "CLAUDE.md"
        ) is False


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    """Run git and require success. Real git, never a simulation of one.

    The predicate under test shells out to `git rev-parse --git-common-dir`,
    so a fixture that models a repository with plain directories is measuring
    the non-repo branch and nothing else.
    """
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                       text=True, timeout=60)
    assert r.returncode == 0, f"git {' '.join(args)} failed: {r.stderr}"
    return r


class TestTheCardinalFallthroughSurvives:
    """A REAL WORKTREE reaching the MAIN checkout's document must still WRITE.

    🔴 WHY THIS CLASS EXISTS, AND IT IS NOT A RESTATEMENT OF THE ARM ABOVE.
    The guard's own docstring names this as the cardinal over-block: PACT
    declares CLAUDE_PROJECT_DIR as a worktree, CLAUDE.md is gitignored and
    therefore absent there, and resolution falls through to the main
    checkout's file on purpose. Refusing that breaks the memory display for
    every worktree session — including the one this suite is running in.

    NOTHING IN THE SUITE WAS DRIVING IT. Every other fixture in this file
    builds plain directories, so `same_repository` reaches its non-repo branch
    and returns False; those arms cannot distinguish a guard that allows the
    fall-through from one that refuses everything. The nearest existing
    coverage lives in the pin-resolver suite and uses a SUBDIRECTORY, with a
    comment calling it "structurally the worktree case".

    A SUBDIRECTORY IS NOT STRUCTURALLY THE WORKTREE CASE, AND THE DIFFERENCE
    IS A BRANCH. Measured with real git:

        git -C <main>           rev-parse --git-common-dir  ->  .git
        git -C <main>/sub       rev-parse --git-common-dir  ->  ../.git
        git -C <main>/sub/deep  rev-parse --git-common-dir  ->  ../../.git
        git -C <worktree>       rev-parse --git-common-dir  ->  /abs/.../main/.git

    A subdirectory returns a RELATIVE path and a worktree returns an ABSOLUTE
    one, so they take opposite sides of `same_repository`'s
    `if not common_dir.is_absolute()` join. The subdir arm exercises the join;
    the cardinal case skips it. Only the case below covers the branch PACT
    actually runs on every session.

    Verdicts measured on the same fixture, all seven:

        same_repository(worktree,    main)      True   <- the cardinal case
        same_repository(main,        worktree)  False  <- argument order matters
        same_repository(subdir,      root)      True
        same_repository(root,        subdir)    False
        same_repository(deep subdir, root)      True
        same_repository(worktree,    itself)    False  (unreachable: the guard
                                                 returns on declared == resolved
                                                 before the predicate is asked)
        same_repository(non-git,     main)      False  <- every other arm here
    """

    def test_a_real_worktree_still_projects_into_the_main_checkout(self, tmp_path):
        """THE OVER-BLOCK ARM. If this reddens, every worktree session has lost
        its working-memory display — which is a strictly worse outcome than the
        under-block the sibling arm above closed.

        MUTANT that reddens this arm: delete the `same_repository(...)` return
        from `_refuse_ambient_sync_on_declared_scope_escape`. The declared
        worktree then differs from the resolved main root, no exemption
        applies, and the cardinal fall-through is refused.
        """
        main = tmp_path / "mainrepo"
        (main / ".claude").mkdir(parents=True)
        (main / ".claude" / "CLAUDE.md").write_text(_SEED_DOCUMENT, encoding="utf-8")
        _git("init", "-q", ".", cwd=main)
        _git("config", "user.email", "t@example.invalid", cwd=main)
        _git("config", "user.name", "t", cwd=main)
        # A TRACKED FILE THAT IS NOT THE DOCUMENT. `git worktree add` needs a
        # commit, and `.claude/` is covered by the operator's global gitignore
        # — which is WHY this whole fall-through exists, so the fixture leans
        # on it rather than forcing the document into the index.
        (main / "README").write_text("seed\n", encoding="utf-8")
        _git("add", "README", cwd=main)
        _git("commit", "-qm", "seed", cwd=main)

        worktree = tmp_path / "wt"
        _git("worktree", "add", "-q", str(worktree), "-b", "wt", cwd=main)
        assert not (worktree / ".claude" / "CLAUDE.md").exists(), (
            "the fixture must reproduce the real shape — a worktree with NO "
            "CLAUDE.md of its own, which is what forces the fall-through"
        )

        target = main / ".claude" / "CLAUDE.md"
        before = target.read_bytes()

        env = _base_env(tmp_path)
        env["CLAUDE_PROJECT_DIR"] = str(worktree)
        result = _run_cli(env, worktree, "save", _save_payload("cardinal-worktree-arm"))

        assert _sync_status(result) == SyncResult.WROTE, (
            "a save from a real git worktree, declaring that worktree and "
            "falling through to the MAIN checkout's CLAUDE.md, was refused. "
            "This is the cardinal over-block the escape guard is shaped to "
            "avoid: CLAUDE.md is gitignored in a worktree, so this is the "
            "NORMAL path for every PACT session, not an edge case. Check that "
            "`same_repository(declared, resolved)` is still consulted and that "
            "its arguments are still in DECLARATION-FIRST order — swapping "
            "them returns False here and nothing else would fail."
        )
        assert target.read_bytes() != before, (
            "the sync reported WROTE but the main checkout's document did not "
            "change — the projection went somewhere else"
        )
