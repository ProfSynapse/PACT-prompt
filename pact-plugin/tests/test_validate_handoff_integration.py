"""
Location: pact-plugin/tests/test_validate_handoff_integration.py
Summary: NON-MOCKED seam coverage for the degrade-path journal telemetry —
         every emission test in the sibling unit file (test_validate_handoff.py)
         monkeypatches append_event, so the unit suite proves the event DICT is
         well-formed but never that an event LANDS in a real journal. THIS file
         drives the REAL pact_context.init(stdin session_id) -> session-dir
         resolution -> real append_event write end-to-end over a tmp-redirected
         config root, then reads the real session-journal.jsonl back.

Used by: the pact-plugin test suite (seam-coverage gate for the
         handoff_refusal_degraded telemetry; classifier COVERED_L2 entry).

================================ ANTI-MOCK INVARIANT ===========================
The tests here MUST NOT monkeypatch append_event / make_event /
pact_context.init / session_journal internals. The init -> resolve -> append
composition IS the seam under test — stubbing any leg of it reproduces the gap
this file exists to close (the telemetry is fail-open, so a broken seam loses
events SILENTLY: nothing reddens and the escape hatch goes unobserved). The
ONLY test doubles permitted are filesystem redirection (Path.home +
CLAUDE_PROJECT_DIR / CLAUDE_CONFIG_DIR env) and the pre-written
pact-session-context.json, which is filesystem SETUP mirroring the production
topology (session_init writes that file at SessionStart; SubagentStop reads
it), not a stub of any function.

============================ NON-VACUITY (source ablation) ====================
Measured 2026-09-11 on the 26fd5732 tree, mutating an ISOLATED /tmp copy of
hooks/+tests/ (never the shared worktree), __pycache__ cleared:

  Arm 1 — the degrade path's init+append_event telemetry block REMOVED
  (identical to reverting the telemetry addition; the ablated state IS the
  pre-telemetry behavior): {3 failed} across this file and the sibling unit
  file — this file's test (on journal.exists: 0 events land) plus the
  sibling's two capture-assertion tests (test_degrade_emits_handoff_refusal_
  degraded_event, test_stop_hook_active_true_degrades_lossless_refusal),
  whose monkeypatched append_event captures nothing when the call is gone.

  Arm 2 — DISCRIMINATING: pact_context.init neutralized (resolution leg
  broken) while the append_event call stays intact: {1 failed} — THIS file's
  test alone; all 64 sibling tests green. A broken resolution leg is the
  failure shape the mocked-seam suite is blind to BY CONSTRUCTION (the stub
  replaces the seam), and the fail-open design makes it silent in production.
  This arm is the proof the seam test adds information the unit file cannot.
================================================================================
"""
import io
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from shared.session_journal import read_events  # noqa: E402

SID = "cccccccc-1234-5678-9abc-def012345678"
PROJECT_DIR = "/test/project"

# Keyword-poor closing message, 100+ chars: engages the implicit-element path
# with all three element groups absent -> the missing_handoff refusal class.
POOR_CLOSING = "x" * 100 + " " + (
    "Hello world, here is some random text without any handoff info."
)


class TestDegradeTelemetryRealSeam:
    """The degrade path (stop_hook_active=true) must append exactly one
    handoff_refusal_degraded event to the REAL session journal — the event is
    the only observability the escape hatch has, and its failure mode is
    silent (append_event returns False; at most a stderr warning no consumer
    surfaces). Path.home + env redirection only; no resolver stubbed."""

    def test_degrade_event_lands_in_real_journal(self, tmp_path, monkeypatch, capsys):
        # Filesystem redirection: the config root resolves under the tmp home
        # (CLAUDE_CONFIG_DIR deleted so a leaked ambient value cannot win),
        # and init() picks project_dir up from CLAUDE_PROJECT_DIR.
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", PROJECT_DIR)

        # Production topology: session_init writes pact-session-context.json at
        # SessionStart; this hook's SubagentStop init() resolves the same path
        # from the stdin session_id and the getters read the file. Pre-write it
        # at the path the REAL init() will compute (config/pact-sessions/
        # {slug}/{session_id}/), so the read side is exercised, not bypassed.
        session_dir = (
            tmp_path / ".claude" / "pact-sessions" / "project" / SID
        )
        session_dir.mkdir(parents=True)
        (session_dir / "pact-session-context.json").write_text(
            json.dumps({
                "team_name": "pact-testteam",
                "session_id": SID,
                "project_dir": PROJECT_DIR,
                "plugin_root": "",
                "started_at": "2026-09-11T00:00:00Z",
            }),
            encoding="utf-8",
        )

        import validate_handoff

        payload = json.dumps({
            "agent_type": "pact-backend-coder",
            "last_assistant_message": POOR_CLOSING,
            "stop_hook_active": True,
            "session_id": SID,
        })
        with patch("sys.stdin", io.StringIO(payload)):
            with pytest.raises(SystemExit) as exc_info:
                validate_handoff.main()

        # The degrade contract still holds end-to-end: exit 0, no block key,
        # and the user-facing systemMessage lands.
        assert exc_info.value.code == 0
        out = json.loads(capsys.readouterr().out.strip())
        assert "decision" not in out
        assert "refusal degraded by stop_hook_active loop guard" in out["systemMessage"]

        # The journal file the event landed in MUST live under the redirected
        # home — proves the seam resolved to the tmp root (a leak to the real
        # config dir would write outside tmp_path and fail this).
        journal = session_dir / "session-journal.jsonl"
        assert journal.exists(), (
            "handoff_refusal_degraded must land in the REAL journal under the "
            "redirected config root — absent means the init -> resolve -> "
            "append seam is broken (and the fail-open design would hide it)"
        )

        # Read back through the REAL reader (implicit path resolution), not by
        # parsing the file ourselves.
        events = read_events("handoff_refusal_degraded")
        assert len(events) == 1, (
            "exactly one degrade event per degraded stop; got %d" % len(events)
        )
        ev = events[0]
        assert ev["type"] == "handoff_refusal_degraded"
        assert ev["v"] == 1
        assert ev["agent_type"] == "pact-backend-coder"
        assert "Handoff Refusal" in ev["detail"]
        assert ev["classes"] == ["missing_handoff"]
        assert "ts" in ev
