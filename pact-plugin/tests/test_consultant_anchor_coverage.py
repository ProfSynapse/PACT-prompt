"""Behavioural pins for CONSULTANT coverage — the most-recently-completed anchor.

Location: pact-plugin/tests/test_consultant_anchor_coverage.py
Summary: pins `owner_anchor_tasks`, the expiry asymmetry in `has_live_listed_task`,
         the removed status filter in `any_listed_task_flagged`, and the
         write-time-only `anchor_completed` field on `_sanitize_record`.
Used by: the suite. No module-level sys.path.insert — path setup is
         conftest-owned; see tests/test_path_setup_pin.py.

THE DEFECT BEING PINNED. Every layer was keyed on an owned `in_progress` task,
so a teammate in CONSULTANT MODE — which the framework defines as a supported
state, entered when a task is done and no follow-up is available — owned zero
`in_progress` tasks and was invisible to all of it. Worse, the same agent could
not flag the wait either, because `intentional_wait` is task metadata. Both
halves of the mechanism had the same hole for the same reason.

The fix anchors a consultant on its MOST RECENTLY COMPLETED task instead, and
marks the resulting record so that expiry does not immediately kill it.

🔴 THE PROOF STANDARD FOR THIS FILE IS A REVERT-TO-PRE-FIX MUTATION, NOT A
TOTAL BREAK. Measured on the sibling fix: breaking `wait_scope_anchor` outright
killed nine pre-existing arms, while reverting it to the previous behaviour
killed ZERO of 124. Destroying a function is not the regression anyone causes;
restoring the simpler earlier version because it reads cleaner is. Every arm
below was verified against the second kind.

NON-COVERAGE, STATED. These pin the PREDICATES. They do not pin that the
registry writer actually calls them with a consultant's frame — that is Layer
1's seam — nor that consultant mode is entered correctly, which is a platform
behaviour no test here observes.
"""

from __future__ import annotations

import pytest

from shared.background_work import (
    _sanitize_record,
    any_listed_task_flagged,
    has_live_listed_task,
    owner_anchor_tasks,
)

REGISTERED_AT = "2026-09-12T10:00:00+00:00"

# A store holding all three shapes at once, so each arm discriminates against
# the others rather than against an empty set.
#   alice  — a teammate: two in_progress tasks
#   bob    — a consultant: no in_progress, two completed, ids "3" and "20"
#   carol  — neither: a pending task only
TASKS = [
    {"id": "7", "status": "in_progress", "owner": "alice"},
    {"id": "9", "status": "in_progress", "owner": "alice"},
    {"id": "3", "status": "completed", "owner": "bob"},
    {"id": "20", "status": "completed", "owner": "bob"},
    {"id": "5", "status": "pending", "owner": "carol"},
]


def _record(task_ids, **over) -> dict:
    base = {"agent_name": "bob", "session_id": "s", "task_ids": task_ids,
            "registered_at": REGISTERED_AT}
    base.update(over)
    return base


class TestOwnerAnchorTasks:
    """Which tasks anchor a launch, and whether they are live or completed."""

    def test_a_teammate_anchors_on_ALL_its_in_progress_tasks(self):
        """Not one. The exactly-one rule silently disabled Layer 1 for any
        teammate holding two, which `pact-teachback` explicitly permits."""
        assert owner_anchor_tasks(TASKS, "alice") == (["7", "9"], False)

    def test_a_consultant_anchors_on_its_MOST_RECENTLY_COMPLETED_task(self):
        """The whole fix. Zero in_progress tasks used to mean no record at all."""
        assert owner_anchor_tasks(TASKS, "bob") == (["20"], True)

    def test_recency_is_by_INTEGER_id_not_string_order(self):
        """🔴 THE SILENT ONE. bob's completed ids are "3" and "20". A string
        sort returns "3"; the integer sort returns "20".

        THIS IS THE ARM MOST WORTH HAVING, because a string sort produces a
        WRONG ANSWER THAT NEVER SURFACES AS A FAILURE — the record is written,
        the registry looks healthy, the advisory cites the wrong task, and
        nothing anywhere else notices. Every other defect in this family
        announces itself by producing no record.
        """
        ids, _ = owner_anchor_tasks(TASKS, "bob")
        assert ids == ["20"], (
            "anchored on %r — a STRING sort returns '3' because '3' > '20' "
            "lexically. The ids are compared as integers precisely so that "
            "task 20 beats task 3." % (ids,)
        )

    def test_a_PENDING_task_anchors_nothing(self):
        """Pending is neither live work nor a completed anchor. Discriminates
        against an implementation that falls back to "any task at all"."""
        assert owner_anchor_tasks(TASKS, "carol") == ([], False)

    def test_an_unknown_owner_anchors_nothing(self):
        assert owner_anchor_tasks(TASKS, "nobody") == ([], False)


