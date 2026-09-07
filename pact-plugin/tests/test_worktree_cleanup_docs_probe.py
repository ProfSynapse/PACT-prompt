"""Site 3's docs/ probe: the states an empty listing can mean.

`git worktree remove` deletes `docs/` irrecoverably, and `docs/` is gitignored,
so an instrument that returns empty over a full directory authorises the
removal of artifacts nobody harvested. `skills/worktree-cleanup/SKILL.md`
Step 1.5 answers that with TWO commands — a presence marker and an ignore-blind
listing — because neither alone separates the states.

THESE ARMS EXECUTE THE SHIPPED COMMANDS. Both are extracted from the fence and
run, unmodified apart from the path substitution the step itself specifies,
against directory states built on disk. That is what makes them survive a
reword: a phrase pin over the same block disarms silently when the prose is
correctly rewritten, and this arc rewrote that prose three times.

THE OBSERVATION TRIPLE IS THE GUARD, not a separate verdict assertion. The step
routes `DIR_ABSENT` straight to removal, so asserting that a state which may
hold unreadable artifacts reports `CANNOT_OBSERVE` rather than `DIR_ABSENT` IS
the assertion that it does not reach the destructive branch.

BINARY RESOLUTION, stated because it bounds what these arms prove: the commands
run under `/bin/bash` with `PATH` pinned to `/usr/bin:/bin`, so `find` is the
system `find` and not whatever an operator has shimmed onto their own `PATH`.
This skill ships to consumers, so the system binary is the honest subject. A
consumer whose `find` is a different implementation is outside what is measured
here.

EUID: the mode-000 arms depend on the process not being root. As root the
permission bits do not bite and those arms fail LOUDLY on the marker value
rather than passing silently, so no skip is registered for them — read this
line before deleting an arm that reddens on a root CI runner.
"""

import os
import re
import subprocess
from pathlib import Path

import pytest

SKILL_FILE = (
    Path(__file__).resolve().parents[1] / "skills" / "worktree-cleanup" / "SKILL.md"
)
BASH = Path("/bin/bash")
SAFE_PATH = "/usr/bin:/bin"

_FENCE = re.compile(r"```bash\n(.*?)```", re.DOTALL)

pytestmark = pytest.mark.skipif(not BASH.exists(), reason="no /bin/bash")


def step_1_5(skill_text):
    start = skill_text.find("### Step 1.5:")
    assert start != -1, "no Step 1.5 in worktree-cleanup SKILL.md"
    block = skill_text[start:]
    end = block.find("### Step 2:")
    assert end != -1, "Step 1.5 does not run into Step 2 — the file changed shape"
    return block[:end]


def probe_commands(skill_text):
    """The marker command and the listing command, in the order the step gives.

    Exactly one fence must sit in Step 1.5. A second would make `search` take
    whichever came first and the arms would measure a command nobody meant.
    """
    block = step_1_5(skill_text)
    fences = _FENCE.findall(block)
    assert len(fences) == 1, (
        f"expected exactly one bash fence in a {len(block)}-char Step 1.5; "
        f"found {len(fences)}"
    )
    lines = [ln for ln in fences[0].strip().splitlines() if ln.strip()]
    assert len(lines) == 2, f"expected a marker line and a listing line; got {lines}"
    marker, listing = lines
    assert "-d " in marker, f"the presence marker is gone: {marker!r}"
    assert marker.count("echo") == 3, (
        f"the marker no longer reports three states — an unobservable parent "
        f"and an absent directory may have collapsed onto one answer: {marker!r}"
    )
    assert listing.startswith("find "), f"the listing is not `find`: {listing!r}"
    assert " -L" in listing, (
        f"`find` no longer follows symlinks, so a symlinked docs/ lists nothing "
        f"and reads as empty: {listing!r}"
    )
    return marker, listing


@pytest.fixture
def probe():
    marker, listing = probe_commands(SKILL_FILE.read_text())

    def run(worktree):
        def shell(command):
            done = subprocess.run(
                [str(BASH), "-c", command.replace("{abs_worktree}", str(worktree))],
                capture_output=True, text=True, env={"PATH": SAFE_PATH},
                # Deliberately NOT the worktree: the step specifies an absolute
                # path precisely so a wrong CWD cannot produce a false empty,
                # and running from elsewhere is how that gets measured.
                cwd="/",
            )
            return done.returncode, done.stdout.strip()

        _, mark = shell(marker)
        code, out = shell(listing)
        return mark, code, len([ln for ln in out.splitlines() if ln.strip()])

    return run


@pytest.fixture
def worktree(tmp_path):
    """A worktree whose `docs/` each arm shapes for itself."""
    root = tmp_path / "wt"
    root.mkdir()
    try:
        yield root
    finally:
        # mode-000 arms would otherwise defeat tmp_path cleanup.
        for path in (root / "docs", root):
            if path.exists():
                os.chmod(path, 0o755)


def populate(docs, count=3):
    docs.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        (docs / f"artifact-{i}.md").write_text("phase artifact\n")


