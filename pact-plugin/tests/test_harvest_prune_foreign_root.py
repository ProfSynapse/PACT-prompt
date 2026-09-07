"""The prune's foreign-root case: absence under one config root verifies nothing.

The gate this file closes: a ledger section whose session directory is absent
under the READER's config root must be retained, and retained ON THE GROUND
that the root is unresolvable — not on the ground that no journal was found.

WHY THE GROUND AND NOT JUST THE VERDICT. The live ledger's one foreign-root
section carries no journal, so a verdict-only assertion passes under the fixed
rule AND under the rule it replaced, and would keep passing while testing
nothing. The discriminating case the live ledger cannot supply is a section
that is absent under the reader's root and PRESENT WITH A COMPLETE JOURNAL
under another — one that a reader able to resolve it would remove. This file
builds that case.

WHAT IS EXECUTED AND WHAT IS READ, stated so neither is mistaken for the other:

- EXECUTED — the session-directory path template and the journal filename are
  extracted from the skill and resolved against two real config roots on disk;
  the skill's own `session_journal.py read-last` command is run, unmocked,
  against the foreign journal. That establishes the fixture really carries the
  discriminating property rather than being a second no-journal case.
- READ — the verdict and its ground are a sentence an agent follows, not a
  command it runs. Consolidation Step 3 item 2 has no executable existence
  test, so that half of the gate is a structural assertion over the clause's
  own shape: which clause resolves the absent case, what it names as its
  ground, and that it sits ahead of any journal predicate. THE GATE AS
  SPECIFIED IS THEREFORE NOT FULLY MECHANISABLE, and this docstring is the
  honest label rather than a phrase pin dressed as an execution arm.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL_FILE = PLUGIN_ROOT / "skills" / "pact-handoff-harvest" / "SKILL.md"

# Two synthetic sections. They differ ONLY in the property the gate must not
# depend on: whether a journal exists somewhere the reader cannot see.
WITH_JOURNAL = ("alpha", "11111111-1111-1111-1111-111111111111")
NO_JOURNAL = ("beta", "22222222-2222-2222-2222-222222222222")

# BOTH placeholders are required, and the match must be UNIQUE. Item 1 carries
# TWO config-dir-rooted forms — this concrete path and a `*`-glob for headers
# that name no session — and a looser pattern silently takes whichever comes
# first. MEASURED: with the concrete form removed, a `[^`]+` pattern fell
# through to the glob, built a path containing a literal `*`, and every arm
# below still passed because a nonexistent path is a nonexistent path. The arm
# was green for the wrong reason and no assertion could see it.
_PATH_TEMPLATE = re.compile(
    r"`(\{config_dir\}/pact-sessions/[^`]*\{project\}[^`]*\{session_id\}[^`]*)`"
)
_JOURNAL_NAME = re.compile(r"`\{that dir\}/([^`]+)`")
_READ_LAST = re.compile(r'python3 "\{plugin_root\}/([^"]+)" (read-last)')


def consolidation_step3(skill_text):
    """Consolidation Step 3, sliced from inside the Consolidation section.

    NOT `skill_text.find("### Step 3")`: Standard Harvest has its own Step 3
    EARLIER in the file, so a file-wide search reads the wrong block and every
    absence drawn from it would be an absence from an unrelated section.
    """
    start = skill_text.find("## Consolidation Harvest Workflow")
    assert start != -1, "no Consolidation Harvest Workflow section"
    block = skill_text[start:]
    end = block.find("## Knowledge Extraction Guide")
    block = block if end == -1 else block[:end]
    step3 = block[block.find("### Step 3"):]
    step4 = step3.find("### Step 4")
    step3 = step3 if step4 == -1 else step3[:step4]
    assert "Consolidate and Prune" in step3, "sliced the wrong Step 3"
    return step3


@pytest.fixture
def step3():
    return consolidation_step3(SKILL_FILE.read_text())


@pytest.fixture
def roots(tmp_path, step3):
    """Two config roots. The reader's holds neither session; the foreign root
    holds the WITH_JOURNAL session, with a journal that verifies complete."""
    found = _PATH_TEMPLATE.findall(step3)
    assert len(found) == 1, (
        f"expected exactly one config-dir-rooted session path carrying both "
        f"placeholders in a {len(step3)}-char Step 3; found {len(found)}: {found}"
    )
    template = found[0]
    journals = _JOURNAL_NAME.findall(step3)
    assert len(journals) == 1, (
        f"expected exactly one journal filename in a {len(step3)}-char Step 3; "
        f"found {len(journals)}: {journals}"
    )

    def session_dir(config_dir, project, session_id):
        rel = (
            template.replace("{config_dir}", str(config_dir))
            .replace("{project}", project)
            .replace("{session_id}", session_id)
        )
        return Path(rel)

    reader = tmp_path / "reader" / ".claude"
    foreign = tmp_path / "foreign" / ".claude"
    live = session_dir(foreign, *WITH_JOURNAL)
    live.mkdir(parents=True)
    (live / journals[0]).write_text(
        json.dumps({"type": "session_start", "ts": "2026-09-01T00:00:00+00:00"})
        + "\n"
        + json.dumps({"type": "session_end", "ts": "2026-09-01T01:00:00+00:00"})
        + "\n"
    )
    return {
        "session_dir": session_dir,
        "journal_name": journals[0],
        "reader": reader,
        "foreign": foreign,
    }


def read_last(session_dir, event_type, step3):
    """Run the command item 3 names, unmocked, and return the parsed event."""
    found = _READ_LAST.findall(step3)
    assert len(found) == 1, (
        f"expected exactly one read-last invocation in a {len(step3)}-char "
        f"Step 3; found {len(found)}: {found}"
    )
    script_rel, subcommand = found[0]
    script = PLUGIN_ROOT / script_rel
    assert script.is_file(), script
    done = subprocess.run(
        [sys.executable, str(script), subcommand,
         "--session-dir", str(session_dir), "--type", event_type],
        capture_output=True, text=True, check=True,
    )
    return json.loads(done.stdout)


class TestForeignRootSectionCannotBeVerified:
    def test_the_reader_sees_the_same_nothing_for_both_sections(self, roots):
        """THE GROUND, measured. Population: 2 sections, 1 reader root.

        The two sections differ in whether a complete journal exists under a
        DIFFERENT root. From the reader's root the observations are identical,
        so no verdict reached from the reader's root can be riding the journal.
        """
        observed = {}
        for label, (project, session_id) in (
            ("with journal elsewhere", WITH_JOURNAL),
            ("no journal anywhere", NO_JOURNAL),
        ):
            path = roots["session_dir"](roots["reader"], project, session_id)
            observed[label] = (path.exists(), (path / roots["journal_name"]).exists())

        assert observed["with journal elsewhere"] == (False, False)
        assert observed["no journal anywhere"] == (False, False)
        assert len(set(observed.values())) == 1, observed

    def test_the_discriminating_section_is_complete_under_its_own_root(self, roots, step3):
        """The fixture really carries the property the live ledger cannot supply.

        Runs the skill's own read-last command against the foreign journal and
        applies item 4's ordering rule. A complete verdict here is what makes
        the arm above discriminating: a reader able to resolve this section
        WOULD remove it, so retention cannot be explained by a missing journal.
        (Item 4's rule is re-applied here to characterise the FIXTURE. The
        instruction under test is item 2, asserted structurally below.)
        """
        live = roots["session_dir"](roots["foreign"], *WITH_JOURNAL)
        assert (live / roots["journal_name"]).is_file()

        start = read_last(live, "session_start", step3)
        ended = read_last(live, "session_end", step3)
        paused = read_last(live, "session_paused", step3)

        assert start is not None
        assert ended is not None or paused is not None
        newest = max(e["ts"] for e in (ended, paused) if e is not None)
        assert newest > start["ts"], "fixture journal does not verify complete"

    def test_absent_directory_stays_on_the_root_and_not_on_the_journal(self, step3):
        """§8.1's ground assertion, structurally.

        The clause that resolves an absent directory must name the ROOT as its
        ground and must carry no journal predicate — a retention explained by
        a missing journal is the wrong-reason pass this gate exists to catch.
        """
        item2 = step3[step3.find("2. **Existence.**"):]
        end = item2.find("3. **Reads.**")
        assert end != -1, "item 2 does not run into item 3 — Step 3 changed shape"
        item2 = item2[:end]

        split = item2.find("If the directory exists")
        assert split != -1, (
            "item 2 no longer carries a separate directory-exists clause; the "
            "absent case and the journal case may have been merged"
        )
        absent_clause = item2[:split]

        assert "does not exist" in absent_clause
        assert "it stays" in absent_clause
        assert "from this root" in absent_clause, (
            f"the absent-directory clause does not name the root as its ground: "
            f"{absent_clause!r}"
        )
        # THE LOAD-BEARING ASSERTION. Base rate stated: `journal` appears
        # elsewhere in item 2 (the directory-exists clause) and elsewhere in
        # Step 3, so this is scoped to the absent clause alone.
        assert "journal" not in absent_clause.lower(), (
            f"the absent-directory verdict now depends on a journal predicate "
            f"in a {len(absent_clause)}-char clause: {absent_clause!r}"
        )
        assert step3.lower().count("journal") > 1, "base rate check read an empty Step 3"

    def test_existence_is_decided_before_any_journal_is_read(self, step3):
        """The verdict must be reached at item 2, before item 3 runs."""
        existence = step3.find("2. **Existence.**")
        reads = step3.find("3. **Reads.**")
        assert -1 < existence < reads, (existence, reads)
