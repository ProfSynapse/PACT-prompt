"""
Location: pact-plugin/tests/test_unflagged_background_scan_integration.py
Summary: NON-MOCKED integration coverage for #1625 — tracker write and lead
         scan both drive the REAL get_team_name -> team-dir -> glob
         resolution. The sibling unit files may stub; THIS file must not.

================================ ANTI-MOCK INVARIANT ===========================
Do NOT monkeypatch get_task_list / iter_team_task_jsons / get_team_name /
get_session_id / read_task_json. Path.home + pact_context redirection only.

============================ NON-VACUITY (revert cardinality) =================
Source-revert of a broken team-dir resolver (arg-less get_task_list reading
~/.claude/tasks/{session_id}/) makes TestLeadScanEndToEnd +
TestTrackerWritesRegistry FAIL (resolver None / no team tasks -> no surface
and no bind). Restore the team-first resolver and the gate is green again.
================================================================================
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))

import background_work_tracker as tracker  # noqa: E402
import unflagged_background_scan as scan  # noqa: E402
from fixtures.role_frames import (  # noqa: E402
    captured_lead_userpromptsubmit_qualified,
    captured_teammate_sessionstart,
    synthesized_teammate_bash_background,
)
from shared import background_work as bw  # noqa: E402
from shared.session_journal import read_events  # noqa: E402

TEAM = "pact-testteam"
LEAD_SID = "aaaaaaaa-1111-2222-3333-444444444444"
PROJECT_DIR = "/test/project"
FIXED_NOW = datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc)


def _iso(minutes_ago: int, now: datetime = FIXED_NOW) -> str:
    return (now - timedelta(minutes=minutes_ago)).isoformat(timespec="seconds")


def _write_task(
    tasks_dir: Path,
    task_id: str = "7",
    owner: str = "architect",
    subject: str = "review X",
    status: str = "in_progress",
    wait="__null__",
) -> dict:
    tasks_dir.mkdir(parents=True, exist_ok=True)
    meta: dict = {}
    if wait == "__null__":
        meta["intentional_wait"] = None
    elif wait is not None:
        meta["intentional_wait"] = wait
    task = {
        "id": task_id,
        "owner": owner,
        "subject": subject,
        "status": status,
        "metadata": meta,
    }
    (tasks_dir / f"{task_id}.json").write_text(json.dumps(task), encoding="utf-8")
    return task


@pytest.fixture
def live_env(tmp_path, monkeypatch, pact_context):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    pact_context(team_name=TEAM, session_id=LEAD_SID, project_dir=PROJECT_DIR)
    return tmp_path


def _tasks_dir(home: Path) -> Path:
    return home / ".claude" / "tasks" / TEAM


class TestTrackerWritesRegistry:
    def test_non_vacuity_gate_teammate_bash_records_row(self, live_env):
        _write_task(_tasks_dir(live_env))
        frame = synthesized_teammate_bash_background()
        assert tracker.record_background_launch(frame) is True
        records = bw.load_records(TEAM)
        assert len(records) == 1
        assert records[0]["task_id"] == "7"
        assert records[0]["agent_name"] == "architect"

    def test_predicate_fires_after_tracker_with_null_wait(self, live_env):
        task = _write_task(_tasks_dir(live_env))
        assert tracker.record_background_launch(synthesized_teammate_bash_background())
        fire, klass, rec = bw.unflagged_fire(task, team_name=TEAM)
        assert fire is True
        assert klass == bw.WAIT_CLASS_NULL
        assert rec is not None


class TestLeadScanEndToEnd:
    def test_non_vacuity_gate_lead_surfaces_sendmessage(self, live_env):
        _write_task(_tasks_dir(live_env))
        bw.append_record(
            {
                "agent_name": "architect",
                "session_id": "sid-architect",
                "task_id": "7",
                "registered_at": _iso(20),
                "command": "pytest -q",
                "idled_at": _iso(15),
            },
            TEAM,
        )
        out = scan.run_surface(
            captured_lead_userpromptsubmit_qualified(), now=FIXED_NOW
        )
        assert out is not None, (
            "run_surface MUST surface an unflagged-background task that lives "
            "in the REAL team dir + registry — None here is the inert-scan bug"
        )
        assert "SendMessage" in out
        assert "architect" in out
        events = read_events("unflagged_background_wait")
        assert len(events) == 1
        assert events[0]["type"] == "unflagged_background_wait"
        assert events[0]["wait_class"] == "null"
        assert events[0].get("reason") != "awaiting_lead_completion"

    def test_teammate_frame_no_surface(self, live_env):
        _write_task(_tasks_dir(live_env))
        bw.append_record(
            {
                "agent_name": "architect",
                "session_id": "sid-architect",
                "task_id": "7",
                "registered_at": _iso(20),
                "idled_at": _iso(15),
            },
            TEAM,
        )
        assert scan.run_surface(captured_teammate_sessionstart(), now=FIXED_NOW) is None

    def test_valid_wait_clears_surface(self, live_env):
        _write_task(
            _tasks_dir(live_env),
            wait={
                "reason": "awaiting_lead_takeover",
                "expected_resolver": "lead",
                "since": _iso(5),
            },
        )
        bw.append_record(
            {
                "agent_name": "architect",
                "session_id": "sid-architect",
                "task_id": "7",
                "registered_at": _iso(20),
                "idled_at": _iso(15),
            },
            TEAM,
        )
        assert scan.run_surface(
            captured_lead_userpromptsubmit_qualified(), now=FIXED_NOW
        ) is None
        assert read_events("unflagged_background_wait") == []