class TestTheExpiryAsymmetryInBothDirections:
    """🔴 PINNED IN BOTH DIRECTIONS DELIBERATELY, because the `anchor_completed`
    early return looks like it should apply to everyone.

    A TEAMMATE's record expires when its listed task completes: the task
    leaving `in_progress` is the signal that the work it anchored is over.

    A CONSULTANT's record must NOT, because its anchor was ALREADY completed at
    the moment the record was written. That signal is spent before it can fire,
    so applying the same rule would kill every consultant row instantly and the
    coverage this fix adds would be inert on arrival.

    COVERAGE YES, EXPIRY PARITY NO — a consultant row is bounded by the 24h TTL
    alone. An arm on either direction by itself reads as an inconsistency; the
    pair is what makes it an asymmetry someone must keep deliberately.
    """

    COMPLETED_ANCHOR = [{"id": "3", "status": "completed", "owner": "bob"}]

    def test_a_TEAMMATE_record_expires_when_its_task_completes(self):
        assert has_live_listed_task(_record(["3"]), self.COMPLETED_ANCHOR) is False

    def test_a_CONSULTANT_record_does_NOT_expire_on_the_same_input(self):
        """Identical record and identical task store — the ONLY difference is
        the write-time flag, which is what makes this an asymmetry rather than
        two unrelated behaviours."""
        consultant = _record(["3"], anchor_completed=True)
        assert has_live_listed_task(consultant, self.COMPLETED_ANCHOR) is True, (
            "a consultant's anchor is completed BY CONSTRUCTION at write time, "
            "so expiring on it kills the row the moment it is created and this "
            "entire fix becomes inert. Bounded by the 24h TTL instead."
        )


class TestTheStatusFilterIsGoneFromTheFlagCheck:
    """A consultant's wait sits on a COMPLETED task, so a status filter here
    made its flag invisible and the advisory fired at an agent that had
    correctly declared its wait.

    NON-COVERAGE: this pins that a flag on a completed listed task is SEEN. It
    does not pin what any caller then does with that knowledge.
    """

    def test_a_valid_wait_on_a_COMPLETED_listed_task_is_seen(self):
        flagged = [{"id": "3", "status": "completed", "owner": "bob",
                    "metadata": {"intentional_wait": {
                        "reason": "awaiting_lead_completion",
                        "expected_resolver": "lead",
                        "since": REGISTERED_AT}}}]
        assert any_listed_task_flagged(_record(["3"]), flagged) is True, (
            "restoring an `in_progress` filter here makes a consultant's "
            "correctly-flagged wait invisible, and the advisory then fires at "
            "the one population that did the right thing"
        )


class TestAnchorCompletedIsAWriteTimeFactNotAStatus:
    """`_sanitize_record` keeps the flag ONLY when True.

    Absence defaulting to False is correct rather than merely convenient: every
    record written before this field existed is teammate-shaped, and must keep
    expiring exactly as it did. Persisting an explicit False would be noise on
    every row; persisting True is the only case that changes a decision.

    NON-COVERAGE: this pins the round-trip through the sanitizer. It does not
    pin that the WRITER sets the flag correctly — that is `bind_launcher_identity`.
    """

    @pytest.mark.parametrize(
        "given,expected_present",
        [(True, True), (False, False)],
        ids=["True-is-kept", "False-is-dropped"],
    )
    def test_the_flag_survives_only_when_True(self, given, expected_present):
        out = _sanitize_record(_record(["3"], anchor_completed=given))
        assert ("anchor_completed" in out) is expected_present

    def test_a_record_without_the_field_stays_teammate_shaped(self):
        """The pre-existing-row case: no flag means it expires, as before."""
        out = _sanitize_record(_record(["3"]))
        assert "anchor_completed" not in out
        assert has_live_listed_task(
            out, [{"id": "3", "status": "completed", "owner": "bob"}]) is False
