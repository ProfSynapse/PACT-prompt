"""
Location: pact-plugin/tests/test_background_work_tracker.py
Summary: Unit coverage for the #1625 PostToolUse Bash tracker.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))

import background_work_tracker as tracker  # noqa: E402
from fixtures.role_frames import (  # noqa: E402
    lead_frame_qualified,
    synthesized_teammate_bash_background,
)
from shared import background_work as bw  # noqa: E402

TEAM = "pact-testteam"


def _task(task_id="7", owner="architect", status="in_progress"):
    return {"id": task_id, "owner": owner, "status": status, "metadata": {}}


class TestIsHarnessBackgroundBash:
    def test_true_on_run_in_background(self):
        assert tracker.is_harness_background_bash(
            synthesized_teammate_bash_background()
        )

    def test_false_on_foreground(self):
        frame = synthesized_teammate_bash_background(run_in_background=False)
        assert tracker.is_harness_background_bash(frame) is False

    def test_false_on_shell_ampersand_without_flag(self):
        frame = synthesized_teammate_bash_background(
            command="pytest -q &", run_in_background=False
        )
        assert tracker.is_harness_background_bash(frame) is False

    def test_false_on_missing_tool_input(self):
        assert tracker.is_harness_background_bash({"tool_name": "Bash"}) is False


class TestBindLauncherIdentity:
    def test_unique_in_progress_binds(self):
        frame = synthesized_teammate_bash_background()
        with patch(
            "background_work_tracker.iter_team_task_jsons",
            return_value=[_task()],
        ):
            bound = tracker.bind_launcher_identity(frame, TEAM)
        assert bound == ("architect", "sid-architect", "7")

    def test_type_strip_only_refuses(self):
        frame = synthesized_teammate_bash_background()
        frame.pop("agent_name")
        with patch(
            "background_work_tracker.iter_team_task_jsons",
            return_value=[_task(owner="architect")],
        ), patch("background_work_tracker.registry_resolve", return_value=None):
            assert tracker.bind_launcher_identity(frame, TEAM) is None

    def test_same_type_siblings_no_write(self):
        frame = synthesized_teammate_bash_background()
        tasks = [
            _task(task_id="7", owner="architect"),
            _task(task_id="8", owner="architect"),
        ]
        with patch("background_work_tracker.iter_team_task_jsons", return_value=tasks):
            assert tracker.bind_launcher_identity(frame, TEAM) is None


class TestRecordBackgroundLaunch:
    def test_teammate_background_writes(self, tmp_path, monkeypatch, pact_context):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        pact_context(team_name=TEAM, session_id="sid-lead")
        frame = synthesized_teammate_bash_background()
        with patch(
            "background_work_tracker.iter_team_task_jsons",
            return_value=[_task()],
        ):
            assert tracker.record_background_launch(frame) is True
        records = bw.load_records(TEAM)
        assert len(records) == 1
        assert records[0]["task_id"] == "7"
        assert records[0]["agent_name"] == "architect"
        assert "pytest" in records[0]["command"]

    def test_lead_background_no_write(self, tmp_path, monkeypatch, pact_context):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        pact_context(team_name=TEAM, session_id="sid-lead")
        frame = lead_frame_qualified(
            hook_event_name="PostToolUse",
            tool_name="Bash",
            tool_input={"command": "pytest -q", "run_in_background": True},
            session_id="sid-lead",
        )
        with patch(
            "background_work_tracker.iter_team_task_jsons",
            return_value=[_task(owner="team-lead")],
        ):
            assert tracker.record_background_launch(frame) is False
        assert bw.load_records(TEAM) == []

    def test_durable_dev_server_not_recorded(self, tmp_path, monkeypatch, pact_context):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        pact_context(team_name=TEAM, session_id="sid-lead")
        frame = synthesized_teammate_bash_background(command="npm run dev")
        with patch(
            "background_work_tracker.iter_team_task_jsons",
            return_value=[_task()],
        ):
            assert tracker.record_background_launch(frame) is False
        assert bw.load_records(TEAM) == []

    def test_main_missing_tool_input_exits_0(self, capsys):
        with patch("sys.stdin", __import__("io").StringIO(json.dumps({
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "agent_type": "pact-architect",
        }))):
            with pytest.raises(SystemExit) as exc:
                tracker.main()
        assert exc.value.code == 0
        assert json.loads(capsys.readouterr().out)["suppressOutput"] is True
