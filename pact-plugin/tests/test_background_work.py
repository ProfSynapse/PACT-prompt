"""Behaviour pins for shared/background_work.py.

Location: pact-plugin/tests/test_background_work.py
Summary: pins the registry's record schema, the R5 task_ids list, the Layer 3
         two-threshold clock, the identity bind (including the validated
         agent_type route and the collisions it must refuse), and the
         acknowledgment discharge.
Used by: the suite. No module-level sys.path.insert — path setup is
         conftest-owned; see tests/test_path_setup_pin.py.

THESE PIN BEHAVIOUR, NOT FRAME FIELDS. Identity may arrive by `agent_name`,
by an `@`-bearing `agent_id`, or by a validated `agent_type`, and no test
here asserts WHICH field carried it, because that is a property of the
harness rather than of this code. What is pinned is the OUTCOME: a frame
carrying an identity by any accepted route produces a record; a frame
carrying none produces nothing.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from shared.background_work import (
    LEAD_STALE_MINUTES,
    LEAD_UNIDLED_STALE_MINUTES,
    _sanitize_record,
    agent_type_names_a_member,
    bind_launcher_identity,
    classify_wait,
    discharge_acknowledged,
    effective_since,
    is_durable_command,
    lead_stale,
    load_records_for_discharge,
    matching_outstanding,
    record_task_ids,
    outstanding_unflagged,
    unflagged_fire,
    wait_covers_record,
)

TEAM = "probe-team"
T0 = datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _record(**over):
    base = {
        "agent_name": "probe-coder",
        "session_id": "sid",
        "task_ids": ["13"],
        "registered_at": _iso(T0),
    }
    base.update(over)
    return base


def _task(task_id="13", status="in_progress", wait=None, **over):
    task = {"id": task_id, "status": status, "owner": "probe-coder"}
    if wait is not None:
        task["metadata"] = {"intentional_wait": wait}
    task.update(over)
    return task


def _wait(since: datetime, reason="awaiting_blocker_resolution"):
    return {"reason": reason, "expected_resolver": "lead", "since": _iso(since)}


# ---------------------------------------------------------------- schema (R5)


class TestRecordSchema:
    def test_task_ids_list_is_accepted(self):
        assert _sanitize_record(_record())["task_ids"] == ["13"]

    def test_two_task_ids_survive(self):
        assert _sanitize_record(_record(task_ids=["13", "14"]))["task_ids"] == [
            "13",
            "14",
        ]

    def test_scalar_task_id_is_REJECTED_not_coerced(self):
        """A scalar is a malformed write, not an older schema.

        Records are ephemeral team state with a 24h TTL and are never read
        across a version boundary, so coercing a scalar into a one-element
        list would silently reinterpret a record nobody wrote deliberately.
        """
        raw = _record()
        del raw["task_ids"]
        raw["task_id"] = "13"
        assert _sanitize_record(raw) is None

    def test_string_task_ids_is_rejected(self):
        assert _sanitize_record(_record(task_ids="13")) is None

    @pytest.mark.parametrize("bad", [[], [""], ["13", 14], [None], [["13"]]])
    def test_malformed_task_ids_rejected(self, bad):
        assert _sanitize_record(_record(task_ids=bad)) is None

    def test_command_is_truncated_to_240(self):
        out = _sanitize_record(_record(command="x" * 500))
        assert len(out["command"]) == 240

    def test_record_task_ids_is_total(self):
        assert record_task_ids(None) == []
        assert record_task_ids({}) == []
        assert record_task_ids({"task_ids": "nope"}) == []


class TestMatchingByList:
    def test_matches_any_listed_id(self):
        rec = _sanitize_record(_record(task_ids=["13", "14"]))
        assert matching_outstanding(_task("14"), records=[rec]) == rec

    def test_unlisted_id_does_not_match(self):
        rec = _sanitize_record(_record(task_ids=["13"]))
        assert matching_outstanding(_task("99"), records=[rec]) is None


# -------------------------------------------------- Layer 3's two-clock rule


class TestEffectiveSince:
    def test_idled_at_present_uses_the_short_window(self):
        rec = _record(idled_at=_iso(T0))
        since, minutes = effective_since(_sanitize_record(rec))
        assert minutes == LEAD_STALE_MINUTES
        assert since == T0

    def test_idled_at_absent_falls_back_to_registered_at(self):
        """Without this, a missed TeammateIdle disables Layer 3 entirely.

        `stamp_idled_at` is the only writer of `idled_at`, so keying the lead
        surface on that field alone made Layer 3 a consumer of Layer 2 rather
        than a backstop for it.
        """
        since, minutes = effective_since(_sanitize_record(_record()))
        assert minutes == LEAD_UNIDLED_STALE_MINUTES
        assert since == T0

    def test_registered_at_arm_needs_the_longer_window(self):
        rec = _sanitize_record(_record())
        mid = T0 + timedelta(minutes=LEAD_STALE_MINUTES + 1)
        assert lead_stale(rec, now=mid) is False, (
            "registered_at is not evidence of idling; the short window must "
            "not apply to it"
        )
        late = T0 + timedelta(minutes=LEAD_UNIDLED_STALE_MINUTES + 1)
        assert lead_stale(rec, now=late) is True

    def test_idled_at_arm_fires_on_the_short_window(self):
        rec = _sanitize_record(_record(idled_at=_iso(T0)))
        assert lead_stale(rec, now=T0 + timedelta(minutes=LEAD_STALE_MINUTES + 1))

    def test_thresholds_are_distinct(self):
        assert LEAD_UNIDLED_STALE_MINUTES > LEAD_STALE_MINUTES


# ------------------------------------------------------------ the fire predicate


class TestUnflaggedFire:
    def test_fires_when_in_progress_recorded_and_unflagged(self):
        rec = _sanitize_record(_record())
        fire, klass, got = unflagged_fire(_task(), records=[rec])
        assert fire is True and klass == "missing" and got == rec

    def test_does_not_fire_without_a_record(self):
        assert unflagged_fire(_task(), records=[])[0] is False

    def test_does_not_fire_when_the_wait_is_valid(self):
        rec = _sanitize_record(_record())
        assert unflagged_fire(_task(wait=_wait(T0)), records=[rec])[0] is False

    def test_does_not_fire_once_the_task_leaves_in_progress(self):
        rec = _sanitize_record(_record())
        assert unflagged_fire(_task(status="completed"), records=[rec])[0] is False

    @pytest.mark.parametrize(
        "wait,expected",
        [(None, "missing"), ({}, "malformed"), ({"reason": "x"}, "malformed")],
    )
    def test_wait_classes(self, wait, expected):
        task = _task()
        task["metadata"] = {"intentional_wait": wait} if wait is not None else {}
        assert classify_wait(task) == expected

    def test_a_flag_on_EITHER_held_task_silences_the_advisory(self):
        """R5's silencing half, and it points at LESS firing deliberately.

        A teammate holding two tasks who flagged on either has flagged. Under
        the old exactly-one-task rule that teammate got no record at all, so
        this strictly adds coverage without adding a false-positive route.
        """
        rec = _sanitize_record(_record(task_ids=["13", "14"]))
        tasks = [_task("13"), _task("14", wait=_wait(T0))]
        assert unflagged_fire(_task("13"), records=[rec], tasks=tasks)[0] is False

    def test_neither_task_flagged_still_fires(self):
        rec = _sanitize_record(_record(task_ids=["13", "14"]))
        tasks = [_task("13"), _task("14")]
        assert unflagged_fire(_task("13"), records=[rec], tasks=tasks)[0] is True


# ------------------------------------------- the acknowledgment discharge (P1a)


class TestWaitCoversRecord:
    """The discharge predicate. Pure over (task, record) — no session needed."""

    def test_wait_after_the_launch_acknowledges_it(self):
        rec = _sanitize_record(_record())
        assert wait_covers_record(_task(wait=_wait(T0 + timedelta(minutes=1))), rec)

    def test_wait_exactly_at_the_launch_acknowledges_it(self):
        rec = _sanitize_record(_record())
        assert wait_covers_record(_task(wait=_wait(T0)), rec)

    def test_wait_BEFORE_the_launch_does_not_acknowledge_it(self):
        """The comparison is load-bearing, not decoration.

        A wait flagged for an earlier job must not acquit a job launched
        afterwards. Dropping the comparison turns a precise discharge into a
        blanket amnesty.
        """
        rec = _sanitize_record(_record(registered_at=_iso(T0 + timedelta(minutes=5))))
        assert wait_covers_record(_task(wait=_wait(T0)), rec) is False

    def test_no_wait_acknowledges_nothing(self):
        assert wait_covers_record(_task(), _sanitize_record(_record())) is False

    def test_malformed_wait_acknowledges_nothing(self):
        task = _task()
        task["metadata"] = {"intentional_wait": {"reason": "x"}}
        assert wait_covers_record(task, _sanitize_record(_record())) is False

    def test_naive_since_acknowledges_nothing(self):
        """validate_wait rejects tz-naive, so this can never acquit a record."""
        task = _task(wait={"reason": "r", "expected_resolver": "lead",
                           "since": "2026-09-11T12:00:00"})
        assert wait_covers_record(task, _sanitize_record(_record())) is False


class TestDischargeSequences:
    """The four sequences that decide whether Layers 2 and 3 may ship.

    Each is a full sequence rather than a point check, because the defect
    being pinned only exists ACROSS steps: a record that outlives its own
    acknowledgment, and is then cited by a later advisory.

    WHAT IS BEING PREVENTED, AT ITS ACTUAL SIZE: a MISATTRIBUTED advisory,
    not one that fires at a compliant teammate. The threshold counter is
    cleared on every tick where the fire predicate is false, so a teammate
    that flags never accumulates toward it. When the advisory does fire the
    teammate is genuinely idling unflagged — the advice is right and only the
    CITED CAUSE is stale. Sequence 1 pins that the discharge happens; it does
    not pin a false alarm that was never reachable.
    """

    @pytest.fixture(autouse=True)
    def _isolated_team(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))
        (tmp_path / "teams" / TEAM).mkdir(parents=True)

    def _seed(self, **over):
        from shared.background_work import append_record

        assert append_record(_record(**over), team_name=TEAM) is True

    def test_1_flag_then_idle_then_clear_then_idle_DOES_NOT_FIRE(self):
        """The whole point. A teammate that did everything right stays silent."""
        self._seed()
        flagged = _task(wait=_wait(T0 + timedelta(minutes=1)))
        assert discharge_acknowledged(flagged, team_name=TEAM) == 1
        assert load_records_for_discharge(TEAM, now=T0) == []
        # later it clears the wait and keeps working the same task
        assert unflagged_fire(_task(), team_name=TEAM, now=T0)[0] is False

    def test_2_never_flag_then_idle_FIRES(self):
        """The target case must be untouched by the discharge."""
        self._seed()
        assert discharge_acknowledged(_task(), team_name=TEAM) == 0
        assert unflagged_fire(_task(), team_name=TEAM, now=T0)[0] is True

    def test_3_a_wait_discharges_job1_ONLY_and_job2_fires_once_the_wait_clears(
        self,
    ):
        """RENAMED. It previously read `..._FIRES_FOR_JOB2_ONLY`, which
        asserted more than the arm measures: the fire check below runs on a
        task with NO wait and without a `tasks` list, so at that point the
        job-1 flag is already cleared and the R5 silencing gate is not
        evaluated at all. What this arm actually pins — and it is the
        load-bearing half — is that `since >= registered_at` discharges job 1
        and spares job 2. See the sibling class below for what happens while
        the wait is still open, which is the opposite of what the name implied.
        """
        self._seed(registered_at=_iso(T0))
        self._seed(registered_at=_iso(T0 + timedelta(minutes=10)))
        flagged = _task(wait=_wait(T0 + timedelta(minutes=1)))
        assert discharge_acknowledged(flagged, team_name=TEAM) == 1, (
            "exactly one record — job 1 — may be discharged by a wait flagged "
            "before job 2 was launched"
        )
        left = load_records_for_discharge(TEAM, now=T0)
        assert len(left) == 1
        assert left[0]["registered_at"] == _iso(T0 + timedelta(minutes=10))
        # the wait has since been cleared: no valid wait on the task, no tasks list
        assert unflagged_fire(_task(), team_name=TEAM, now=T0)[0] is True


    def test_4_RESIDUAL_flag_and_clear_within_one_turn_keeps_the_record(self):
        """Documented residue, not a bug to fix.

        Discharge runs on TeammateIdle. A teammate that flags and clears
        inside one turn never idles between the two, so nothing observes the
        flag and the record survives. Pinned so the limit is visible rather
        than discovered.
        """
        self._seed()
        # no idle occurs, so discharge_acknowledged is never called
        assert unflagged_fire(_task(), team_name=TEAM, now=T0)[0] is True
        assert len(load_records_for_discharge(TEAM, now=T0)) == 1


class TestSuppressionIsTemporaryNotPermanent:
    """What an OPEN wait does to a job launched after it.

    THE DESIGN DOCUMENT SAYS THIS FIRES. IT DOES NOT, AND THE CODE IS RIGHT.
    §6.2's discharge table reads "job 2's registered_at > the wait's since,
    test fails, job 2 not discharged -> fires". Only the first clause is true.
    The record does survive the discharge — and then nothing surfaces it,
    because the task carries a valid wait.

    THE SUPPRESSION IS OVER-DETERMINED, AND SAYING WHICH GATE DOES IT WOULD BE
    WRONG. `unflagged_fire` consults `any_listed_task_flagged` first and
    `classify_wait` second, and on this input EITHER ALONE suffices: MEASURED,
    disabling `any_listed_task_flagged` entirely leaves both arms below green,
    because `classify_wait` refuses the same frame. So these arms pin an
    OUTCOME with two independent causes, and no arm here should be read as
    evidence about which gate is load-bearing. The R5 silencing gate is
    isolated by `test_a_flag_on_EITHER_held_task_silences_the_advisory`, which
    puts the flag on a DIFFERENT task than the one in hand — the only shape
    where the two gates disagree.

    WHAT THESE TWO ARMS UNIQUELY PIN is the discharge's `since` scoping:
    job 2's record SURVIVES an acknowledgment aimed at job 1, and fires once
    the wait closes. MEASURED — both arms die when `since >= registered` is
    widened to a blanket amnesty and when it is narrowed to never discharge.
    Suppression is temporary; discharge is permanent.

    AND FIRING WOULD BE WORSE THAN A MISSED TICK. The advisory's own text says
    "no flagged wait" — literally false at a teammate holding one open. A
    discredited alarm never recovers, which is the standing posture and what
    decides this.

    Pinned as a pair — suppressed while open, fires once cleared — because
    either arm alone reads as the other's bug.
    """

    @pytest.fixture(autouse=True)
    def _isolated_team(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))
        (tmp_path / "teams" / TEAM).mkdir(parents=True)

    def _two_jobs(self):
        from shared.background_work import append_record

        assert append_record(_record(registered_at=_iso(T0)), team_name=TEAM)
        assert append_record(
            _record(registered_at=_iso(T0 + timedelta(minutes=10))), team_name=TEAM
        )
        flagged = _task(wait=_wait(T0 + timedelta(minutes=1)))
        assert discharge_acknowledged(flagged, team_name=TEAM) == 1
        return flagged

    def test_job2_is_SILENT_while_the_job1_wait_is_still_open(self):
        flagged = self._two_jobs()
        fire, wait_class, record = unflagged_fire(
            flagged, team_name=TEAM, now=T0, tasks=[flagged]
        )
        assert fire is False, (
            "an advisory here would tell a teammate it has no flagged wait "
            "while it holds one open"
        )
        assert wait_class is None
        assert record is not None, "and the record must SURVIVE, not be discharged"
        assert record["registered_at"] == _iso(T0 + timedelta(minutes=10))

    def test_BOTH_gates_independently_refuse_so_NEITHER_reads_AS_DEAD(self):
        """States the over-determination, so nobody has to re-derive it.

        `unflagged_fire` refuses THIS frame twice over: `any_listed_task_flagged`
        returns True and `classify_wait` returns None, and either alone
        suffices. Nothing else asserts that, because every other arm checks the
        combined outcome, which cannot distinguish one gate from two.

        WHAT THIS ARM IS *NOT*. It is not closing a coverage gap. Both gates
        were ALREADY pinned before it existed — MEASURED at primary +
        adversarial scope, with this arm removed: disabling
        `any_listed_task_flagged` kills 5 arms
        (`test_a_flag_on_EITHER_held_task_silences_the_advisory`,
        `..._suppresses_the_surface`, `test_a_FLAGGED_task_is_NOT_surfaced`,
        `test_the_discharge_read_stays_RAW_so_it_can_still_see_a_flag`,
        `test_the_two_alarms_are_EXCLUSIVE_on_one_task`) and disabling
        `classify_wait`'s validation kills 14. Neither gate can be deleted on a
        green suite.

        That correction matters more than the arm. The belief that neither gate
        was pinned came from a TRUE but NARROW measurement — disabling one gate
        left the two suppression arms in this class green — generalised to the
        suite without re-measuring. The arms that pin each gate use a fixture
        where the two gates DISAGREE (flag on a different task than the one in
        hand); this class uses one where they agree, so of course it could not
        see them.

        What is left for this arm to do is name the property: these two agree
        here and disagree elsewhere, so neither is redundant, and a reader who
        mutates one in THIS shape and sees nothing should not conclude it is
        dead.
        """
        from shared.background_work import any_listed_task_flagged

        flagged = self._two_jobs()
        record = matching_outstanding(
            flagged, records=load_records_for_discharge(TEAM, now=T0)
        )
        assert record is not None

        assert any_listed_task_flagged(record, [flagged]) is True, (
            "gate 1 (R5 silencing) no longer refuses this frame"
        )
        assert classify_wait(flagged) is None, (
            "gate 2 (valid-wait) no longer refuses this frame"
        )
        # and gate 2 alone still suppresses, with no task list for gate 1 to read
        assert unflagged_fire(flagged, team_name=TEAM, now=T0, tasks=None)[0] is False

    def test_job2_FIRES_as_soon_as_that_wait_is_cleared(self):
        """The other half. Without it the arm above reads as a swallowed alarm."""
        self._two_jobs()
        cleared = _task()
        fire, wait_class, record = unflagged_fire(
            cleared, team_name=TEAM, now=T0, tasks=[cleared]
        )
        assert fire is True and wait_class == "missing"
        assert record["registered_at"] == _iso(T0 + timedelta(minutes=10)), (
            "and it fires for JOB 2 — job 1 stays discharged"
        )


# ------------------------------------------------ the Layer 3 read path (gates)


class TestOutstandingUnflagged:
    """The gated selector every surface-read path must go through.

    WHY THIS CLASS EXISTS. Layer 2 reached records through `unflagged_fire`,
    which applies the task-status and flagged-wait gates. Layer 3's lead-side
    selector read `load_records` directly and applied NEITHER, so it surfaced
    records for completed tasks and for correctly-flagged waits — while the
    lead-facing text asserts "outstanding launches and no flagged wait".
    MEASURED on one 40-minute-old record: `lead_stale` True (surfaced) against
    `unflagged_fire` False on both gates (refused). One gated consumer, one
    ungated.

    The earlier coverage pinned the gates only on the path that already had
    them — coverage that looks like coverage and is not.
    """

    def test_a_completed_task_is_NOT_surfaced(self):
        rec = _sanitize_record(_record())
        tasks = [_task(status="completed")]
        assert outstanding_unflagged(tasks, records=[rec]) == []

    def test_a_FLAGGED_task_is_NOT_surfaced(self):
        """The clause the lead-facing text asserts and the old path never checked."""
        rec = _sanitize_record(_record())
        tasks = [_task(wait=_wait(T0 + timedelta(minutes=1)))]
        assert outstanding_unflagged(tasks, records=[rec]) == []

    def test_an_in_progress_unflagged_task_IS_surfaced(self):
        """The positive, so the two negatives above are not vacuous."""
        rec = _sanitize_record(_record())
        assert outstanding_unflagged([_task()], records=[rec]) == [rec]

    def test_a_flag_on_EITHER_held_task_suppresses_the_surface(self):
        rec = _sanitize_record(_record(task_ids=["13", "14"]))
        tasks = [_task("13"), _task("14", wait=_wait(T0))]
        assert outstanding_unflagged(tasks, records=[rec]) == []

    def test_an_unknown_task_id_is_NOT_surfaced(self):
        """A record whose tasks are absent from the store cannot be judged."""
        rec = _sanitize_record(_record(task_ids=["99"]))
        assert outstanding_unflagged([_task("13")], records=[rec]) == []

    def test_a_non_list_task_set_surfaces_NOTHING(self):
        """An unevaluable gate must never read as a passed gate.

        Falling back to the ungated record list here is precisely the defect
        this selector exists to remove.
        """
        rec = _sanitize_record(_record())
        assert outstanding_unflagged(None, records=[rec]) == []

    def test_the_discharge_read_stays_RAW_so_it_can_still_see_a_flag(self):
        """Gate B must NOT move into any read the discharge uses.

        `discharge_acknowledged` retires a record BY observing that a valid
        wait covers it. If the loader pre-filtered flagged records away, the
        discharge would never see one and the fix would die silently — green,
        because every test of the gates would still pass.
        """
        rec = _sanitize_record(_record())
        flagged = _task(wait=_wait(T0 + timedelta(minutes=1)))
        assert outstanding_unflagged([flagged], records=[rec]) == []
        assert wait_covers_record(flagged, rec) is True, (
            "the discharge must still be able to see the flagged record that "
            "the surface selector correctly hides"
        )


# ------------------------------------------------------------------ identity


class TestBindLauncherIdentity:
    @pytest.fixture(autouse=True)
    def _team_config(self, tmp_path, monkeypatch):
        import json

        monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))
        team_dir = tmp_path / "teams" / TEAM
        team_dir.mkdir(parents=True)
        (team_dir / "config.json").write_text(
            json.dumps(
                {
                    "leadSessionId": "lead-sid",
                    "members": [
                        {"name": "probe-coder", "agentId": f"probe-coder@{TEAM}",
                         "agentType": "pact-backend-coder"},
                        {"name": "preparer", "agentId": f"preparer@{TEAM}",
                         "agentType": "pact-preparer"},
                    ],
                }
            )
        )
        tasks = tmp_path / "tasks" / TEAM
        tasks.mkdir(parents=True)
        (tasks / "13.json").write_text(
            json.dumps({"id": "13", "status": "in_progress", "owner": "probe-coder"})
        )

    def _frame(self, **over):
        frame = {
            "session_id": "sid",
            "tool_name": "Bash",
            "tool_input": {"command": "echo hi", "run_in_background": True},
        }
        frame.update(over)
        return frame

    def test_step2_route_with_NO_agent_name_key(self):
        """Exercises the `@`-bearing agent_id route on its own.

        Every fixture that supplies `agent_name` passes through Step 1, so
        without this arm the Step-2 route would ship entirely unexecuted —
        and nobody has been able to separate the two on live data.
        """
        frame = self._frame(agent_id=f"probe-coder@{TEAM}")
        assert "agent_name" not in frame
        bound = bind_launcher_identity(frame, TEAM)
        assert bound is not None and bound[0] == "probe-coder"

    def test_step1_route(self):
        bound = bind_launcher_identity(self._frame(agent_name="probe-coder"), TEAM)
        assert bound is not None and bound[0] == "probe-coder"

    def test_validated_agent_type_route(self):
        """The measured in-process shape: agent_type carries the NAME."""
        frame = self._frame(agent_id="0123456789abcdef", agent_type="probe-coder")
        assert "agent_name" not in frame and "@" not in frame["agent_id"]
        bound = bind_launcher_identity(frame, TEAM)
        assert bound is not None and bound[0] == "probe-coder"

    def test_task_ids_is_a_list_on_the_bound_result(self):
        bound = bind_launcher_identity(self._frame(agent_name="probe-coder"), TEAM)
        assert bound[2] == ["13"]

    def test_the_raw_agent_type_does_NOT_leak_into_the_step1_route(self):
        """Steps 1/2 must still win, and must NOT record the raw agent_type.

        The membership route records the RAW `agent_type` because that is the
        value validation passed. If that raw value reached the `agent_name`
        or `@`-bearing `agent_id` branches, the mis-bind would MOVE rather
        than close — and a membership-route test cannot see it, because that
        route is the one behaving correctly.

        Here `agent_name` says `probe-coder` while `agent_type` says
        `preparer` — a different LIVE member. Step 1 must win, so the bind
        must report `probe-coder` and `probe-coder`'s task, not `preparer`.
        """
        frame = self._frame(agent_name="probe-coder", agent_type="preparer")
        bound = bind_launcher_identity(frame, TEAM)
        assert bound is not None
        assert bound[0] == "probe-coder", (
            f"Step 1 lost to the agent_type route: bound {bound[0]!r}"
        )
        assert bound[2] == ["13"], (
            "bound the wrong member's tasks — the raw agent_type leaked past "
            "the membership route"
        )

    def test_the_raw_agent_type_does_NOT_leak_into_the_step2_route(self):
        """Same claim for the `@`-bearing `agent_id` branch."""
        frame = self._frame(
            agent_id=f"probe-coder@{TEAM}", agent_type="preparer"
        )
        assert "agent_name" not in frame
        bound = bind_launcher_identity(frame, TEAM)
        assert bound is not None
        assert bound[0] == "probe-coder"
        assert bound[2] == ["13"]

    def test_no_identity_writes_nothing(self):
        frame = self._frame(agent_id="0123456789abcdef", agent_type="pact-backend-coder")
        assert bind_launcher_identity(frame, TEAM) is None

    def test_owner_with_no_in_progress_task_writes_nothing(self):
        frame = self._frame(agent_name="preparer")
        assert bind_launcher_identity(frame, TEAM) is None

    # --- the exposure we accepted rather than eliminated -------------------

    def test_prefixed_type_naming_a_live_member_is_REFUSED(self):
        """`Agent(subagent_type="pact-preparer")` must not bind to `preparer`.

        A non-teammate spawn of a PACT agent type is ordinary usage. Matching
        the RAW value is what closes this: an in-process teammate's frame
        carries the bare name, a type carries the `pact-` prefix, so the
        prefix is itself the discriminator. Never strip before matching.
        """
        assert agent_type_names_a_member("pact-preparer", TEAM) is False
        frame = self._frame(agent_id="0123456789abcdef", agent_type="pact-preparer")
        assert bind_launcher_identity(frame, TEAM) is None

    def test_prefixed_collision_is_refused_BY_THE_RAW_MATCH_not_the_deny_set(self):
        """Isolates the raw-match rule from the deny set that shadows it.

        `pact-preparer` is ALSO an agents/*.md stem, so the deny set refuses
        it before the name comparison ever runs — which means the previous
        arm passes whether or not the match is raw. MEASURED: a mutant that
        strips the prefix before comparing SURVIVED that arm.

        `probe-coder` is a member whose `pact-`-prefixed spelling is NOT a
        shipped agent file, so the deny set does not fire and only the raw
        comparison can refuse it. This arm is the one that separates the two
        mechanisms, and it is the reason the rule is "match raw, never strip".
        """
        from shared.background_work import _known_agent_types

        assert "pact-probe-coder" not in _known_agent_types(), (
            "this arm requires a member whose prefixed spelling is NOT a "
            "shipped agent stem, or the deny set shadows what it measures"
        )
        assert agent_type_names_a_member("probe-coder", TEAM) is True
        assert agent_type_names_a_member("pact-probe-coder", TEAM) is False
        frame = self._frame(agent_id="0123456789abcdef", agent_type="pact-probe-coder")
        assert bind_launcher_identity(frame, TEAM) is None

    @pytest.mark.parametrize(
        "platform_type", ["general-purpose", "Explore", "Plan", "statusline-setup"]
    )
    def test_platform_types_are_refused(self, platform_type):
        assert agent_type_names_a_member(platform_type, TEAM) is False

    def test_deny_set_control_member_named_after_a_real_agent_type(self, tmp_path):
        """The residual, made visible rather than claimed away.

        A member NAMED after a shipped agent type is refused by the deny set.
        An UNKNOWN FUTURE platform type colliding with a member name is NOT
        covered, and fails toward mis-bind rather than silence.
        """
        import json

        cfg = tmp_path / "teams" / TEAM / "config.json"
        cfg.write_text(
            json.dumps(
                {"members": [{"name": "pact-architect", "agentType": "pact-architect"}]}
            )
        )
        assert agent_type_names_a_member("pact-architect", TEAM) is False


class TestDurableCommandFilter:
    @pytest.mark.parametrize("cmd", ["npm run dev", "yarn start", "make serve"])
    def test_durable_commands_are_not_recorded(self, cmd):
        assert is_durable_command(cmd) is True

    @pytest.mark.parametrize("cmd", ["echo hi", "pytest -q", "watchdog --help"])
    def test_ordinary_commands_are_recorded(self, cmd):
        assert is_durable_command(cmd) is False
