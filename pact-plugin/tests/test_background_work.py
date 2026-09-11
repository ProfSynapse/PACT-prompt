"""
Location: pact-plugin/tests/test_background_work.py
Summary: Unit coverage for the #1625 unflagged-background registry and
         fire predicate (shared.background_work). No hook I/O.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))

from shared import background_work as bw  # noqa: E402

FIXED_NOW = datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc)
TEAM = "pact-testteam"


def _iso(minutes_ago: int, now: datetime = FIXED_NOW) -> str:
    return (now - timedelta(minutes=minutes_ago)).isoformat(timespec="seconds")


def _task(
    task_id="7",
    status="in_progress",
    wait="__null__",
    owner="architect",
):
    meta = {}
    if wait == "__null__":
        meta["intentional_wait"] = None
    elif wait == "__missing__":
        pass
    elif wait is not None:
        meta["intentional_wait"] = wait
    return {"id": task_id, "status": status, "owner": owner, "metadata": meta}


def _valid_wait(minutes_ago: int = 5) -> dict:
    return {
        "reason": "awaiting_lead_takeover",
        "expected_resolver": "lead",
        "since": _iso(minutes_ago),
    }


def _record(**over) -> dict:
    rec = {
        "agent_name": "architect",
        "session_id": "sid-architect",
        "task_id": "7",
        "registered_at": _iso(15),
        "command": "pytest -q",
    }
    rec.update(over)
    return rec


@pytest.fixture
def team_home(tmp_path, monkeypatch, pact_context):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    pact_context(team_name=TEAM, session_id="sid-lead")
    return tmp_path


class TestClassifyWait:
    def test_null(self):
        assert bw.classify_wait(_task(wait="__null__")) == bw.WAIT_CLASS_NULL

    def test_missing(self):
        assert bw.classify_wait(_task(wait="__missing__")) == bw.WAIT_CLASS_MISSING

    def test_valid(self):
        assert bw.classify_wait(_task(wait=_valid_wait())) is None

    def test_malformed_naive_since(self):
        wait = _valid_wait()
        wait["since"] = "2026-09-11T12:00:00"
        assert bw.classify_wait(_task(wait=wait)) == bw.WAIT_CLASS_MALFORMED

    def test_non_dict(self):
        assert bw.classify_wait(None) == bw.WAIT_CLASS_MISSING


class TestDurableCommand:
    def test_pytest_not_durable(self):
        assert bw.is_durable_command("pytest -q") is False

    def test_npm_run_dev(self):
        assert bw.is_durable_command("npm run dev") is True

    def test_watchdog_is_not_watch(self):
        assert bw.is_durable_command("python -m watchdog") is False


class TestUnflaggedFire:
    def test_in_progress_record_null_wait_fires_null(self):
        fire, klass, rec = bw.unflagged_fire(
            _task(), records=[_record()], now=FIXED_NOW
        )
        assert fire is True
        assert klass == bw.WAIT_CLASS_NULL
        assert rec["task_id"] == "7"

    def test_valid_wait_does_not_fire(self):
        fire, klass, rec = bw.unflagged_fire(
            _task(wait=_valid_wait()), records=[_record()], now=FIXED_NOW
        )
        assert fire is False
        assert klass is None
        assert rec is not None

    def test_no_record_null_wait_does_not_fire(self):
        fire, klass, rec = bw.unflagged_fire(
            _task(), records=[], now=FIXED_NOW
        )
        assert fire is False
        assert klass is None
        assert rec is None

    def test_completed_task_with_record_does_not_fire(self):
        fire, klass, _rec = bw.unflagged_fire(
            _task(status="completed"), records=[_record()], now=FIXED_NOW
        )
        assert fire is False
        assert klass is None

    def test_malformed_wait_fires_malformed(self):
        wait = {"reason": "x", "expected_resolver": "lead", "since": "yesterday"}
        fire, klass, rec = bw.unflagged_fire(
            _task(wait=wait), records=[_record()], now=FIXED_NOW
        )
        assert fire is True
        assert klass == bw.WAIT_CLASS_MALFORMED
        assert rec is not None


class TestRegistryIO:
    def test_corrupt_file_returns_empty(self, team_home):
        path = bw.registry_path(TEAM)
        assert path is not None
        path.parent.mkdir(parents=True)
        path.write_text("{not-json", encoding="utf-8")
        assert bw.load_records(TEAM, now=FIXED_NOW) == []

    def test_missing_team_name_returns_empty(self):
        assert bw.load_records("") == []
        assert bw.registry_path("") is None

    def test_expired_record_excluded(self, team_home):
        old = _record(registered_at=_iso(25 * 60, now=FIXED_NOW))
        assert bw.save_records([old], TEAM) is True
        assert bw.load_records(TEAM, now=FIXED_NOW) == []

    def test_round_trip_outstanding(self, team_home):
        rec = _record()
        assert bw.append_record(rec, TEAM) is True
        loaded = bw.load_records(TEAM, now=FIXED_NOW)
        assert len(loaded) == 1
        assert loaded[0]["task_id"] == "7"
        assert loaded[0]["agent_name"] == "architect"

    def test_stamp_idled_at_once(self, team_home):
        bw.append_record(_record(), TEAM)
        assert bw.stamp_idled_at("7", now=FIXED_NOW, team_name=TEAM) is True
        first = bw.load_records(TEAM, now=FIXED_NOW)[0]["idled_at"]
        later = FIXED_NOW + timedelta(minutes=3)
        assert bw.stamp_idled_at("7", now=later, team_name=TEAM) is False
        assert bw.load_records(TEAM, now=FIXED_NOW)[0]["idled_at"] == first

    def test_idled_at_stale_window(self):
        fresh = _record(idled_at=_iso(5))
        stale = _record(idled_at=_iso(11))
        missing = _record()
        assert bw.idled_at_stale(fresh, now=FIXED_NOW) is False
        assert bw.idled_at_stale(stale, now=FIXED_NOW) is True
        assert bw.idled_at_stale(missing, now=FIXED_NOW) is False
