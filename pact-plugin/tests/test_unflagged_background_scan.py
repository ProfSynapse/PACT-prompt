"""
Location: pact-plugin/tests/test_unflagged_background_scan.py
Summary: Behavioral coverage for the #1625 lead unflagged-background surfacer.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))

import unflagged_background_scan as scan  # noqa: E402
from fixtures.role_frames import (  # noqa: E402
    captured_lead_userpromptsubmit_qualified,
    captured_teammate_sessionstart,
)
from shared.background_work import WAIT_CLASS_NULL  # noqa: E402

FIXED_NOW = datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc)


def _iso(minutes_ago: int, now: datetime = FIXED_NOW) -> str:
    return (now - timedelta(minutes=minutes_ago)).isoformat(timespec="seconds")


def _valid_wait():
    return {
        "reason": "awaiting_lead_takeover",
        "expected_resolver": "lead",
        "since": _iso(5),
    }


def _task(task_id="7", owner="architect", subject="review X",
          status="in_progress", wait="__null__"):
    meta = {}
    if wait == "__null__":
        meta["intentional_wait"] = None
    elif wait is not None:
        meta["intentional_wait"] = wait
    return {
        "id": task_id,
        "owner": owner,
        "subject": subject,
        "status": status,
        "metadata": meta,
    }


def _record(task_id="7", idled_minutes=15, **over):
    rec = {
        "agent_name": "architect",
        "session_id": "sid-architect",
        "task_id": task_id,
        "registered_at": _iso(20),
        "command": "pytest -q",
        "idled_at": _iso(idled_minutes),
    }
    rec.update(over)
    return rec


@pytest.fixture
def journal(monkeypatch):
    state = {"seed": [], "emitted": []}
    monkeypatch.setattr(scan, "read_events", lambda et: list(state["seed"]) if et == "unflagged_background_wait" else [])
    monkeypatch.setattr(scan, "append_event", lambda e: state["emitted"].append(e) or True)
    monkeypatch.setattr(scan, "get_journal_path", lambda: "/tmp/fake-journal.jsonl")
    return state


class TestFindUnflaggedStale:
    def test_stale_idled_null_wait_qualifies(self):
        found = scan.find_unflagged_stale(
            [_task()], records=[_record()], now=FIXED_NOW
        )
        assert len(found) == 1
        assert found[0]["wait_class"] == WAIT_CLASS_NULL

    def test_fresh_idled_at_does_not_qualify(self):
        found = scan.find_unflagged_stale(
            [_task()], records=[_record(idled_minutes=5)], now=FIXED_NOW
        )
        assert found == []

    def test_missing_idled_at_does_not_qualify(self):
        rec = _record()
        rec.pop("idled_at")
        found = scan.find_unflagged_stale(
            [_task()], records=[rec], now=FIXED_NOW
        )
        assert found == []

    def test_valid_wait_does_not_qualify(self):
        found = scan.find_unflagged_stale(
            [_task(wait=_valid_wait())], records=[_record()], now=FIXED_NOW
        )
        assert found == []


class TestBuildSurface:
    def test_names_sendmessage_not_completion_wake(self):
        stale = scan.find_unflagged_stale(
            [_task()], records=[_record()], now=FIXED_NOW
        )
        text = scan.build_surface(stale, now=FIXED_NOW)
        assert text is not None
        assert "SendMessage" in text
        assert "awaiting_lead_completion" not in text
        assert "forgotten" not in text.lower()
        assert "architect" in text
        assert "#7" in text


class TestRunSurface:
    def test_lead_surfaces_and_emits_honest_event(self, journal, monkeypatch):
        monkeypatch.setattr(scan, "get_task_list", lambda: [_task()])
        monkeypatch.setattr(scan, "load_records", lambda now=None: [_record()])
        out = scan.run_surface(captured_lead_userpromptsubmit_qualified(), now=FIXED_NOW)
        assert out is not None
        assert "SendMessage" in out
        assert len(journal["emitted"]) == 1
        ev = journal["emitted"][0]
        assert ev["type"] == "unflagged_background_wait"
        assert ev["wait_class"] == "null"
        assert ev.get("reason") != "awaiting_lead_completion"
        assert "awaiting_lead_completion" not in json_blob(ev)

    def test_valid_wait_suppresses(self, journal, monkeypatch):
        monkeypatch.setattr(scan, "get_task_list", lambda: [_task(wait=_valid_wait())])
        monkeypatch.setattr(scan, "load_records", lambda now=None: [_record()])
        assert scan.run_surface(captured_lead_userpromptsubmit_qualified(), now=FIXED_NOW) is None
        assert journal["emitted"] == []

    def test_teammate_frame_noops(self, journal, monkeypatch):
        monkeypatch.setattr(scan, "get_task_list", lambda: [_task()])
        monkeypatch.setattr(scan, "load_records", lambda now=None: [_record()])
        assert scan.run_surface(captured_teammate_sessionstart(), now=FIXED_NOW) is None
        assert journal["emitted"] == []

    def test_borrowed_awaiting_lead_completion_is_not_this_event(self, journal, monkeypatch):
        other = _task(
            task_id="99",
            owner="coder",
            wait={
                "reason": "awaiting_lead_completion",
                "expected_resolver": "lead",
                "since": _iso(60),
            },
        )
        monkeypatch.setattr(scan, "get_task_list", lambda: [_task(), other])
        monkeypatch.setattr(scan, "load_records", lambda now=None: [_record()])
        out = scan.run_surface(captured_lead_userpromptsubmit_qualified(), now=FIXED_NOW)
        assert out is not None
        assert len(journal["emitted"]) == 1
        assert journal["emitted"][0]["task_id"] == "7"
        assert journal["emitted"][0]["type"] == "unflagged_background_wait"

    def test_empty_journal_path_still_surfaces(self, monkeypatch):
        monkeypatch.setattr(scan, "get_task_list", lambda: [_task()])
        monkeypatch.setattr(scan, "load_records", lambda now=None: [_record()])
        monkeypatch.setattr(scan, "get_journal_path", lambda: "")
        emitted = []
        monkeypatch.setattr(scan, "append_event", lambda e: emitted.append(e))
        out = scan.run_surface(captured_lead_userpromptsubmit_qualified(), now=FIXED_NOW)
        assert out is not None
        assert emitted == []


def json_blob(ev) -> str:
    import json
    return json.dumps(ev)