class TestDocsProbeSeparatesTheStates:
    """Every state an empty listing can mean, and what the probe reports."""

    def test_absent_docs_reports_absent(self, probe, worktree):
        # §8.3's third arm. It MUST report absent, or the guard blocks the
        # no-team manual cleanup path the file protects.
        assert probe(worktree) == ("DIR_ABSENT", 1, 0)

    def test_empty_docs_reports_present_and_lists_nothing(self, probe, worktree):
        (worktree / "docs").mkdir()
        assert probe(worktree) == ("DIR_PRESENT", 0, 0)

    def test_gitignored_artifacts_are_listed(self, probe, worktree):
        # §8.3's second arm. `docs/` is gitignored in the real tree, so an
        # ignore-aware instrument returns empty over exactly this state. The
        # listing is ignore-blind, so it must find all three.
        populate(worktree / "docs")
        assert probe(worktree) == ("DIR_PRESENT", 0, 3)

    def test_absolute_path_survives_a_foreign_cwd(self, probe, worktree):
        # §8.3's first arm. The probe fixture runs from `/`, never from the
        # worktree, so a path that had become relative would list nothing here.
        populate(worktree / "docs")
        marker, _, files = probe(worktree)
        assert (marker, files) == ("DIR_PRESENT", 3)

    def test_symlinked_docs_is_followed(self, probe, worktree, tmp_path):
        # A `find` without `-L` reports zero files over a populated symlinked
        # docs/ — indistinguishable from empty, and it proceeds to removal.
        target = tmp_path / "elsewhere"
        populate(target, count=2)
        (worktree / "docs").symlink_to(target, target_is_directory=True)
        assert probe(worktree) == ("DIR_PRESENT", 0, 2)

    def test_unreadable_docs_is_present_but_unlistable(self, probe, worktree):
        # The marker says present, the listing fails: `docs/` may hold
        # artifacts the instrument could not read. Exit status ALONE cannot
        # separate this from absent — both are 1 — which is why the marker
        # carries the discrimination.
        populate(worktree / "docs")
        os.chmod(worktree / "docs", 0o000)
        assert probe(worktree) == ("DIR_PRESENT", 1, 0)

    def test_unreadable_parent_is_not_reported_as_absent(self, probe, worktree):
        """THE ARM THAT DISCRIMINATES THE SHIPPED MARKER FROM ITS PREDECESSOR.

        A marker consulting `[ -d ]` alone answers false on an unreadable
        PARENT exactly as it does on a genuinely absent `docs/`, so a populated
        worktree the instrument cannot enter routes onto the proceed branch and
        is removed irrecoverably. The third state is what separates them.
        """
        populate(worktree / "docs")
        os.chmod(worktree, 0o000)
        marker, code, files = probe(worktree)
        assert marker == "CANNOT_OBSERVE", (
            f"an unreadable worktree reports {marker!r}; DIR_ABSENT here routes "
            f"a populated docs/ straight to an irrecoverable removal"
        )
        assert (code, files) == (1, 0)


class TestProceedBranchAdmitsOnlyTheSafeStates:
    """The routing, which the observation arms above cannot see.

    HONEST LABEL: a prose pin. The observations are executed; which branch each
    one takes is a sentence an agent follows. It is keyed on the bullet's own
    conditions rather than on its wording, and it is here because the commands
    surviving while their routing widens is a regression every arm above stays
    green through.
    """

    def test_proceed_names_both_safe_states_and_neither_unsafe_one(self):
        """The catch-all sits INSIDE the proceed bullet, deliberately.

        An unsure reader takes the branch that ends the task, so the default
        action has to live where that reader lands rather than in a fourth
        bullet below them. That is why this arm splits the bullet at its own
        clause boundary instead of reading the whole line: the two halves make
        opposite claims and a whole-line search cannot tell them apart.
        """
        block = step_1_5(SKILL_FILE.read_text())
        bullet = next(
            (ln for ln in block.splitlines() if "proceed directly to Step 2" in ln), ""
        )
        assert bullet, "no proceed bullet in Step 1.5"
        marker = "**Any other result**"
        assert marker in bullet, (
            f"the proceed bullet no longer carries its catch-all clause, so an "
            f"unsure reader has no default but to proceed: {bullet!r}"
        )
        proceed, catch_all = bullet.split(marker, 1)

        # The proceed half admits exactly the two states that cannot hold
        # unread artifacts.
        assert "DIR_ABSENT" in proceed
        assert "DIR_PRESENT" in proceed
        assert "CANNOT_OBSERVE" not in proceed, (
            f"the proceed clause now admits an unobservable worktree: {proceed!r}"
        )

        # The catch-all half carries the unobservable state and ends on the
        # non-destructive branch.
        assert "CANNOT_OBSERVE" in catch_all
        assert "loud-warning" in catch_all, (
            f"the catch-all no longer routes anywhere non-destructive: {catch_all!r}"
        )
        # Base rate, so a zero above is distinguishable from an empty read.
        assert block.count("CANNOT_OBSERVE") >= 2, "base-rate check read an empty block"
